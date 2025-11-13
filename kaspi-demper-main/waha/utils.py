# utils.py
"""
Вспомогательные утилиты для WAHA модуля
"""

import re
import logging
import asyncio
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from uuid import UUID
import hashlib
import json

from .config import get_config


logger = logging.getLogger(__name__)


class PhoneNumberValidator:
    """Валидатор номеров телефонов"""
    
    def __init__(self):
        self.config = get_config()
        self.pattern = re.compile(self.config.get("phone_number_pattern", r"^\+7\d{10}$"))
    
    def validate(self, phone_number: str) -> bool:
        """Валидация номера телефона"""
        if not self.config.get("validate_phone_numbers", True):
            return True
        
        return bool(self.pattern.match(phone_number))
    
    def normalize(self, phone_number: str) -> str:
        """Нормализация номера телефона"""
        # Удаляем все символы кроме цифр и +
        clean_phone = re.sub(r'[^\d+]', '', phone_number)
        
        # Добавляем код страны если нужно
        if clean_phone.startswith('8'):
            clean_phone = '+7' + clean_phone[1:]
        elif clean_phone.startswith('7') and not clean_phone.startswith('+7'):
            clean_phone = '+' + clean_phone
        elif not clean_phone.startswith('+'):
            clean_phone = '+7' + clean_phone
        
        return clean_phone
    
    def format_for_whatsapp(self, phone_number: str) -> str:
        """Форматирование номера для WhatsApp"""
        normalized = self.normalize(phone_number)
        # Удаляем + и добавляем @c.us
        clean_number = normalized.replace('+', '')
        return f"{clean_number}@c.us"


class RateLimiter:
    """Ограничитель скорости отправки сообщений"""
    
    def __init__(self):
        self.config = get_config()
        self.windows: Dict[str, List[datetime]] = {}
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """Проверка разрешения на отправку"""
        if not self.config.get("enable_rate_limiting", True):
            return True
        
        async with self.lock:
            now = datetime.now()
            window_minutes = self.config.get("rate_limit_window_minutes", 60)
            max_messages = self.config.get("max_messages_per_window", 100)
            
            # Очищаем старые записи
            cutoff_time = now - timedelta(minutes=window_minutes)
            
            if key not in self.windows:
                self.windows[key] = []
            
            # Удаляем старые записи
            self.windows[key] = [
                timestamp for timestamp in self.windows[key] 
                if timestamp > cutoff_time
            ]
            
            # Проверяем лимит
            if len(self.windows[key]) >= max_messages:
                return False
            
            # Добавляем новую запись
            self.windows[key].append(now)
            return True
    
    async def get_remaining_quota(self, key: str) -> int:
        """Получение оставшейся квоты"""
        async with self.lock:
            now = datetime.now()
            window_minutes = self.config.get("rate_limit_window_minutes", 60)
            max_messages = self.config.get("max_messages_per_window", 100)
            
            cutoff_time = now - timedelta(minutes=window_minutes)
            
            if key not in self.windows:
                return max_messages
            
            # Подсчитываем активные записи
            active_count = len([
                timestamp for timestamp in self.windows[key] 
                if timestamp > cutoff_time
            ])
            
            return max(0, max_messages - active_count)


class MessageTemplateProcessor:
    """Процессор шаблонов сообщений"""
    
    def __init__(self):
        self.config = get_config()
        self.variable_pattern = re.compile(r'\{([^}]+)\}')
    
    def extract_variables(self, template: str) -> List[str]:
        """Извлечение переменных из шаблона"""
        return self.variable_pattern.findall(template)
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """Валидация шаблона"""
        variables = self.extract_variables(template)
        
        # Проверяем лимит переменных
        max_variables = self.config.get("template_variables_limit", 20)
        if len(variables) > max_variables:
            return {
                "valid": False,
                "error": f"Слишком много переменных: {len(variables)} > {max_variables}"
            }
        
        # Проверяем на циклические ссылки
        for var in variables:
            if var in template.replace(f"{{{var}}}", ""):
                return {
                    "valid": False,
                    "error": f"Циклическая ссылка в переменной: {var}"
                }
        
        return {
            "valid": True,
            "variables": variables,
            "variable_count": len(variables)
        }
    
    def sanitize_template(self, template: str) -> str:
        """Очистка шаблона от потенциально опасных символов"""
        # Удаляем потенциально опасные символы
        dangerous_chars = ['<', '>', '&', '"', "'"]
        sanitized = template
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()


