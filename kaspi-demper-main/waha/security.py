# security.py
"""
Модуль безопасности для WAHA интеграции
"""

import logging
import hashlib
import secrets
import re
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from uuid import UUID
import json

from .config import get_config
from .utils import get_phone_validator, DataSanitizer

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Валидатор безопасности"""
    
    def __init__(self):
        self.config = get_config()
        self.phone_validator = get_phone_validator()
        
        # Паттерны для проверки безопасности
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',  # JavaScript injection
            r'data:text/html',  # Data URI injection
            r'vbscript:',  # VBScript injection
            r'on\w+\s*=',  # Event handlers
            r'expression\s*\(',  # CSS expression
        ]
        
        # Компилируем паттерны
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
    
    def validate_template_security(self, template_text: str) -> Dict[str, Any]:
        """Валидация безопасности шаблона"""
        try:
            # Проверяем на опасные паттерны
            for pattern in self.compiled_patterns:
                if pattern.search(template_text):
                    return {
                        "valid": False,
                        "error": "Обнаружен потенциально опасный код в шаблоне",
                        "pattern": pattern.pattern
                    }
            
            # Проверяем длину шаблона
            max_length = 4000  # WhatsApp лимит
            if len(template_text) > max_length:
                return {
                    "valid": False,
                    "error": f"Шаблон слишком длинный: {len(template_text)} > {max_length}"
                }
            
            # Проверяем количество переменных
            variable_count = template_text.count('{')
            max_variables = self.config.get("template_variables_limit", 20)
            if variable_count > max_variables:
                return {
                    "valid": False,
                    "error": f"Слишком много переменных: {variable_count} > {max_variables}"
                }
            
            return {
                "valid": True,
                "message": "Шаблон прошел проверку безопасности"
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации безопасности шаблона: {e}")
            return {
                "valid": False,
                "error": f"Ошибка валидации: {str(e)}"
            }
    
    def validate_phone_number_security(self, phone_number: str) -> Dict[str, Any]:
        """Валидация безопасности номера телефона"""
        try:
            # Базовая валидация
            if not self.phone_validator.validate(phone_number):
                return {
                    "valid": False,
                    "error": "Неверный формат номера телефона"
                }
            
            # Проверяем на подозрительные паттерны
            suspicious_patterns = [
                r'^\+7(000|111|222|333|444|555|666|777|888|999)',  # Подозрительные номера
                r'^\+7\d{10}$'  # Только казахстанские номера
            ]
            
            for pattern in suspicious_patterns:
                if not re.match(pattern, phone_number):
                    return {
                        "valid": False,
                        "error": "Подозрительный номер телефона"
                    }
            
            return {
                "valid": True,
                "message": "Номер телефона прошел проверку безопасности"
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации безопасности номера: {e}")
            return {
                "valid": False,
                "error": f"Ошибка валидации: {str(e)}"
            }
    
    def validate_order_data_security(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация безопасности данных заказа"""
        try:
            # Очищаем данные
            sanitized_data = DataSanitizer.sanitize_order_data(order_data)
            
            # Проверяем обязательные поля
            required_fields = ['customer_name', 'customer_phone', 'order_id']
            for field in required_fields:
                if field not in sanitized_data or not sanitized_data[field]:
                    return {
                        "valid": False,
                        "error": f"Отсутствует обязательное поле: {field}"
                    }
            
            # Валидируем номер телефона
            phone_validation = self.validate_phone_number_security(sanitized_data['customer_phone'])
            if not phone_validation['valid']:
                return phone_validation
            
            # Проверяем длину полей
            field_limits = {
                'customer_name': 100,
                'order_id': 50,
                'product_name': 200
            }
            
            for field, limit in field_limits.items():
                if field in sanitized_data and len(str(sanitized_data[field])) > limit:
                    return {
                        "valid": False,
                        "error": f"Поле {field} слишком длинное: {len(str(sanitized_data[field]))} > {limit}"
                    }
            
            return {
                "valid": True,
                "message": "Данные заказа прошли проверку безопасности",
                "sanitized_data": sanitized_data
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации безопасности данных заказа: {e}")
            return {
                "valid": False,
                "error": f"Ошибка валидации: {str(e)}"
            }


class AccessController:
    """Контроллер доступа"""
    
    def __init__(self):
        self.config = get_config()
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
    
    def generate_api_key(self, store_id: UUID, permissions: List[str] = None) -> str:
        """Генерация API ключа для магазина"""
        try:
            # Генерируем случайный ключ
            key_data = f"{store_id}_{datetime.now().isoformat()}_{secrets.token_hex(16)}"
            api_key = hashlib.sha256(key_data.encode()).hexdigest()
            
            # Сохраняем информацию о ключе
            self.api_keys[api_key] = {
                "store_id": str(store_id),
                "permissions": permissions or ["read", "write"],
                "created_at": datetime.now(),
                "last_used": None,
                "is_active": True
            }
            
            logger.info(f"Сгенерирован API ключ для магазина {store_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"Ошибка генерации API ключа: {e}")
            raise
    
    def validate_api_key(self, api_key: str, required_permission: str = None) -> Dict[str, Any]:
        """Валидация API ключа"""
        try:
            if api_key not in self.api_keys:
                return {
                    "valid": False,
                    "error": "Неверный API ключ"
                }
            
            key_info = self.api_keys[api_key]
            
            # Проверяем активность ключа
            if not key_info["is_active"]:
                return {
                    "valid": False,
                    "error": "API ключ деактивирован"
                }
            
            # Проверяем права доступа
            if required_permission and required_permission not in key_info["permissions"]:
                return {
                    "valid": False,
                    "error": f"Недостаточно прав для операции: {required_permission}"
                }
            
            # Обновляем время последнего использования
            key_info["last_used"] = datetime.now()
            
            return {
                "valid": True,
                "store_id": key_info["store_id"],
                "permissions": key_info["permissions"]
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации API ключа: {e}")
            return {
                "valid": False,
                "error": f"Ошибка валидации: {str(e)}"
            }
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Отзыв API ключа"""
        try:
            if api_key in self.api_keys:
                self.api_keys[api_key]["is_active"] = False
                logger.info(f"API ключ {api_key[:8]}... отозван")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка отзыва API ключа: {e}")
            return False
    
    def generate_session_token(self, store_id: UUID, expires_in_hours: int = 24) -> str:
        """Генерация токена сессии"""
        try:
            # Генерируем токен
            token_data = f"{store_id}_{datetime.now().isoformat()}_{secrets.token_hex(32)}"
            session_token = hashlib.sha256(token_data.encode()).hexdigest()
            
            # Вычисляем время истечения
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            # Сохраняем токен
            self.session_tokens[session_token] = {
                "store_id": str(store_id),
                "created_at": datetime.now(),
                "expires_at": expires_at,
                "is_active": True
            }
            
            logger.info(f"Сгенерирован токен сессии для магазина {store_id}")
            return session_token
            
        except Exception as e:
            logger.error(f"Ошибка генерации токена сессии: {e}")
            raise
    
    def validate_session_token(self, session_token: str) -> Dict[str, Any]:
        """Валидация токена сессии"""
        try:
            if session_token not in self.session_tokens:
                return {
                    "valid": False,
                    "error": "Неверный токен сессии"
                }
            
            token_info = self.session_tokens[session_token]
            
            # Проверяем активность токена
            if not token_info["is_active"]:
                return {
                    "valid": False,
                    "error": "Токен сессии деактивирован"
                }
            
            # Проверяем срок действия
            if datetime.now() > token_info["expires_at"]:
                return {
                    "valid": False,
                    "error": "Токен сессии истек"
                }
            
            return {
                "valid": True,
                "store_id": token_info["store_id"],
                "expires_at": token_info["expires_at"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации токена сессии: {e}")
            return {
                "valid": False,
                "error": f"Ошибка валидации: {str(e)}"
            }
    
    def cleanup_expired_tokens(self):
        """Очистка истекших токенов"""
        try:
            now = datetime.now()
            expired_tokens = []
            
            for token, info in self.session_tokens.items():
                if now > info["expires_at"]:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.session_tokens[token]
            
            if expired_tokens:
                logger.info(f"Очищено {len(expired_tokens)} истекших токенов")
                
        except Exception as e:
            logger.error(f"Ошибка очистки токенов: {e}")


class RateLimiter:
    """Ограничитель скорости для безопасности"""
    
    def __init__(self):
        self.config = get_config()
        self.attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self, identifier: str, max_attempts: int = 10, window_minutes: int = 15) -> Dict[str, Any]:
        """Проверка ограничения скорости"""
        try:
            async with self.lock:
                now = datetime.now()
                
                # Проверяем, не заблокирован ли идентификатор
                if identifier in self.blocked_ips:
                    block_until = self.blocked_ips[identifier]
                    if now < block_until:
                        remaining_time = (block_until - now).total_seconds()
                        return {
                            "allowed": False,
                            "error": f"Идентификатор заблокирован до {block_until.isoformat()}",
                            "remaining_seconds": int(remaining_time)
                        }
                    else:
                        # Разблокируем
                        del self.blocked_ips[identifier]
                
                # Очищаем старые попытки
                cutoff_time = now - timedelta(minutes=window_minutes)
                
                if identifier not in self.attempts:
                    self.attempts[identifier] = []
                
                self.attempts[identifier] = [
                    attempt for attempt in self.attempts[identifier]
                    if attempt > cutoff_time
                ]
                
                # Проверяем лимит
                if len(self.attempts[identifier]) >= max_attempts:
                    # Блокируем на час
                    block_until = now + timedelta(hours=1)
                    self.blocked_ips[identifier] = block_until
                    
                    return {
                        "allowed": False,
                        "error": f"Превышен лимит попыток: {len(self.attempts[identifier])} >= {max_attempts}",
                        "blocked_until": block_until.isoformat()
                    }
                
                # Добавляем текущую попытку
                self.attempts[identifier].append(now)
                
                return {
                    "allowed": True,
                    "attempts_used": len(self.attempts[identifier]),
                    "attempts_remaining": max_attempts - len(self.attempts[identifier])
                }
                
        except Exception as e:
            logger.error(f"Ошибка проверки ограничения скорости: {e}")
            return {
                "allowed": False,
                "error": f"Ошибка проверки: {str(e)}"
            }


class SecurityAuditor:
    """Аудитор безопасности"""
    
    def __init__(self):
        self.security_events: List[Dict[str, Any]] = []
        self.max_events = 1000
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "info"):
        """Логирование события безопасности"""
        try:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "details": details
            }
            
            self.security_events.append(event)
            
            # Ограничиваем количество событий
            if len(self.security_events) > self.max_events:
                self.security_events = self.security_events[-self.max_events:]
            
            # Логируем в зависимости от серьезности
            if severity == "critical":
                logger.critical(f"КРИТИЧЕСКОЕ СОБЫТИЕ БЕЗОПАСНОСТИ: {event_type} - {details}")
            elif severity == "warning":
                logger.warning(f"Предупреждение безопасности: {event_type} - {details}")
            else:
                logger.info(f"Событие безопасности: {event_type} - {details}")
                
        except Exception as e:
            logger.error(f"Ошибка логирования события безопасности: {e}")
    
    def get_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Получение отчета по безопасности"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Фильтруем события по времени
            recent_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event["timestamp"]) >= cutoff_time
            ]
            
            # Группируем по типам событий
            event_counts = {}
            severity_counts = {"critical": 0, "warning": 0, "info": 0}
            
            for event in recent_events:
                event_type = event["event_type"]
                severity = event["severity"]
                
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                severity_counts[severity] += 1
            
            return {
                "period_hours": hours,
                "total_events": len(recent_events),
                "event_counts": event_counts,
                "severity_counts": severity_counts,
                "recent_events": recent_events[-10:],  # Последние 10 событий
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета безопасности: {e}")
            return {"error": str(e)}


# Глобальные экземпляры
security_validator = SecurityValidator()
access_controller = AccessController()
rate_limiter = RateLimiter()
security_auditor = SecurityAuditor()


def get_security_validator() -> SecurityValidator:
    """Получение валидатора безопасности"""
    return security_validator


def get_access_controller() -> AccessController:
    """Получение контроллера доступа"""
    return access_controller


def get_rate_limiter() -> RateLimiter:
    """Получение ограничителя скорости"""
    return rate_limiter


def get_security_auditor() -> SecurityAuditor:
    """Получение аудитора безопасности"""
    return security_auditor


# Декораторы для безопасности
def require_api_key(permission: str = None):
    """Декоратор для проверки API ключа"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Здесь должна быть логика проверки API ключа
            # В реальной реализации это будет интегрировано с FastAPI
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_security_validation():
    """Декоратор для проверки безопасности"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Здесь должна быть логика проверки безопасности
            return await func(*args, **kwargs)
        return wrapper
    return decorator
