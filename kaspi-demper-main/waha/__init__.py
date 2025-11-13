# __init__.py
"""
WAHA интеграция для Kaspi Demper
Модуль для автоматической отправки WhatsApp уведомлений о заказах
"""

from .waha_client import WAHAClient, WAHASessionManager
from .models import (
    WhatsAppTemplate, WhatsAppTemplateCreate, WhatsAppTemplateUpdate,
    WAHASettings, WAHASettingsCreate, WhatsAppMessageLog,
    OrderData, WhatsAppSendResponse, WAHAWebhookEvent
)
from .template_manager import TemplateManager
from .message_sender import WhatsAppMessageSender
from .order_integration import OrderIntegration
from .database import WAHA_Database
from .waha_integration import WAHAManager, initialize_waha, shutdown_waha, get_waha_manager, get_waha_router
from .config import WAHAConfig, get_config, initialize_config
from .utils import (
    PhoneNumberValidator, RateLimiter, MessageTemplateProcessor,
    ErrorHandler, MetricsCollector, DataSanitizer, HashGenerator, TimeUtils,
    get_phone_validator, get_rate_limiter, get_template_processor,
    get_error_handler, get_metrics_collector
)
from .monitoring import WAHAMonitor, AlertManager, initialize_monitoring, shutdown_monitoring
from .security import (
    SecurityValidator, AccessController, RateLimiter as SecurityRateLimiter,
    SecurityAuditor, get_security_validator, get_access_controller,
    get_security_auditor
)

__version__ = "1.0.0"
__author__ = "Kaspi Demper Team"
__description__ = "WAHA интеграция для автоматической отправки WhatsApp уведомлений о заказах Kaspi"

__all__ = [
    # Основные компоненты
    "WAHAClient",
    "WAHASessionManager",
    "WAHAManager",
    
    # Модели данных
    "WhatsAppTemplate",
    "WhatsAppTemplateCreate", 
    "WhatsAppTemplateUpdate",
    "WAHASettings",
    "WAHASettingsCreate",
    "WhatsAppMessageLog",
    "OrderData",
    "WhatsAppSendResponse",
    "WAHAWebhookEvent",
    
    # Менеджеры
    "TemplateManager",
    "WhatsAppMessageSender",
    "OrderIntegration",
    
    # База данных
    "WAHA_Database",
    
    # Конфигурация
    "WAHAConfig",
    "get_config",
    "initialize_config",
    
    # Утилиты
    "PhoneNumberValidator",
    "RateLimiter",
    "MessageTemplateProcessor",
    "ErrorHandler",
    "MetricsCollector",
    "DataSanitizer",
    "HashGenerator",
    "TimeUtils",
    "get_phone_validator",
    "get_rate_limiter",
    "get_template_processor",
    "get_error_handler",
    "get_metrics_collector",
    
    # Мониторинг
    "WAHAMonitor",
    "AlertManager",
    "initialize_monitoring",
    "shutdown_monitoring",
    
    # Безопасность
    "SecurityValidator",
    "AccessController",
    "SecurityRateLimiter",
    "SecurityAuditor",
    "get_security_validator",
    "get_access_controller",
    "get_security_auditor",
    
    # Инициализация
    "initialize_waha",
    "shutdown_waha",
    "get_waha_manager",
    "get_waha_router"
]

# Информация о модуле
MODULE_INFO = {
    "name": "WAHA Integration",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "components": {
        "core": ["WAHAClient", "WAHAManager", "WAHASessionManager"],
        "models": ["WhatsAppTemplate", "WAHASettings", "OrderData"],
        "managers": ["TemplateManager", "WhatsAppMessageSender", "OrderIntegration"],
        "database": ["WAHA_Database"],
        "utils": ["PhoneNumberValidator", "RateLimiter", "ErrorHandler"],
        "monitoring": ["WAHAMonitor", "AlertManager"],
        "security": ["SecurityValidator", "AccessController", "SecurityAuditor"]
    },
    "features": [
        "Автоматическая отправка WhatsApp уведомлений",
        "Подключение через связанные устройства",
        "Кастомные шаблоны сообщений",
        "Webhook для входящих сообщений",
        "Мониторинг и метрики",
        "Безопасность и валидация",
        "REST API для управления",
        "Интеграция с Kaspi Demper"
    ]
}
