"""
Сервис для работы с прокси
Адаптировано из unified-backend/proxy_balancer.py и proxy_config.py
"""
import os
from typing import Dict, Optional
from django.conf import settings

# Простая реализация proxy балансировки
# Если нужна полная функциональность, можно перенести из unified-backend


def get_proxy_url(identifier: Optional[str] = None) -> Optional[str]:
    """
    Возвращает URL прокси для использования в запросах
    Если прокси не настроены, возвращает None
    """
    if not getattr(settings, 'KASPI_SETTINGS', {}).get('PROXY_ENABLED', False):
        return None
    
    # Здесь можно добавить логику балансировки прокси
    # Пока возвращаем None (без прокси)
    return None


def get_proxy_dict(identifier: Optional[str] = None) -> Optional[Dict]:
    """Возвращает словарь с настройками прокси"""
    proxy_url = get_proxy_url(identifier)
    if not proxy_url:
        return None
    
    # Парсим URL прокси в словарь
    # Формат: http://user:pass@host:port
    return {
        'http': proxy_url,
        'https': proxy_url
    }

