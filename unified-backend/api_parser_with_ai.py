# api_parser_with_ai.py
"""
Модифицированный api_parser.py с интеграцией AI-продажника
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import sys
import os

# Добавляем путь к модулям интеграции
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'waha'))

from kaspi_ai_integration import get_kaspi_ai_integration

logger = logging.getLogger(__name__)

# Импортируем оригинальные функции из api_parser.py
from api_parser import (
    SessionManager,
    fetch_orders,
    map_order_data,
    map_top_products,
    calculate_metrics
)

async def get_sells_with_ai(shop_id: str) -> tuple[bool, Any]:
    """
    Модифицированная функция get_sells с интеграцией AI-продажника
    """
    try:
        # Получаем данные заказов как обычно
        session_manager = SessionManager(shop_uid=shop_id)
        if not await session_manager.load():
            return False, 'Сессия истекла, пожалуйста, войдите заново.'
        
        cookies = session_manager.get_cookies()
        result = get_sells_delivery_request(session_manager.merchant_uid, cookies)
        
        # Интеграция с AI-продажником
        await process_orders_with_ai(result.get('orders', []), shop_id)
        
        return True, result
        
    except Exception as e:
        logger.error(f"Ошибка в get_sells_with_ai: {e}")
        return False, f"Ошибка получения данных: {str(e)}"

async def process_orders_with_ai(orders: List[Dict[str, Any]], shop_id: str):
    """
    Обработка заказов с AI-продажником
    """
    try:
        # Получаем интеграцию AI-продажника
        ai_integration = get_kaspi_ai_integration()
        
        if not ai_integration.is_enabled():
            logger.info("AI-продажник отключен, пропускаем обработку заказов")
            return
        
        # Обрабатываем каждый заказ
        processed_count = 0
        for order in orders:
            try:
                # Преобразуем данные заказа в формат для AI-продажника
                order_data = convert_kaspi_order_to_ai_format(order, shop_id)
                
                if order_data:
                    # Триггерим AI-продажника для нового заказа
                    success = await ai_integration.process_new_order(order_data)
                    
                    if success:
                        processed_count += 1
                        logger.info(f"AI-продажник обработал заказ: {order_data.get('order_id', 'unknown')}")
                    else:
                        logger.warning(f"AI-продажник не смог обработать заказ: {order_data.get('order_id', 'unknown')}")
                
            except Exception as e:
                logger.error(f"Ошибка обработки заказа AI-продажником: {e}")
                continue
        
        logger.info(f"AI-продажник обработал {processed_count} заказов из {len(orders)}")
        
    except Exception as e:
        logger.error(f"Ошибка в process_orders_with_ai: {e}")

def convert_kaspi_order_to_ai_format(order: Dict[str, Any], shop_id: str) -> Optional[Dict[str, Any]]:
    """
    Преобразование данных заказа Kaspi в формат для AI-продажника
    """
    try:
        # Извлекаем данные из структуры заказа Kaspi
        order_info = order.get('order', {})
        customer_info = order.get('customer', {})
        
        # Проверяем наличие обязательных полей
        if not order_info or not customer_info:
            logger.warning("Неполные данные заказа")
            return None
        
        # Формируем данные в формате для AI-продажника
        ai_order_data = {
            "customer": {
                "phone": customer_info.get('phone', ''),
                "name": customer_info.get('name', customer_info.get('customer_name', ''))
            },
            "order": {
                "order_id": order_info.get('id', order_info.get('order_id', '')),
                "product_name": order_info.get('product_name', order_info.get('product', '')),
                "sku": order_info.get('sku', order_info.get('product_sku', '')),
                "quantity": order_info.get('quantity', order_info.get('item_qty', 1)),
                "total_amount": float(order_info.get('total_amount', order_info.get('amount', 0))),
                "shop_name": order_info.get('shop_name', order_info.get('store_name', 'Kaspi Store'))
            },
            "shop_id": shop_id,
            "timestamp": order_info.get('created_at', order_info.get('date', ''))
        }
        
        return ai_order_data
        
    except Exception as e:
        logger.error(f"Ошибка преобразования данных заказа: {e}")
        return None

async def trigger_ai_seller_for_delivered_order(order_data: Dict[str, Any], shop_id: str) -> bool:
    """
    Триггер AI-продажника для доставленного заказа
    """
    try:
        ai_integration = get_kaspi_ai_integration()
        
        if not ai_integration.is_enabled():
            return False
        
        # Преобразуем данные заказа
        ai_order_data = convert_kaspi_order_to_ai_format(order_data, shop_id)
        
        if not ai_order_data:
            return False
        
        # Триггерим ORDER_DELIVERED
        success = await ai_integration.process_delivered_order(ai_order_data)
        
        if success:
            logger.info(f"AI-продажник обработал доставку заказа: {ai_order_data.get('order', {}).get('order_id', 'unknown')}")
        
        return success
        
    except Exception as e:
        logger.error(f"Ошибка триггера AI-продажника для доставленного заказа: {e}")
        return False

def get_ai_seller_metrics() -> Dict[str, Any]:
    """
    Получение метрик AI-продажника
    """
    try:
        ai_integration = get_kaspi_ai_integration()
        return ai_integration.get_metrics()
    except Exception as e:
        logger.error(f"Ошибка получения метрик AI-продажника: {e}")
        return {"error": str(e)}

def reset_ai_seller_metrics():
    """
    Сброс метрик AI-продажника
    """
    try:
        ai_integration = get_kaspi_ai_integration()
        ai_integration.reset_metrics()
        logger.info("Метрики AI-продажника сброшены")
    except Exception as e:
        logger.error(f"Ошибка сброса метрик AI-продажника: {e}")

# Функция для инициализации AI-продажника при запуске приложения
async def initialize_ai_seller():
    """
    Инициализация AI-продажника
    """
    try:
        ai_integration = get_kaspi_ai_integration()
        await ai_integration.initialize()
        logger.info("AI-продажник инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации AI-продажника: {e}")

# Функция для очистки ресурсов AI-продажника при завершении приложения
async def cleanup_ai_seller():
    """
    Очистка ресурсов AI-продажника
    """
    try:
        ai_integration = get_kaspi_ai_integration()
        await ai_integration.cleanup()
        logger.info("AI-продажник очищен")
    except Exception as e:
        logger.error(f"Ошибка очистки AI-продажника: {e}")
