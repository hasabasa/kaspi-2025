# ai_seller_integration.py
"""
Модуль интеграции AI-продажника с WAHA системой
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class CustomerData:
    """Данные клиента"""
    phone: str
    name: str
    order_id: str
    product_name: str
    product_sku: str
    quantity: int
    total_amount: float
    shop_name: str

@dataclass
class AISellerConfig:
    """Конфигурация AI-продажника"""
    ai_seller_url: str = "http://localhost:8080"
    enabled: bool = True
    max_messages_per_customer: int = 3
    message_cooldown_hours: int = 24
    fallback_enabled: bool = True
    test_mode: bool = False

class RateLimiter:
    """Контроль частоты отправки сообщений"""
    
    def __init__(self, cooldown_hours: int = 24):
        self.cooldown_hours = cooldown_hours
        self.customer_last_message = {}
        self.customer_message_count = {}
    
    def can_send_message(self, customer_phone: str, max_messages: int = 3) -> bool:
        """Проверка возможности отправки сообщения"""
        now = datetime.now()
        
        # Проверка количества сообщений
        message_count = self.customer_message_count.get(customer_phone, 0)
        if message_count >= max_messages:
            logger.warning(f"Превышен лимит сообщений для {customer_phone}: {message_count}/{max_messages}")
            return False
        
        # Проверка cooldown
        last_message_time = self.customer_last_message.get(customer_phone)
        if last_message_time:
            time_diff = now - last_message_time
            if time_diff.total_seconds() < self.cooldown_hours * 3600:
                logger.info(f"Cooldown активен для {customer_phone}: {time_diff}")
                return False
        
        return True
    
    def record_message_sent(self, customer_phone: str):
        """Запись отправленного сообщения"""
        now = datetime.now()
        self.customer_last_message[customer_phone] = now
        self.customer_message_count[customer_phone] = self.customer_message_count.get(customer_phone, 0) + 1
        logger.info(f"Сообщение записано для {customer_phone}: {self.customer_message_count[customer_phone]}")

class AISellerIntegration:
    """Интеграция с AI-продажником"""
    
    def __init__(self, config: AISellerConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.message_cooldown_hours)
        self.session = None
        self.metrics = {
            "messages_sent": 0,
            "messages_blocked": 0,
            "errors": 0,
            "success_rate": 0.0
        }
    
    async def initialize(self):
        """Инициализация интеграции"""
        if not self.config.enabled:
            logger.info("AI-продажник отключен")
            return
        
        self.session = aiohttp.ClientSession()
        logger.info(f"AI-продажник инициализирован: {self.config.ai_seller_url}")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.session:
            await self.session.close()
    
    def is_enabled(self) -> bool:
        """Проверка активности интеграции"""
        return self.config.enabled
    
    async def trigger_post_purchase(self, customer_data: CustomerData) -> bool:
        """Триггер для этапа POST_PURCHASE"""
        if not self.is_enabled():
            return False
        
        try:
            # Проверка rate limiting
            if not self.rate_limiter.can_send_message(customer_data.phone, self.config.max_messages_per_customer):
                self.metrics["messages_blocked"] += 1
                logger.info(f"Сообщение заблокировано rate limiter для {customer_data.phone}")
                return False
            
            # Подготовка данных для AI-продажника
            event_data = {
                "waha_stage_id": "POST_PURCHASE",
                "customer": {
                    "phone": customer_data.phone,
                    "name": customer_data.name
                },
                "order": {
                    "sku": customer_data.product_sku,
                    "product_name": customer_data.product_name,
                    "quantity": customer_data.quantity,
                    "total_amount": customer_data.total_amount,
                    "order_id": customer_data.order_id
                }
            }
            
            # Отправка запроса к AI-продажнику
            success = await self._send_to_ai_seller(event_data)
            
            if success:
                self.rate_limiter.record_message_sent(customer_data.phone)
                self.metrics["messages_sent"] += 1
                logger.info(f"POST_PURCHASE триггер отправлен для {customer_data.phone}")
            else:
                self.metrics["errors"] += 1
                if self.config.fallback_enabled:
                    await self._send_fallback_message(customer_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка в trigger_post_purchase: {e}")
            self.metrics["errors"] += 1
            return False
    
    async def trigger_order_delivered(self, customer_data: CustomerData) -> bool:
        """Триггер для этапа ORDER_DELIVERED"""
        if not self.is_enabled():
            return False
        
        try:
            # Проверка rate limiting
            if not self.rate_limiter.can_send_message(customer_data.phone, self.config.max_messages_per_customer):
                self.metrics["messages_blocked"] += 1
                return False
            
            # Подготовка данных для AI-продажника
            event_data = {
                "waha_stage_id": "ORDER_DELIVERED",
                "customer": {
                    "phone": customer_data.phone,
                    "name": customer_data.name
                },
                "order": {
                    "sku": customer_data.product_sku,
                    "product_name": customer_data.product_name,
                    "quantity": customer_data.quantity,
                    "total_amount": customer_data.total_amount,
                    "order_id": customer_data.order_id
                }
            }
            
            # Отправка запроса к AI-продажнику
            success = await self._send_to_ai_seller(event_data)
            
            if success:
                self.rate_limiter.record_message_sent(customer_data.phone)
                self.metrics["messages_sent"] += 1
                logger.info(f"ORDER_DELIVERED триггер отправлен для {customer_data.phone}")
            else:
                self.metrics["errors"] += 1
                if self.config.fallback_enabled:
                    await self._send_fallback_message(customer_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка в trigger_order_delivered: {e}")
            self.metrics["errors"] += 1
            return False
    
    async def _send_to_ai_seller(self, event_data: Dict[str, Any]) -> bool:
        """Отправка данных к AI-продажнику"""
        try:
            if not self.session:
                logger.error("HTTP сессия не инициализирована")
                return False
            
            url = f"{self.config.ai_seller_url}/event_handler"
            
            async with self.session.post(
                url,
                json=event_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"AI-продажник ответил: {result}")
                    return True
                else:
                    logger.error(f"AI-продажник вернул ошибку: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка отправки к AI-продажнику: {e}")
            return False
    
    async def _send_fallback_message(self, customer_data: CustomerData):
        """Отправка fallback сообщения через WAHA"""
        try:
            fallback_message = f"""Здравствуйте, {customer_data.name}!