class ErrorHandler:
    """Обработчик ошибок"""
    
    def __init__(self):
        self.config = get_config()
        self.error_counts: Dict[str, int] = {}
        self.last_notification: Dict[str, datetime] = {}
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Логирование ошибки"""
        logger.error(f"[{error_type}] {error_message}", extra={
            "error_type": error_type,
            "context": context or {}
        })
        
        # Увеличиваем счетчик ошибок
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Проверяем порог для уведомлений
        threshold = self.config.get("admin_notification_threshold", 10)
        if self.error_counts[error_type] >= threshold:
            self._check_admin_notification(error_type)
    
    def _check_admin_notification(self, error_type: str):
        """Проверка необходимости уведомления администратора"""
        if not self.config.get("enable_admin_notifications", True):
            return
        
        now = datetime.now()
        last_notif = self.last_notification.get(error_type)
        
        # Уведомляем не чаще раза в час
        if last_notif and (now - last_notif).total_seconds() < 3600:
            return
        
        self.last_notification[error_type] = now
        
        logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: {error_type} - достигнут порог {self.error_counts[error_type]} ошибок")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Получение статистики ошибок"""
        return {
            "error_counts": self.error_counts.copy(),
            "last_notifications": {
                k: v.isoformat() for k, v in self.last_notification.items()
            }
        }
    
    def reset_error_counts(self):
        """Сброс счетчиков ошибок"""
        self.error_counts.clear()
        self.last_notification.clear()


class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.config = get_config()
        self.metrics: Dict[str, Any] = {
            "messages_sent": 0,
            "messages_failed": 0,
            "messages_delivered": 0,
            "sessions_active": 0,
            "templates_created": 0,
            "errors_total": 0,
            "last_reset": datetime.now().isoformat()
        }
        self.lock = asyncio.Lock()
    
    async def increment(self, metric_name: str, value: int = 1):
        """Увеличение метрики"""
        if not self.config.get("enable_metrics", True):
            return
        
        async with self.lock:
            if metric_name in self.metrics:
                self.metrics[metric_name] += value
            else:
                self.metrics[metric_name] = value
    
    async def set(self, metric_name: str, value: Any):
        """Установка значения метрики"""
        if not self.config.get("enable_metrics", True):
            return
        
        async with self.lock:
            self.metrics[metric_name] = value
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Получение всех метрик"""
        async with self.lock:
            return self.metrics.copy()
    
    async def reset_metrics(self):
        """Сброс метрик"""
        async with self.lock:
            self.metrics = {
                "messages_sent": 0,
                "messages_failed": 0,
                "messages_delivered": 0,
                "sessions_active": 0,
                "templates_created": 0,
                "errors_total": 0,
                "last_reset": datetime.now().isoformat()
            }


class DataSanitizer:
    """Очистка данных"""
    
    @staticmethod
    def sanitize_order_data(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка данных заказа"""
        sanitized = {}
        
        for key, value in order_data.items():
            if isinstance(value, str):
                # Удаляем потенциально опасные символы
                sanitized[key] = re.sub(r'[<>"\']', '', value).strip()
            elif isinstance(value, (int, float)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = DataSanitizer.sanitize_order_data(value)
            else:
                sanitized[key] = str(value).strip()
        
        return sanitized
    
    @staticmethod
    def sanitize_template_data(template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка данных шаблона"""
        sanitized = {}
        
        for key, value in template_data.items():
            if key == "template_text":
                # Особо тщательно очищаем текст шаблона
                sanitized[key] = re.sub(r'[<>"\']', '', str(value)).strip()
            elif isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        
        return sanitized


class HashGenerator:
    """Генератор хешей"""
    
    @staticmethod
    def generate_session_hash(store_id: str, timestamp: datetime) -> str:
        """Генерация хеша сессии"""
        data = f"{store_id}_{timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_message_hash(store_id: str, phone: str, template_id: str) -> str:
        """Генерация хеша сообщения"""
        data = f"{store_id}_{phone}_{template_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]


class TimeUtils:
    """Утилиты для работы со временем"""
    
    @staticmethod
    def get_kazakhstan_time() -> datetime:
        """Получение времени в Казахстане"""
        from datetime import timezone, timedelta
        
        # UTC+6 для Казахстана
        kz_tz = timezone(timedelta(hours=6))
        return datetime.now(kz_tz)
    
    @staticmethod
    def format_datetime_for_kaspi(dt: datetime) -> str:
        """Форматирование даты для Kaspi API"""
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    @staticmethod
    def parse_kaspi_timestamp(timestamp: Union[int, str]) -> datetime:
        """Парсинг timestamp от Kaspi"""
        if isinstance(timestamp, str):
            timestamp = int(timestamp)
        
        # Kaspi использует миллисекунды
        if timestamp > 1e10:  # Если больше 10^10, то это миллисекунды
            timestamp = timestamp / 1000
        
        return datetime.fromtimestamp(timestamp)


# Глобальные экземпляры утилит
phone_validator = PhoneNumberValidator()
rate_limiter = RateLimiter()
template_processor = MessageTemplateProcessor()
error_handler = ErrorHandler()
metrics_collector = MetricsCollector()


def get_phone_validator() -> PhoneNumberValidator:
    """Получение валидатора номеров телефонов"""
    return phone_validator


def get_rate_limiter() -> RateLimiter:
    """Получение ограничителя скорости"""
    return rate_limiter


def get_template_processor() -> MessageTemplateProcessor:
    """Получение процессора шаблонов"""
    return template_processor


def get_error_handler() -> ErrorHandler:
    """Получение обработчика ошибок"""
    return error_handler


def get_metrics_collector() -> MetricsCollector:
    """Получение сборщика метрик"""
    return metrics_collector
