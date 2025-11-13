# kaspi_ai_integration.py
"""
Интеграция AI-продажника с основным приложением Kaspi Demper
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Добавляем путь к WAHA модулю
sys.path.append(os.path.join(os.path.dirname(__file__), 'waha'))

from ai_seller_integration import (
    AISellerIntegration, 
    CustomerData, 
    AISellerConfig,
    get_ai_seller_integration
)

logger = logging.getLogger(__name__)

class KaspiAIIntegration:
    """Интеграция AI-продажника с Kaspi Demper"""
    
    def __init__(self):
        self.ai_seller = get_ai_seller_integration()
        self.enabled = True
    
    async def initialize(self):
        """Инициализация интеграции"""
        try:
            await self.ai_seller.initialize()
            logger.info("Kaspi AI интеграция инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации Kaspi AI интеграции: {e}")
            self.enabled = False
    
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            await self.ai_seller.cleanup()
            logger.info("Kaspi AI интеграция очищена")
        except Exception as e:
            logger.error(f"Ошибка очистки Kaspi AI интеграции: {e}")
    
    def is_enabled(self) -> bool:
        """Проверка активности интеграции"""
        return self.enabled and self.ai_seller.is_enabled()
    
    async def process_new_order(self, order_data: Dict[str, Any]) -> bool:
        """Обработка нового заказа"""
        if not self.is_enabled():
            logger.info("AI-продажник отключен, пропускаем обработку заказа")
            return False
        
        try:
            # Преобразование данных заказа в формат CustomerData
            customer_data = self._convert_order_to_customer_data(order_data)
            
            if not customer_data:
                logger.warning("Не удалось преобразовать данные заказа")
                return False
            
            # Триггер POST_PURCHASE для нового заказа
            success = await self.ai_seller.trigger_post_purchase(customer_data)
            
            if success:
                logger.info(f"AI-продажник обработал заказ {customer_data.order_id}")
            else:
                logger.warning(f"AI-продажник не смог обработать заказ {customer_data.order_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка обработки заказа AI-продажником: {e}")
            return False
    
    async def process_delivered_order(self, order_data: Dict[str, Any]) -> bool:
        """Обработка доставленного заказа"""
        if not self.is_enabled():
            return False
        
        try:
            # Преобразование данных заказа в формат CustomerData
            customer_data = self._convert_order_to_customer_data(order_data)
            
            if not customer_data:
                return False
            
            # Триггер ORDER_DELIVERED для доставленного заказа
            success = await self.ai_seller.trigger_order_delivered(customer_data)
            
            if success:
                logger.info(f"AI-продажник обработал доставку заказа {customer_data.order_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка обработки доставки заказа AI-продажником: {e}")
            return False
    
    def _convert_order_to_customer_data(self, order_data: Dict[str, Any]) -> Optional[CustomerData]:
        """Преобразование данных заказа в CustomerData"""
        try:
            # Извлечение данных из структуры заказа Kaspi
            customer_info = order_data.get('customer', {})
            order_info = order_data.get('order', {})
            
            # Проверка обязательных полей
            required_fields = ['phone', 'name', 'order_id', 'product_name']
            for field in required_fields:
                if not customer_info.get(field) and not order_info.get(field):
                    logger.warning(f"Отсутствует обязательное поле: {field}")
                    return None
            
            return CustomerData(
                phone=customer_info.get('phone') or order_info.get('phone', ''),
                name=customer_info.get('name') or order_info.get('customer_name', ''),
                order_id=order_info.get('order_id') or order_info.get('id', ''),
                product_name=order_info.get('product_name') or order_info.get('product', ''),
                product_sku=order_info.get('sku') or order_info.get('product_sku', ''),
                quantity=order_info.get('quantity') or order_info.get('item_qty', 1),
                total_amount=float(order_info.get('total_amount') or order_info.get('amount', 0)),
                shop_name=order_info.get('shop_name') or order_info.get('store_name', 'Kaspi Store')
            )
            
        except Exception as e:
            logger.error(f"Ошибка преобразования данных заказа: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик интеграции"""
        return {
            "enabled": self.is_enabled(),
            "ai_seller_metrics": self.ai_seller.get_metrics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_metrics(self):
        """Сброс метрик"""
        self.ai_seller.reset_metrics()

# Глобальный экземпляр интеграции
kaspi_ai_integration = None

def get_kaspi_ai_integration() -> KaspiAIIntegration:
    """Получение экземпляра интеграции"""
    global kaspi_ai_integration
    if kaspi_ai_integration is None:
        kaspi_ai_integration = KaspiAIIntegration()
    
    return kaspi_ai_integration
