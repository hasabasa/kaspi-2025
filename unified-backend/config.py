"""
@file: config.py
@description: Конфигурация для unified-backend
@dependencies: pydantic, python-dotenv
@created: 2025-01-27
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # База данных
    DB_MODE: str = Field(default="supabase", env="DB_MODE")
    SUPABASE_URL: str = Field(default="", env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(default="", env="SUPABASE_KEY")
    
    # PostgreSQL (если используется)
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="kaspi_demper", env="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="", env="POSTGRES_PASSWORD")
    
    # Аутентификация
    AUTH_METHOD: str = Field(default="playwright", env="AUTH_METHOD")
    
    # CORS
    CORS_ALLOWED_ORIGINS: str = Field(
        default=r"^(http:\/\/localhost(:\d+)?|http:\/\/127\.0\.0\.1(:\d+)?)$",
        env="CORS_ALLOWED_ORIGINS"
    )
    
    # Proxy
    PROXY_ENABLED: bool = Field(default=False, env="PROXY_ENABLED")
    PROXY_LIST: str = Field(default="", env="PROXY_LIST")
    
    # Demper
    DEMPER_ENABLED: bool = Field(default=True, env="DEMPER_ENABLED")
    DEMPER_INTERVAL: int = Field(default=300, env="DEMPER_INTERVAL")  # 5 минут
    
    # Логирование
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # WAHA
    WAHA_API_URL: str = Field(default="http://localhost:3000", env="WAHA_API_URL")
    WAHA_ENABLED: bool = Field(default=False, env="WAHA_ENABLED")
    WAHA_WEBHOOK_BASE_URL: str = Field(default="http://localhost:8010", env="WAHA_WEBHOOK_BASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Создаем экземпляр настроек
settings = Settings()

def get_database_config():
    """Получить конфигурацию базы данных"""
    if settings.DB_MODE == "supabase":
        return {
            "url": settings.SUPABASE_URL,
            "key": settings.SUPABASE_KEY
        }
    elif settings.DB_MODE == "postgres":
        return {
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD
        }
    else:
        raise ValueError(f"Unsupported database mode: {settings.DB_MODE}")