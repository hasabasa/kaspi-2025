# database.py
"""
Работа с базой данных для WAHA интеграции
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import asyncpg

from .models import WhatsAppTemplate, WAHASettings, WhatsAppMessageLog, WAHASessionInfo

logger = logging.getLogger(__name__)


class WAHA_Database:
    """Класс для работы с базой данных WAHA"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create_tables(self):
        """Создание таблиц для WAHA"""
        try:
            async with self.pool.acquire() as conn:
                # Таблица шаблонов WhatsApp сообщений
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_templates (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        store_id UUID REFERENCES kaspi_stores(id) ON DELETE CASCADE,
                        template_name VARCHAR(255) NOT NULL,
                        template_text TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Таблица настроек WAHA
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_settings (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        store_id UUID REFERENCES kaspi_stores(id) ON DELETE CASCADE,
                        waha_server_url VARCHAR(500) NOT NULL,
                        waha_session_name VARCHAR(100) DEFAULT 'kaspi-session',
                        is_enabled BOOLEAN DEFAULT TRUE,
                        webhook_url VARCHAR(500) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(store_id)
                    )
                """)
                
                # Таблица логов отправленных сообщений
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_messages_log (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        store_id UUID REFERENCES kaspi_stores(id) ON DELETE CASCADE,
                        order_id VARCHAR(255),
                        customer_phone VARCHAR(20) NOT NULL,
                        message_text TEXT NOT NULL,
                        template_id UUID REFERENCES whatsapp_templates(id),
                        status VARCHAR(50) DEFAULT 'pending',
                        waha_response JSONB,
                        sent_at TIMESTAMP DEFAULT NOW(),
                        delivered_at TIMESTAMP,
                        error_message TEXT
                    )
                """)
                
                # Таблица сессий WAHA
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS waha_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        store_id UUID REFERENCES kaspi_stores(id) ON DELETE CASCADE,
                        session_name VARCHAR(100) NOT NULL,
                        status VARCHAR(50) DEFAULT 'disconnected',
                        phone VARCHAR(20),
                        profile_name VARCHAR(255),
                        profile_picture_url VARCHAR(500),
                        is_connected BOOLEAN DEFAULT FALSE,
                        connected_at TIMESTAMP,
                        last_activity TIMESTAMP,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(store_id)
                    )
                """)
                
                # Индексы для оптимизации
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_whatsapp_templates_store_id 
                    ON whatsapp_templates(store_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_log_store_id 
                    ON whatsapp_messages_log(store_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_log_sent_at 
                    ON whatsapp_messages_log(sent_at)
                """)
                
                logger.info("Таблицы WAHA созданы успешно")
                
        except Exception as e:
            logger.error(f"Ошибка создания таблиц WAHA: {e}")
            raise
    
    # Методы для работы с шаблонами
    async def create_template(self, template: WhatsAppTemplate) -> UUID:
        """Создание шаблона"""
        async with self.pool.acquire() as conn:
            template_id = await conn.fetchval("""
                INSERT INTO whatsapp_templates (store_id, template_name, template_text, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, template.store_id, template.template_name, template.template_text, 
                template.is_active, template.created_at, template.updated_at)
            
            return template_id
    
    async def get_templates(self, store_id: UUID) -> List[WhatsAppTemplate]:
        """Получение всех шаблонов магазина"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, store_id, template_name, template_text, is_active, created_at, updated_at
                FROM whatsapp_templates
                WHERE store_id = $1
                ORDER BY created_at DESC
            """, store_id)
            
            templates = []
            for row in rows:
                template = WhatsAppTemplate(
                    id=row['id'],
                    store_id=row['store_id'],
                    template_name=row['template_name'],
                    template_text=row['template_text'],
                    is_active=row['is_active'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                templates.append(template)
            
            return templates
    
    async def get_template(self, template_id: UUID) -> Optional[WhatsAppTemplate]:
        """Получение шаблона по ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, store_id, template_name, template_text, is_active, created_at, updated_at
                FROM whatsapp_templates
                WHERE id = $1
            """, template_id)
            
            if not row:
                return None
            
            return WhatsAppTemplate(
                id=row['id'],
                store_id=row['store_id'],
                template_name=row['template_name'],
                template_text=row['template_text'],
                is_active=row['is_active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
    
    async def update_template(self, template_id: UUID, update_data: Dict[str, Any]) -> bool:
        """Обновление шаблона"""
        async with self.pool.acquire() as conn:
            # Формируем SET часть запроса
            set_parts = []
            params = []
            param_count = 1
            
            for key, value in update_data.items():
                set_parts.append(f"{key} = ${param_count}")
                params.append(value)
                param_count += 1
            
            params.append(template_id)
            
            query = f"""
                UPDATE whatsapp_templates 
                SET {', '.join(set_parts)}
                WHERE id = ${param_count}
            """
            
            result = await conn.execute(query, *params)
            return result == "UPDATE 1"
    
    async def delete_template(self, template_id: UUID) -> bool:
        """Удаление шаблона"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM whatsapp_templates WHERE id = $1
            """, template_id)
            return result == "DELETE 1"
    
    async def get_active_template(self, store_id: UUID) -> Optional[WhatsAppTemplate]:
        """Получение активного шаблона магазина"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, store_id, template_name, template_text, is_active, created_at, updated_at
                FROM whatsapp_templates
                WHERE store_id = $1 AND is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
            """, store_id)
            
            if not row:
                return None
            
            return WhatsAppTemplate(
                id=row['id'],
                store_id=row['store_id'],
                template_name=row['template_name'],
                template_text=row['template_text'],
                is_active=row['is_active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
    
    # Методы для работы с настройками WAHA
    async def create_or_update_settings(self, settings: WAHASettings) -> UUID:
        """Создание или обновление настроек WAHA"""
        async with self.pool.acquire() as conn:
            settings_id = await conn.fetchval("""
                INSERT INTO whatsapp_settings (store_id, waha_server_url, waha_session_name, is_enabled, webhook_url, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (store_id) DO UPDATE SET
                    waha_server_url = EXCLUDED.waha_server_url,
                    waha_session_name = EXCLUDED.waha_session_name,
                    is_enabled = EXCLUDED.is_enabled,
                    webhook_url = EXCLUDED.webhook_url,
                    updated_at = EXCLUDED.updated_at
                RETURNING id
            """, settings.store_id, settings.waha_server_url, settings.waha_session_name,
                settings.is_enabled, settings.webhook_url, settings.created_at, settings.updated_at)
            
            return settings_id
    
    async def get_settings(self, store_id: UUID) -> Optional[WAHASettings]:
        """Получение настроек WAHA магазина"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, store_id, waha_server_url, waha_session_name, is_enabled, webhook_url, created_at, updated_at
                FROM whatsapp_settings
                WHERE store_id = $1
            """, store_id)
            
            if not row:
                return None
            
            return WAHASettings(
                id=row['id'],
                store_id=row['store_id'],
                waha_server_url=row['waha_server_url'],
                waha_session_name=row['waha_session_name'],
                is_enabled=row['is_enabled'],
                webhook_url=row['webhook_url'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
    
    # Методы для работы с логами сообщений
    async def log_message(self, message_log: WhatsAppMessageLog) -> UUID:
        """Логирование отправленного сообщения"""
        async with self.pool.acquire() as conn:
            log_id = await conn.fetchval("""
                INSERT INTO whatsapp_messages_log 
                (store_id, order_id, customer_phone, message_text, template_id, status, waha_response, sent_at, delivered_at, error_message)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """, message_log.store_id, message_log.order_id, message_log.customer_phone,
                message_log.message_text, message_log.template_id, message_log.status,
                message_log.waha_response, message_log.sent_at, message_log.delivered_at,
                message_log.error_message)
            
            return log_id
    
    async def update_message_status(self, log_id: UUID, status: str, delivered_at: Optional[datetime] = None, error_message: Optional[str] = None):
        """Обновление статуса сообщения"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE whatsapp_messages_log 
                SET status = $1, delivered_at = $2, error_message = $3
                WHERE id = $4
            """, status, delivered_at, error_message, log_id)
    
    async def get_message_logs(self, store_id: UUID, limit: int = 100, offset: int = 0) -> List[WhatsAppMessageLog]:
        """Получение логов сообщений магазина"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, store_id, order_id, customer_phone, message_text, template_id, status, 
                       waha_response, sent_at, delivered_at, error_message
                FROM whatsapp_messages_log
                WHERE store_id = $1
                ORDER BY sent_at DESC
                LIMIT $2 OFFSET $3
            """, store_id, limit, offset)
            
            logs = []
            for row in rows:
                log = WhatsAppMessageLog(
                    id=row['id'],
                    store_id=row['store_id'],
                    order_id=row['order_id'],
                    customer_phone=row['customer_phone'],
                    message_text=row['message_text'],
                    template_id=row['template_id'],
                    status=row['status'],
                    waha_response=row['waha_response'],
                    sent_at=row['sent_at'],
                    delivered_at=row['delivered_at'],
                    error_message=row['error_message']
                )
                logs.append(log)
            
            return logs
    
    # Методы для работы с сессиями WAHA
    async def create_or_update_session(self, store_id: UUID, session_name: str, status: str, 
                                     phone: Optional[str] = None, profile_name: Optional[str] = None,
                                     profile_picture_url: Optional[str] = None, is_connected: bool = False,
                                     error_message: Optional[str] = None) -> UUID:
        """Создание или обновление сессии WAHA"""
        async with self.pool.acquire() as conn:
            session_id = await conn.fetchval("""
                INSERT INTO waha_sessions 
                (store_id, session_name, status, phone, profile_name, profile_picture_url, is_connected, 
                 connected_at, last_activity, error_message, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
                ON CONFLICT (store_id) DO UPDATE SET
                    session_name = EXCLUDED.session_name,
                    status = EXCLUDED.status,
                    phone = EXCLUDED.phone,
                    profile_name = EXCLUDED.profile_name,
                    profile_picture_url = EXCLUDED.profile_picture_url,
                    is_connected = EXCLUDED.is_connected,
                    connected_at = EXCLUDED.connected_at,
                    last_activity = EXCLUDED.last_activity,
                    error_message = EXCLUDED.error_message,
                    updated_at = NOW()
                RETURNING id
            """, store_id, session_name, status, phone, profile_name, profile_picture_url,
                is_connected, datetime.now() if is_connected else None, datetime.now(), error_message)
            
            return session_id
    
    async def get_session_info(self, store_id: UUID) -> Optional[WAHASessionInfo]:
        """Получение информации о сессии WAHA"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT session_name, status, phone, is_connected, created_at, last_activity
                FROM waha_sessions
                WHERE store_id = $1
            """, store_id)
            
            if not row:
                return None
            
            return WAHASessionInfo(
                session_name=row['session_name'],
                status=row['status'],
                phone=row['phone'],
                is_connected=row['is_connected'],
                created_at=row['created_at'],
                last_activity=row['last_activity']
            )
    
    async def update_session_status(self, store_id: UUID, status: str, is_connected: bool = False, 
                                  error_message: Optional[str] = None):
        """Обновление статуса сессии"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE waha_sessions 
                SET status = $1, is_connected = $2, error_message = $3, 
                    last_activity = NOW(), updated_at = NOW()
                WHERE store_id = $4
            """, status, is_connected, error_message, store_id)
    
    async def get_enabled_stores(self) -> List[UUID]:
        """Получение списка магазинов с включенными WAHA уведомлениями"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT store_id FROM whatsapp_settings WHERE is_enabled = TRUE
            """)
            return [row['store_id'] for row in rows]