Спасибо за ваш заказ {customer_data.order_id}.

Ваш заказ "{customer_data.product_name}" готов к самовывозу.

Если у вас есть вопросы, обращайтесь в любое время.

С уважением,
{customer_data.shop_name}"""
            
            # Здесь можно интегрировать с WAHA для отправки fallback сообщения
            logger.info(f"Fallback сообщение подготовлено для {customer_data.phone}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки fallback сообщения: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        total_attempts = self.metrics["messages_sent"] + self.metrics["messages_blocked"] + self.metrics["errors"]
        if total_attempts > 0:
            self.metrics["success_rate"] = self.metrics["messages_sent"] / total_attempts
        
        return {
            **self.metrics,
            "rate_limiter_stats": {
                "active_customers": len(self.rate_limiter.customer_last_message),
                "cooldown_hours": self.rate_limiter.cooldown_hours
            }
        }
    
    def reset_metrics(self):
        """Сброс метрик"""
        self.metrics = {
            "messages_sent": 0,
            "messages_blocked": 0,
            "errors": 0,
            "success_rate": 0.0
        }
        logger.info("Метрики AI-продажника сброшены")

# Глобальный экземпляр интеграции
ai_seller_integration = None

def get_ai_seller_integration() -> AISellerIntegration:
    """Получение экземпляра интеграции"""
    global ai_seller_integration
    if ai_seller_integration is None:
        config = AISellerConfig(
            ai_seller_url=os.getenv("AI_SELLER_URL", "http://localhost:8080"),
            enabled=os.getenv("AI_SELLER_ENABLED", "true").lower() == "true",
            max_messages_per_customer=int(os.getenv("AI_SELLER_MAX_MESSAGES", "3")),
            message_cooldown_hours=int(os.getenv("AI_SELLER_COOLDOWN_HOURS", "24")),
            fallback_enabled=os.getenv("AI_SELLER_FALLBACK", "true").lower() == "true",
            test_mode=os.getenv("AI_SELLER_TEST_MODE", "false").lower() == "true"
        )
        ai_seller_integration = AISellerIntegration(config)
    
    return ai_seller_integration
