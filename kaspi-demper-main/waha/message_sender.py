# message_sender.py
"""
Отправка WhatsApp сообщений через WAHA
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from .waha_client import WAHAClient, WAHASessionManager
from .template_manager import TemplateManager
from .database import WAHA_Database
from .models import WhatsAppMessageLog, OrderData, WhatsAppSendResponse

logger = logging.getLogger(__name__)


class WhatsAppMessageSender:
    """Отправитель WhatsApp сообщений"""
    
    def __init__(self, waha_client: WAHAClient, template_manager: TemplateManager, db: WAHA_Database):
        self.waha_client = waha_client
        self.template_manager = template_manager
        self.db = db
        self.session_manager = WAHASessionManager(waha_client)
    
    async def send_order_notification(self, store_id: UUID, order_data: OrderData) -> WhatsAppSendResponse:
        """
        Отправка уведомления о заказе
        
        Args:
            store_id: ID магазина
            order_data: Данные заказа
            
        Returns:
            Результат отправки сообщения
        """
        try:
            # Проверяем, включены ли WAHA уведомления для магазина
            settings = await self.db.get_settings(store_id)
            if not settings or not settings.is_enabled:
                return WhatsAppSendResponse(
                    success=False,
                    error="WAHA уведомления отключены для этого магазина"
                )
            
            # Получаем активный шаблон
            template = await self.template_manager.get_active_template(store_id)
            if not template:
                return WhatsAppSendResponse(
                    success=False,
                    error="Активный шаблон не найден"
                )
            
            # Проверяем статус WAHA сессии
            session_status = await self.session_manager.get_session_status(str(store_id))
            if session_status.get('status') != 'CONNECTED':
                return WhatsAppSendResponse(
                    success=False,
                    error=f"WAHA сессия не подключена. Статус: {session_status.get('status')}"
                )
            
            # Формируем сообщение
            message_text = self.template_manager.process_template(
                template.template_text,
                order_data.dict()
            )
            
            # Отправляем сообщение
            result = await self.session_manager.send_message(
                str(store_id),
                order_data.customer_phone,
                message_text
            )
            
            # Логируем отправку
            message_log = WhatsAppMessageLog(
                store_id=store_id,
                order_id=order_data.order_id,
                customer_phone=order_data.customer_phone,
                message_text=message_text,
                template_id=template.id,
                status='sent',
                waha_response=result,
                sent_at=datetime.now()
            )
            
            log_id = await self.db.log_message(message_log)
            
            logger.info(f"Отправлено WhatsApp уведомление для заказа {order_data.order_id} магазина {store_id}")
            
            return WhatsAppSendResponse(
                success=True,
                message_id=result.get('id'),
                waha_response=result
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки WhatsApp уведомления для магазина {store_id}: {e}")
            
            # Логируем ошибку
            try:
                error_log = WhatsAppMessageLog(
                    store_id=store_id,
                    order_id=order_data.order_id if order_data else None,
                    customer_phone=order_data.customer_phone if order_data else "",
                    message_text="",
                    status='failed',
                    error_message=str(e),
                    sent_at=datetime.now()
                )
                await self.db.log_message(error_log)
            except Exception as log_error:
                logger.error(f"Ошибка логирования ошибки отправки: {log_error}")
            
            return WhatsAppSendResponse(
                success=False,
                error=str(e)
            )
    
    async def send_test_message(self, store_id: UUID, phone_number: str, template_text: str, 
                               sample_data: Dict[str, Any]) -> WhatsAppSendResponse:
        """
        Отправка тестового сообщения
        
        Args:
            store_id: ID магазина
            phone_number: Номер телефона для теста
            template_text: Текст шаблона
            sample_data: Тестовые данные
            
        Returns:
            Результат отправки сообщения
        """
        try:
            # Проверяем статус WAHA сессии
            session_status = await self.session_manager.get_session_status(str(store_id))
            if session_status.get('status') != 'CONNECTED':
                return WhatsAppSendResponse(
                    success=False,
                    error=f"WAHA сессия не подключена. Статус: {session_status.get('status')}"
                )
            
            # Формируем сообщение
            message_text = self.template_manager.process_template(template_text, sample_data)
            
            # Отправляем сообщение
            result = await self.session_manager.send_message(
                str(store_id),
                phone_number,
                message_text
            )
            
            # Логируем отправку
            message_log = WhatsAppMessageLog(
                store_id=store_id,
                customer_phone=phone_number,
                message_text=message_text,
                status='sent',
                waha_response=result,
                sent_at=datetime.now()
            )
            
            await self.db.log_message(message_log)
            
            logger.info(f"Отправлено тестовое WhatsApp сообщение для магазина {store_id}")
            
            return WhatsAppSendResponse(
                success=True,
                message_id=result.get('id'),
                waha_response=result
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки тестового WhatsApp сообщения для магазина {store_id}: {e}")
            return WhatsAppSendResponse(
                success=False,
                error=str(e)
            )
    
    async def send_bulk_notifications(self, store_id: UUID, orders_data: List[OrderData]) -> List[WhatsAppSendResponse]:
        """
        Массовая отправка уведомлений о заказах
        
        Args:
            store_id: ID магазина
            orders_data: Список данных заказов
            
        Returns:
            Список результатов отправки
        """
        results = []
        
        for order_data in orders_data:
            try:
                result = await self.send_order_notification(store_id, order_data)
                results.append(result)
                
                # Небольшая задержка между отправками для избежания спама
                import asyncio
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления для заказа {order_data.order_id}: {e}")
                results.append(WhatsAppSendResponse(
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    async def check_phone_number(self, store_id: UUID, phone_number: str) -> Dict[str, Any]:
        """
        Проверка существования номера телефона в WhatsApp
        
        Args:
            store_id: ID магазина
            phone_number: Номер телефона для проверки
            
        Returns:
            Результат проверки
        """
        try:
            # Проверяем статус WAHA сессии
            session_status = await self.session_manager.get_session_status(str(store_id))
            if session_status.get('status') != 'CONNECTED':
                return {
                    'success': False,
                    'error': f"WAHA сессия не подключена. Статус: {session_status.get('status')}"
                }
            
            session_name = self.session_manager.active_sessions.get(str(store_id), {}).get('session_name')
            if not session_name:
                return {
                    'success': False,
                    'error': 'Сессия не найдена'
                }
            
            # Проверяем номер через WAHA API
            result = await self.waha_client.check_phone_number(session_name, phone_number)
            
            return {
                'success': True,
                'exists': result.get('exists', False),
                'jid': result.get('jid'),
                'waha_response': result
            }
            
        except Exception as e:
            logger.error(f"Ошибка проверки номера телефона {phone_number} для магазина {store_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_message_statistics(self, store_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Получение статистики отправленных сообщений
        
        Args:
            store_id: ID магазина
            days: Количество дней для анализа
            
        Returns:
            Статистика сообщений
        """
        try:
            async with self.db.pool.acquire() as conn:
                # Общая статистика
                total_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_messages,
                        COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_messages,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_messages
                    FROM whatsapp_messages_log
                    WHERE store_id = $1 AND sent_at >= NOW() - INTERVAL '%s days'
                """, store_id, days)
                
                # Статистика по дням
                daily_stats = await conn.fetch("""
                    SELECT 
                        DATE(sent_at) as date,
                        COUNT(*) as messages_count,
                        COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_count,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
                    FROM whatsapp_messages_log
                    WHERE store_id = $1 AND sent_at >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE(sent_at)
                    ORDER BY date DESC
                """, store_id, days)
                
                return {
                    'success': True,
                    'total_messages': total_stats['total_messages'],
                    'sent_messages': total_stats['sent_messages'],
                    'delivered_messages': total_stats['delivered_messages'],
                    'failed_messages': total_stats['failed_messages'],
                    'success_rate': (total_stats['sent_messages'] / total_stats['total_messages'] * 100) if total_stats['total_messages'] > 0 else 0,
                    'daily_stats': [dict(row) for row in daily_stats]
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики сообщений для магазина {store_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
