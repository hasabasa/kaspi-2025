"""
SessionManager для управления сессиями Kaspi
Адаптирован из unified-backend/api_parser.py
"""
import json
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from api.models import KaspiStore


class SessionManager:
    """Менеджер сессий для работы с cookies и авторизацией"""
    
    def __init__(self, user_id=None, merchant_uid=None, shop_uid=None):
        self.user_id = user_id
        self.merchant_uid = merchant_uid
        self.shop_uid = shop_uid
        self.session_data = None
        self.last_login = None
        self.store = None
    
    def load(self):
        """Загружает данные сессии из базы данных и проверяет её актуальность"""
        try:
            if self.shop_uid:
                self.store = KaspiStore.objects.get(id=self.shop_uid)
            elif self.user_id and self.merchant_uid:
                self.store = KaspiStore.objects.get(
                    user_id=self.user_id,
                    merchant_id=self.merchant_uid
                )
            else:
                raise KaspiStore.DoesNotExist("Магазин не найден")
            
            self.merchant_uid = self.store.merchant_id
            guid_data = self.store.guid
            
            # Обработка разных форматов guid
            if isinstance(guid_data, dict):
                self.session_data = guid_data
            elif isinstance(guid_data, str):
                try:
                    self.session_data = json.loads(guid_data)
                except (json.JSONDecodeError, TypeError):
                    self.session_data = guid_data
            else:
                self.session_data = guid_data
            
            self.last_login = self.store.last_login
            
            # Проверяем валидность сессии
            if not self.is_session_valid():
                # TODO: Реализовать переавторизацию
                return False
            return True
            
        except KaspiStore.DoesNotExist:
            return False
    
    def get_cookies(self):
        """Возвращает cookies из сохраненной сессии"""
        if self.session_data and isinstance(self.session_data, dict):
            cookies = self.session_data.get("cookies", [])
            return self._format_cookies(cookies)
        return None
    
    def _format_cookies(self, cookies):
        """Форматирует cookies в словарь для requests"""
        if not cookies:
            return {}
        
        if isinstance(cookies, list):
            return {cookie.get('name', ''): cookie.get('value', '') for cookie in cookies}
        return cookies
    
    def is_session_valid(self):
        """Проверяет, действительна ли текущая сессия"""
        cookies = self.get_cookies()
        if not cookies:
            return False
        
        try:
            headers = {
                "x-auth-version": "3",
                "Origin": "https://kaspi.kz",
                "Referer": "https://kaspi.kz/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
            }
            
            response = requests.get(
                "https://mc.shop.kaspi.kz/s/m",
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def save(self, cookies, email=None, password=None):
        """Сохраняет cookies, email и пароль в сессии"""
        self.session_data = {
            "cookies": cookies,
            "email": email,
            "password": password
        }
        self.last_login = timezone.now()
        
        if self.store:
            self.store.guid = self.session_data
            self.store.last_login = self.last_login
            self.store.save(update_fields=['guid', 'last_login'])
        
        return {
            "cookies": cookies,
            "email": email,
            "password": password
        }
    
    def is_session_expired(self, session_timeout=3600):
        """Проверяет, истекла ли сессия"""
        if not self.last_login:
            return True
        
        if isinstance(self.last_login, str):
            last_login_time = datetime.fromisoformat(self.last_login.replace('Z', '+00:00'))
        else:
            last_login_time = self.last_login
        
        if isinstance(last_login_time, datetime):
            if timezone.is_aware(last_login_time):
                now = timezone.now()
            else:
                now = datetime.now()
                last_login_time = timezone.make_aware(last_login_time)
        else:
            return True
        
        return (now - last_login_time).total_seconds() > session_timeout

