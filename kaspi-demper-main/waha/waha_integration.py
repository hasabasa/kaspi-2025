# waha_integration.py
"""
Инициализация и интеграция WAHA модуля с основным приложением
"""

import logging
import asyncio
from typing import Optional
import asyncpg

from .waha_client import WAHAClient, session_manager
from .template_manager import TemplateManager
from .message_sender import WhatsAppMessageSender
from .order_integration import OrderIntegration
from .database import WAHA_Database
from .routes import (
    template_manager, message_sender, order_integration, waha_db,
    router as waha_router
)

logger = logging.getLogger(__name__)


class WAHAManager:
    """Менеджер WAHA интеграции"""
    
    def __init__(self, db_pool: asyncpg.Pool, waha_server_url: str = "http://localhost:3000"):
        self.db_pool = db_pool
        self.waha_server_url = waha_server_url
        self.waha_client = WAHAClient(waha_server_url)
        self.waha_db = WAHA_Database(db_pool)
        self.template_manager = TemplateManager(self.waha_db)
        self.message_sender = WhatsAppMessageSender(
            self.waha_client, 
            self.template_manager, 
            self.waha_db
        )
        self.order_integration = OrderIntegration(
            self.message_sender, 
            self.waha_db
        )
        self._initialized = False
    
    async def initialize(self):
        """Инициализация WAHA модуля"""
        try:
            logger.info("Инициализация WAHA модуля...")
            
            # Создаем таблицы в базе данных
            await self.waha_db.create_tables()
            
            # Инициализируем глобальные переменные для роутов
            global template_manager, message_sender, order_integration, waha_db
            template_manager = self.template_manager
            message_sender = self.message_sender
            order_integration = self.order_integration
            waha_db = self.waha_db
            
            # Проверяем доступность WAHA сервера
            await self._check_waha_server()
            
            # Восстанавливаем активные сессии
            await self._restore_active_sessions()
            
            self._initialized = True
            logger.info("WAHA модуль инициализирован успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации WAHA модуля: {e}")
            raise
    
    async def _check_waha_server(self):
        """Проверка доступности WAHA сервера"""
        try:
            async with self.waha_client:
                sessions = await self.waha_client.get_sessions()
                logger.info(f"WAHA сервер доступен. Активных сессий: {len(sessions)}")
        except Exception as e:
            logger.warning(f"WAHA сервер недоступен: {e}")
            # Не прерываем инициализацию, просто логируем предупреждение
    
    async def _restore_active_sessions(self):
        """Восстановление активных сессий из базы данных"""
        try:
            # Получаем все магазины с включенными WAHA уведомлениями
            enabled_stores = await self.waha_db.get_enabled_stores()
            
            for store_id in enabled_stores:
                try:
                    # Получаем информацию о сессии
                    session_info = await self.waha_db.get_session_info(store_id)
                    
                    if session_info and session_info.is_connected:
                        # Восстанавливаем сессию в менеджере
                        session_manager.active_sessions[str(store_id)] = {
                            "session_name": session_info.session_name,
                            "status": session_info.status,
                            "created_at": session_info.created_at,
                            "last_activity": session_info.last_activity
                        }
                        
                        logger.info(f"Восстановлена сессия для магазина {store_id}")
                        
                except Exception as e:
                    logger.error(f"Ошибка восстановления сессии для магазина {store_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка восстановления активных сессий: {e}")
    
    async def create_store_session(self, store_id: str, store_name: str, webhook_url: str):
        """Создание сессии для магазина"""
        try:
            result = await session_manager.create_store_session(store_id, store_name, webhook_url)
            
            # Сохраняем информацию о сессии в БД
            await self.waha_db.create_or_update_session(
                store_id=store_id,
                session_name=f"kaspi-store-{store_id}",
                status="starting"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии для магазина {store_id}: {e}")
            raise
    
    async def process_orders_for_store(self, store_id: str, orders_data: list, shop_name: str = "Магазин"):
        """Обработка заказов для конкретного магазина"""
        try:
            results = await self.order_integration.process_new_orders(
                store_id, orders_data, shop_name
            )
            return results
            
        except Exception as e:
            logger.error(f"Ошибка обработки заказов для магазина {store_id}: {e}")
            raise
    
    async def get_store_statistics(self, store_id: str, days: int = 30):
        """Получение статистики для магазина"""
        try:
            stats = await self.message_sender.get_message_statistics(store_id, days)
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики для магазина {store_id}: {e}")
            raise
    
    async def shutdown(self):
        """Завершение работы WAHA модуля"""
        try:
            logger.info("Завершение работы WAHA модуля...")
            
            # Останавливаем все активные сессии
            for store_id in list(session_manager.active_sessions.keys()):
                try:
                    await session_manager.stop_session(store_id)
                except Exception as e:
                    logger.error(f"Ошибка остановки сессии для магазина {store_id}: {e}")
            
            # Закрываем соединение с WAHA клиентом
            if hasattr(self.waha_client, 'session') and self.waha_client.session:
                await self.waha_client.session.close()
            
            logger.info("WAHA модуль завершил работу")
            
        except Exception as e:
            logger.error(f"Ошибка завершения работы WAHA модуля: {e}")


# Глобальный экземпляр менеджера
waha_manager: Optional[WAHAManager] = None


async def initialize_waha(db_pool: asyncpg.Pool, waha_server_url: str = "http://localhost:3000") -> WAHAManager:
    """Инициализация WAHA модуля"""
    global waha_manager
    
    if waha_manager is None:
        waha_manager = WAHAManager(db_pool, waha_server_url)
        await waha_manager.initialize()
    
    return waha_manager


async def shutdown_waha():
    """Завершение работы WAHA модуля"""
    global waha_manager
    
    if waha_manager:
        await waha_manager.shutdown()
        waha_manager = None


def get_waha_manager() -> WAHAManager:
    """Получение экземпляра WAHA менеджера"""
    if not waha_manager:
        raise RuntimeError("WAHA модуль не инициализирован")
    return waha_manager


def get_waha_router():
    """Получение роутера WAHA"""
    return waha_router
