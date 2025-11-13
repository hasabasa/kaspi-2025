# waha_client.py
"""
WAHA API клиент для работы с WhatsApp через связанные устройства
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class WAHAClient:
    """Клиент для работы с WAHA API"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполнение HTTP запроса к WAHA API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                result = await response.json()
                
                if response.status >= 400:
                    logger.error(f"WAHA API error: {response.status} - {result}")
                    raise Exception(f"WAHA API error: {result.get('message', 'Unknown error')}")
                
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"WAHA API connection error: {e}")
            raise Exception(f"WAHA API connection error: {str(e)}")
    
    async def start_session(self, session_name: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Создание новой WAHA сессии
        
        Args:
            session_name: Имя сессии
            config: Конфигурация сессии (webhook, phone и т.д.)
        """
        data = {"name": session_name}
        if config:
            data["config"] = config
        
        return await self._make_request("POST", "/api/sessions/start", data)
    
    async def stop_session(self, session_name: str) -> Dict[str, Any]:
        """Остановка WAHA сессии"""
        return await self._make_request("POST", f"/api/sessions/{session_name}/stop")
    
    async def restart_session(self, session_name: str) -> Dict[str, Any]:
        """Перезапуск WAHA сессии"""
        return await self._make_request("POST", f"/api/sessions/{session_name}/restart")
    
    async def get_session_status(self, session_name: str) -> Dict[str, Any]:
        """Получение статуса сессии"""
        return await self._make_request("GET", f"/api/sessions/{session_name}/status")
    
    async def get_sessions(self) -> List[Dict[str, Any]]:
        """Получение списка всех сессий"""
        result = await self._make_request("GET", "/api/sessions")
        return result.get("sessions", [])
    
    async def send_text_message(self, session_name: str, chat_id: str, text: str) -> Dict[str, Any]:
        """
        Отправка текстового сообщения
        
        Args:
            session_name: Имя сессии
            chat_id: ID чата (формат: 7XXXXXXXXXX@c.us)
            text: Текст сообщения
        """
        data = {
            "session": session_name,
            "chatId": chat_id,
            "text": text
        }
        return await self._make_request("POST", "/api/sendText", data)
    
    async def send_image_message(self, session_name: str, chat_id: str, image_url: str, caption: str = "") -> Dict[str, Any]:
        """Отправка сообщения с изображением"""
        data = {
            "session": session_name,
            "chatId": chat_id,
            "image": image_url,
            "caption": caption
        }
        return await self._make_request("POST", "/api/sendImage", data)
    
    async def get_chats(self, session_name: str) -> List[Dict[str, Any]]:
        """Получение списка чатов"""
        result = await self._make_request("GET", f"/api/{session_name}/chats")
        return result.get("chats", [])
    
    async def get_chat_messages(self, session_name: str, chat_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение сообщений чата"""
        result = await self._make_request("GET", f"/api/{session_name}/chats/{chat_id}/messages", {"limit": limit})
        return result.get("messages", [])
    
    async def get_profile_info(self, session_name: str) -> Dict[str, Any]:
        """Получение информации о профиле"""
        return await self._make_request("GET", f"/api/{session_name}/profile")
    
    async def set_profile_name(self, session_name: str, name: str) -> Dict[str, Any]:
        """Установка имени профиля"""
        data = {"name": name}
        return await self._make_request("POST", f"/api/{session_name}/profile/name", data)
    
    async def set_profile_status(self, session_name: str, status: str) -> Dict[str, Any]:
        """Установка статуса профиля"""
        data = {"status": status}
        return await self._make_request("POST", f"/api/{session_name}/profile/status", data)
    
    async def check_phone_number(self, session_name: str, phone_number: str) -> Dict[str, Any]:
        """Проверка существования номера телефона в WhatsApp"""
        data = {"phone": phone_number}
        return await self._make_request("POST", f"/api/{session_name}/check", data)
    
    async def get_qr_code(self, session_name: str) -> str:
        """Получение QR-кода для подключения (если нужно)"""
        result = await self._make_request("GET", f"/api/{session_name}/auth/qr")
        return result.get("qr", "")
    
    async def logout_session(self, session_name: str) -> Dict[str, Any]:
        """Выход из сессии"""
        return await self._make_request("POST", f"/api/{session_name}/auth/logout")


class WAHASessionManager:
    """Менеджер сессий WAHA"""
    
    def __init__(self, waha_client: WAHAClient):
        self.waha_client = waha_client
        self.active_sessions = {}
    
    async def create_store_session(self, store_id: str, store_name: str, webhook_url: str) -> Dict[str, Any]:
        """
        Создание сессии для магазина через связанные устройства
        
        Args:
            store_id: ID магазина
            store_name: Название магазина
            webhook_url: URL для webhook уведомлений
        """
        session_name = f"kaspi-store-{store_id}"
        
        # Конфигурация для подключения через связанные устройства
        config = {
            "webhook": webhook_url,
            "webhookEvents": ["message", "messageStatus", "sessionStatus"],
            "browserArgs": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu"
            ]
        }
        
        try:
            # Создаем сессию
            result = await self.waha_client.start_session(session_name, config)
            
            # Сохраняем информацию о сессии
            self.active_sessions[store_id] = {
                "session_name": session_name,
                "status": "starting",
                "created_at": datetime.now(),
                "webhook_url": webhook_url
            }
            
            logger.info(f"WAHA сессия создана для магазина {store_id}: {session_name}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка создания WAHA сессии для магазина {store_id}: {e}")
            raise
    
    async def get_session_status(self, store_id: str) -> Dict[str, Any]:
        """Получение статуса сессии магазина"""
        if store_id not in self.active_sessions:
            return {"status": "not_found", "message": "Сессия не найдена"}
        
        session_name = self.active_sessions[store_id]["session_name"]
        
        try:
            status = await self.waha_client.get_session_status(session_name)
            self.active_sessions[store_id]["status"] = status.get("status", "unknown")
            return status
        except Exception as e:
            logger.error(f"Ошибка получения статуса сессии для магазина {store_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def restart_session(self, store_id: str) -> Dict[str, Any]:
        """Перезапуск сессии магазина"""
        if store_id not in self.active_sessions:
            raise Exception("Сессия не найдена")
        
        session_name = self.active_sessions[store_id]["session_name"]
        
        try:
            result = await self.waha_client.restart_session(session_name)
            logger.info(f"WAHA сессия перезапущена для магазина {store_id}")
            return result
        except Exception as e:
            logger.error(f"Ошибка перезапуска сессии для магазина {store_id}: {e}")
            raise
    
    async def stop_session(self, store_id: str) -> Dict[str, Any]:
        """Остановка сессии магазина"""
        if store_id not in self.active_sessions:
            raise Exception("Сессия не найдена")
        
        session_name = self.active_sessions[store_id]["session_name"]
        
        try:
            result = await self.waha_client.stop_session(session_name)
            del self.active_sessions[store_id]
            logger.info(f"WAHA сессия остановлена для магазина {store_id}")
            return result
        except Exception as e:
            logger.error(f"Ошибка остановки сессии для магазина {store_id}: {e}")
            raise
    
    async def send_message(self, store_id: str, phone_number: str, message: str) -> Dict[str, Any]:
        """Отправка сообщения через сессию магазина"""
        if store_id not in self.active_sessions:
            raise Exception("Сессия не найдена")
        
        session_name = self.active_sessions[store_id]["session_name"]
        
        # Форматируем номер телефона для WhatsApp
        chat_id = self._format_phone_number(phone_number)
        
        try:
            result = await self.waha_client.send_text_message(session_name, chat_id, message)
            logger.info(f"Сообщение отправлено для магазина {store_id} на номер {phone_number}")
            return result
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения для магазина {store_id}: {e}")
            raise
    
    def _format_phone_number(self, phone_number: str) -> str:
        """Форматирование номера телефона для WhatsApp"""
        # Удаляем все символы кроме цифр
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        # Добавляем код страны если нужно
        if not clean_phone.startswith('7'):
            clean_phone = '7' + clean_phone
        
        return f"{clean_phone}@c.us"
    
    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Получение всех активных сессий"""
        try:
            sessions = await self.waha_client.get_sessions()
            return sessions
        except Exception as e:
            logger.error(f"Ошибка получения списка сессий: {e}")
            return []


# Глобальный экземпляр клиента
waha_client = WAHAClient()
session_manager = WAHASessionManager(waha_client)
