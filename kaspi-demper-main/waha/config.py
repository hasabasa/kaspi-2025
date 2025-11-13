# config.py
"""
Конфигурация для WAHA модуля
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class WAHASettings(BaseSettings):
    """Настройки WAHA модуля"""
    
    # Основные настройки WAHA сервера
    waha_server_url: str = Field(
        default="http://localhost:3000",
        description="URL WAHA сервера"
    )
    
    # Настройки webhook
    webhook_base_url: str = Field(
        default="http://localhost:8000",
        description="Базовый URL для webhook"
    )
    
    # Ограничения
    max_messages_per_day: int = Field(
        default=1000,
        description="Максимальное количество сообщений в день"
    )
    
    message_delay_seconds: float = Field(
        default=1.0,
        description="Задержка между отправкой сообщений в секундах"
    )
    
    retry_attempts: int = Field(
        default=3,
        description="Количество попыток повторной отправки"
    )
    
    retry_delay_seconds: float = Field(
        default=5.0,
        description="Задержка между попытками повторной отправки"
    )
    
    # Настройки сессий
    session_timeout_minutes: int = Field(
        default=30,
        description="Таймаут сессии в минутах"
    )
    
    session_check_interval_minutes: int = Field(
        default=5,
        description="Интервал проверки сессий в минутах"
    )
    
    # Настройки базы данных
    db_pool_size: int = Field(
        default=10,
        description="Размер пула соединений с БД"
    )
    
    db_max_overflow: int = Field(
        default=20,
        description="Максимальное переполнение пула БД"
    )
    
    # Настройки логирования
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования"
    )
    
    log_file: Optional[str] = Field(
        default="logs/waha.log",
        description="Файл для логов"
    )
    
    log_max_size_mb: int = Field(
        default=100,
        description="Максимальный размер лог файла в МБ"
    )
    
    log_backup_count: int = Field(
        default=5,
        description="Количество резервных копий логов"
    )
    
    # Настройки безопасности
    enable_rate_limiting: bool = Field(
        default=True,
        description="Включить ограничение скорости отправки"
    )
    
    rate_limit_window_minutes: int = Field(
        default=60,
        description="Окно для ограничения скорости в минутах"
    )
    
    max_messages_per_window: int = Field(
        default=100,
        description="Максимальное количество сообщений в окне"
    )
    
    # Настройки валидации
    validate_phone_numbers: bool = Field(
        default=True,
        description="Валидировать номера телефонов"
    )
    
    phone_number_pattern: str = Field(
        default=r"^\+7\d{10}$",
        description="Регулярное выражение для валидации номеров"
    )
    
    # Настройки мониторинга
    enable_metrics: bool = Field(
        default=True,
        description="Включить сбор метрик"
    )
    
    metrics_port: int = Field(
        default=9090,
        description="Порт для метрик Prometheus"
    )
    
    # Настройки уведомлений
    enable_admin_notifications: bool = Field(
        default=True,
        description="Включить уведомления администратора"
    )
    
    admin_notification_threshold: int = Field(
        default=10,
        description="Порог ошибок для уведомления администратора"
    )
    
    # Настройки шаблонов
    default_template_enabled: bool = Field(
        default=True,
        description="Автоматически создавать шаблон по умолчанию"
    )
    
    template_variables_limit: int = Field(
        default=20,
        description="Максимальное количество переменных в шаблоне"
    )
    
    # Настройки интеграции с Kaspi
    kaspi_order_statuses: list = Field(
        default=["NEW", "CONFIRMED", "PROCESSING"],
        description="Статусы заказов для отправки уведомлений"
    )
    
    kaspi_integration_enabled: bool = Field(
        default=True,
        description="Включить интеграцию с Kaspi"
    )
    
    # Настройки разработки
    debug_mode: bool = Field(
        default=False,
        description="Режим отладки"
    )
    
    mock_waha_responses: bool = Field(
        default=False,
        description="Использовать мок ответы WAHA для тестирования"
    )
    
    class Config:
        env_prefix = "WAHA_"
        env_file = ".env"
        case_sensitive = False


class WAHAConfig:
    """Глобальная конфигурация WAHA"""
    
    def __init__(self):
        self.settings = WAHASettings()
        self._initialized = False
    
    def initialize(self, **kwargs):
        """Инициализация конфигурации с переопределением параметров"""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        self._initialized = True
    
    def get(self, key: str, default=None):
        """Получение значения конфигурации"""
        return getattr(self.settings, key, default)
    
    def set(self, key: str, value):
        """Установка значения конфигурации"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
    
    def is_initialized(self) -> bool:
        """Проверка инициализации"""
        return self._initialized
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return self.settings.dict()
    
    def update_from_env(self):
        """Обновление конфигурации из переменных окружения"""
        self.settings = WAHASettings()


# Глобальный экземпляр конфигурации
config = WAHAConfig()


def get_config() -> WAHAConfig:
    """Получение глобальной конфигурации"""
    return config


def initialize_config(**kwargs) -> WAHAConfig:
    """Инициализация конфигурации"""
    config.initialize(**kwargs)
    return config


# Предустановленные конфигурации для разных окружений
DEVELOPMENT_CONFIG = {
    "debug_mode": True,
    "log_level": "DEBUG",
    "mock_waha_responses": True,
    "max_messages_per_day": 100,
    "message_delay_seconds": 0.5
}

PRODUCTION_CONFIG = {
    "debug_mode": False,
    "log_level": "INFO",
    "mock_waha_responses": False,
    "max_messages_per_day": 10000,
    "message_delay_seconds": 2.0,
    "enable_rate_limiting": True,
    "retry_attempts": 5
}

TESTING_CONFIG = {
    "debug_mode": True,
    "log_level": "DEBUG",
    "mock_waha_responses": True,
    "max_messages_per_day": 10,
    "message_delay_seconds": 0.1,
    "enable_rate_limiting": False
}


def load_environment_config(env: str = "development") -> dict:
    """Загрузка конфигурации для окружения"""
    configs = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "testing": TESTING_CONFIG
    }
    
    return configs.get(env, DEVELOPMENT_CONFIG)
