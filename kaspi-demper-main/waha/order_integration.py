# order_integration.py
"""
Интеграция WAHA с системой заказов Kaspi
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from .message_sender import WhatsAppMessageSender
from .models import OrderData, WAHAWebhookEvent, WAHAWebhookMessage, WAHAWebhookMessageStatus
from .database import WAHA_Database

logger = logging.getLogger(__name__)


class OrderIntegration:
    """Интеграция заказов с WAHA"""
    
    def __init__(self, message_sender: WhatsAppMessageSender, db: WAHA_Database):
        self.message_sender = message_sender
        self.db = db
    
    def extract_order_data_from_kaspi(self, kaspi_order: Dict[str, Any], shop_name: str = "Магазин") -> OrderData:
        """
        Извлечение данных заказа из структуры Kaspi
        
        Args:
            kaspi_order: Данные заказа от Kaspi API
            shop_name: Название магазина
            
        Returns:
            Структурированные данные заказа
        """
        try:
            # Извлекаем основную информацию о заказе
            order_id = kaspi_order.get('orderId', kaspi_order.get('id', 'N/A'))
            
            # Информация о покупателе
            customer_name = kaspi_order.get('customerName', kaspi_order.get('customer_name', 'Клиент'))
            customer_phone = kaspi_order.get('customerPhone', kaspi_order.get('customer_phone', ''))
            
            # Информация о товаре
            product_name = kaspi_order.get('productName', kaspi_order.get('product_name', 'Товар'))
            quantity = kaspi_order.get('quantity', kaspi_order.get('item_qty', 1))
            
            # Финансовая информация
            total_amount = kaspi_order.get('totalPrice', kaspi_order.get('total_amount', 0))
            
            # Тип доставки
            delivery_type = 'доставка' if kaspi_order.get('deliveryType') == 'DELIVERY' else 'самовывоз'
            
            # Дата заказа
            create_date = kaspi_order.get('createDate', kaspi_order.get('created_at'))
            if create_date:
                if isinstance(create_date, (int, float)):
                    # Timestamp в миллисекундах
                    order_date = datetime.fromtimestamp(create_date / 1000).strftime('%d.%m.%Y')
                else:
                    # Строка даты
                    order_date = str(create_date)[:10]  # Берем только дату
            else:
                order_date = datetime.now().strftime('%d.%m.%Y')
            
            return OrderData(
                customer_name=customer_name,
                customer_phone=customer_phone,
                order_id=str(order_id),
                product_name=product_name,
                quantity=int(quantity),
                total_amount=float(total_amount),
                delivery_type=delivery_type,
                order_date=order_date,
                shop_name=shop_name
            )
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных заказа: {e}")
            # Возвращаем базовые данные в случае ошибки
            return OrderData(
                customer_name='Клиент',
                customer_phone='',
                order_id='N/A',
                product_name='Товар',
                quantity=1,
                total_amount=0.0,
                delivery_type='самовывоз',
                order_date=datetime.now().strftime('%d.%m.%Y'),
                shop_name=shop_name
            )
    
    async def process_new_orders(self, store_id: UUID, orders_data: List[Dict[str, Any]], 
                                shop_name: str = "Магазин") -> List[Dict[str, Any]]:
        """
        Обработка новых заказов и отправка WhatsApp уведомлений
        
        Args:
            store_id: ID магазина
            orders_data: Список заказов от Kaspi API
            shop_name: Название магазина
            
        Returns:
            Список результатов обработки заказов
        """
        results = []
        
        try:
            # Проверяем, включены ли WAHA уведомления для магазина
            settings = await self.db.get_settings(store_id)
            if not settings or not settings.is_enabled:
                logger.info(f"WAHA уведомления отключены для магазина {store_id}")
                return results
            
            # Фильтруем новые заказы
            new_orders = self._filter_new_orders(orders_data)
            
            if not new_orders:
                logger.info(f"Новых заказов не найдено для магазина {store_id}")
                return results
            
            logger.info(f"Найдено {len(new_orders)} новых заказов для магазина {store_id}")
            
            # Обрабатываем каждый новый заказ
            for order_data in new_orders:
                try:
                    # Извлекаем структурированные данные заказа
                    order_info = self.extract_order_data_from_kaspi(order_data, shop_name)
                    
                    # Проверяем, есть ли номер телефона
                    if not order_info.customer_phone:
                        logger.warning(f"Номер телефона не найден для заказа {order_info.order_id}")
                        results.append({
                            'order_id': order_info.order_id,
                            'success': False,
                            'error': 'Номер телефона не найден'
                        })
                        continue
                    
                    # Отправляем WhatsApp уведомление
                    send_result = await self.message_sender.send_order_notification(store_id, order_info)
                    
                    results.append({
                        'order_id': order_info.order_id,
                        'success': send_result.success,
                        'message_id': send_result.message_id,
                        'error': send_result.error
                    })
                    
                    logger.info(f"Обработан заказ {order_info.order_id} для магазина {store_id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки заказа {order_data.get('orderId', 'N/A')}: {e}")
                    results.append({
                        'order_id': order_data.get('orderId', 'N/A'),
                        'success': False,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка обработки заказов для магазина {store_id}: {e}")
            return results
    
    def _filter_new_orders(self, orders_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрация новых заказов
        
        Args:
            orders_data: Список всех заказов
            
        Returns:
            Список новых заказов
        """
        new_orders = []
        
        for order in orders_data:
            # Проверяем статус заказа
            status = order.get('status', '').upper()
            
            # Считаем новыми заказы со статусами NEW, CONFIRMED, PROCESSING
            if status in ['NEW', 'CONFIRMED', 'PROCESSING']:
                new_orders.append(order)
        
        return new_orders
    
    async def handle_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка webhook событий от WAHA
        
        Args:
            webhook_data: Данные webhook события
            
        Returns:
            Результат обработки
        """
        try:
            event_type = webhook_data.get('event')
            session = webhook_data.get('session')
            payload = webhook_data.get('payload', {})
            
            logger.info(f"Получено webhook событие: {event_type} для сессии {session}")
            
            if event_type == 'message':
                # Обработка входящего сообщения
                return await self._handle_incoming_message(payload)
            
            elif event_type == 'messageStatus':
                # Обновление статуса сообщения
                return await self._handle_message_status(payload)
            
            elif event_type == 'sessionStatus':
                # Обновление статуса сессии
                return await self._handle_session_status(session, payload)
            
            else:
                logger.warning(f"Неизвестный тип webhook события: {event_type}")
                return {'success': False, 'error': f'Неизвестный тип события: {event_type}'}
                
        except Exception as e:
            logger.error(f"Ошибка обработки webhook события: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _handle_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка входящего сообщения"""
        try:
            # Логируем входящее сообщение
            logger.info(f"Получено входящее сообщение: {message_data.get('body', '')[:50]}...")
            
            # Здесь можно добавить логику обработки входящих сообщений
            # Например, автоматические ответы, обработка команд и т.д.
            
            return {'success': True, 'message': 'Входящее сообщение обработано'}
            
        except Exception as e:
            logger.error(f"Ошибка обработки входящего сообщения: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _handle_message_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка изменения статуса сообщения"""
        try:
            message_id = status_data.get('id')
            status = status_data.get('status')
            
            if not message_id or not status:
                return {'success': False, 'error': 'Отсутствуют обязательные поля'}
            
            # Обновляем статус сообщения в базе данных
            # Здесь нужно найти запись в логе по message_id и обновить статус
            
            logger.info(f"Обновлен статус сообщения {message_id}: {status}")
            
            return {'success': True, 'message': f'Статус сообщения {message_id} обновлен на {status}'}
            
        except Exception as e:
            logger.error(f"Ошибка обработки статуса сообщения: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _handle_session_status(self, session: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка изменения статуса сессии"""
        try:
            status = status_data.get('status')
            
            if not status:
                return {'success': False, 'error': 'Отсутствует статус сессии'}
            
            # Обновляем статус сессии в базе данных
            # Здесь нужно найти магазин по имени сессии и обновить статус
            
            logger.info(f"Обновлен статус сессии {session}: {status}")
            
            return {'success': True, 'message': f'Статус сессии {session} обновлен на {status}'}
            
        except Exception as e:
            logger.error(f"Ошибка обработки статуса сессии: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_order_statistics(self, store_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Получение статистики по заказам и уведомлениям
        
        Args:
            store_id: ID магазина
            days: Количество дней для анализа
            
        Returns:
            Статистика заказов и уведомлений
        """
        try:
            # Получаем статистику сообщений
            message_stats = await self.message_sender.get_message_statistics(store_id, days)
            
            # Здесь можно добавить дополнительную статистику по заказам
            # Например, количество заказов, конверсия уведомлений и т.д.
            
            return {
                'success': True,
                'message_statistics': message_stats,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики заказов для магазина {store_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
