# ai_seller_config.py
"""
Конфигурация AI-продажника
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class AISellerSettings:
    """Настройки AI-продажника"""
    
    # Основные настройки
    enabled: bool = True
    ai_seller_url: str = "http://localhost:8080"
    test_mode: bool = False
    
    # Настройки частоты сообщений
    max_messages_per_customer: int = 3
    message_cooldown_hours: int = 24
    max_daily_messages: int = 100
    
    # Fallback настройки
    fallback_enabled: bool = True
    fallback_message_template: str = """Здравствуйте, {customer_name}!
Спасибо за ваш заказ {order_id}.

Ваш заказ "{product_name}" готов к самовывозу.

Если у вас есть вопросы, обращайтесь в любое время.

С уважением,
{shop_name}"""
    
    # OpenAI настройки
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 500
    
    # Google Sheets настройки
    google_sheets_url: str = ""
    google_credentials_file: str = "kaspiseller-57379-firebase-adminsdk-fbsvc-1c22a63a88.json"
    
    # WAHA настройки
    waha_api_endpoint: str = "http://localhost:3000"
    waha_session_id: str = "kaspi_demper_session"
    
    # Мониторинг
    enable_metrics: bool = True
    metrics_retention_days: int = 30
    
    # Безопасность
    enable_rate_limiting: bool = True
    enable_opt_out: bool = True
    opt_out_keywords: list = ["стоп", "отписка", "не пишите", "stop"]
    
    @classmethod
    def from_env(cls) -> 'AISellerSettings':
        """Создание настроек из переменных окружения"""
        return cls(
            enabled=os.getenv("AI_SELLER_ENABLED", "true").lower() == "true",
            ai_seller_url=os.getenv("AI_SELLER_URL", "http://localhost:8080"),
            test_mode=os.getenv("AI_SELLER_TEST_MODE", "false").lower() == "true",
            
            max_messages_per_customer=int(os.getenv("AI_SELLER_MAX_MESSAGES", "3")),
            message_cooldown_hours=int(os.getenv("AI_SELLER_COOLDOWN_HOURS", "24")),
            max_daily_messages=int(os.getenv("AI_SELLER_MAX_DAILY_MESSAGES", "100")),
            
            fallback_enabled=os.getenv("AI_SELLER_FALLBACK", "true").lower() == "true",
            fallback_message_template=os.getenv("AI_SELLER_FALLBACK_TEMPLATE", cls.fallback_message_template),
            
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "500")),
            
            google_sheets_url=os.getenv("GOOGLE_SHEET_URL", ""),
            google_credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", cls.google_credentials_file),
            
            waha_api_endpoint=os.getenv("WAHA_API_ENDPOINT", "http://localhost:3000"),
            waha_session_id=os.getenv("WAHA_SESSION_ID", "kaspi_demper_session"),
            
            enable_metrics=os.getenv("AI_SELLER_METRICS", "true").lower() == "true",
            metrics_retention_days=int(os.getenv("AI_SELLER_METRICS_RETENTION", "30")),
            
            enable_rate_limiting=os.getenv("AI_SELLER_RATE_LIMITING", "true").lower() == "true",
            enable_opt_out=os.getenv("AI_SELLER_OPT_OUT", "true").lower() == "true",
            opt_out_keywords=os.getenv("AI_SELLER_OPT_OUT_KEYWORDS", "стоп,отписка,не пишите,stop").split(",")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "enabled": self.enabled,
            "ai_seller_url": self.ai_seller_url,
            "test_mode": self.test_mode,
            "max_messages_per_customer": self.max_messages_per_customer,
            "message_cooldown_hours": self.message_cooldown_hours,
            "max_daily_messages": self.max_daily_messages,
            "fallback_enabled": self.fallback_enabled,
            "openai_model": self.openai_model,
            "openai_temperature": self.openai_temperature,
            "openai_max_tokens": self.openai_max_tokens,
            "enable_metrics": self.enable_metrics,
            "enable_rate_limiting": self.enable_rate_limiting,
            "enable_opt_out": self.enable_opt_out
        }
    
    def validate(self) -> bool:
        """Валидация настроек"""
        if not self.ai_seller_url:
            return False
        
        if self.max_messages_per_customer <= 0:
            return False
        
        if self.message_cooldown_hours <= 0:
            return False
        
        if self.max_daily_messages <= 0:
            return False
        
        return True

# Глобальный экземпляр настроек
settings = AISellerSettings.from_env()

def get_settings() -> AISellerSettings:
    """Получение настроек"""
    return settings

def update_settings(new_settings: Dict[str, Any]) -> bool:
    """Обновление настроек"""
    global settings
    try:
        for key, value in new_settings.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        return settings.validate()
    except Exception:
        return False
