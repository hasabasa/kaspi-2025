# routes.py
"""
API маршруты для WAHA интеграции
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .waha_client import waha_client, session_manager
from .template_manager import TemplateManager
from .message_sender import WhatsAppMessageSender
from .order_integration import OrderIntegration
from .database import WAHA_Database
from .models import (
    WhatsAppTemplateCreate, WhatsAppTemplateUpdate, WAHASettingsCreate,
    WhatsAppTestMessage, OrderData, WhatsAppSendResponse
)

logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter(prefix="/waha", tags=["WAHA Integration"])

# Глобальные экземпляры (будут инициализированы в main.py)
template_manager: Optional[TemplateManager] = None
message_sender: Optional[WhatsAppMessageSender] = None
order_integration: Optional[OrderIntegration] = None
waha_db: Optional[WAHA_Database] = None


def get_template_manager() -> TemplateManager:
    """Получение экземпляра TemplateManager"""
    if not template_manager:
        raise HTTPException(status_code=500, detail="TemplateManager не инициализирован")
    return template_manager


def get_message_sender() -> WhatsAppMessageSender:
    """Получение экземпляра WhatsAppMessageSender"""
    if not message_sender:
        raise HTTPException(status_code=500, detail="WhatsAppMessageSender не инициализирован")
    return message_sender


def get_order_integration() -> OrderIntegration:
    """Получение экземпляра OrderIntegration"""
    if not order_integration:
        raise HTTPException(status_code=500, detail="OrderIntegration не инициализирован")
    return order_integration


def get_waha_db() -> WAHA_Database:
    """Получение экземпляра WAHA_Database"""
    if not waha_db:
        raise HTTPException(status_code=500, detail="WAHA_Database не инициализирован")
    return waha_db


# ==================== УПРАВЛЕНИЕ СЕССИЯМИ ====================

@router.post("/sessions/connect/{store_id}")
async def connect_whatsapp_session(store_id: UUID, webhook_url: str):
    """Подключение WhatsApp сессии для магазина"""
    try:
        # Создаем сессию для магазина
        result = await session_manager.create_store_session(
            str(store_id),
            f"Магазин {store_id}",
            webhook_url
        )
        
        # Сохраняем информацию о сессии в БД
        db = get_waha_db()
        await db.create_or_update_session(
            store_id=store_id,
            session_name=f"kaspi-store-{store_id}",
            status="starting"
        )
        
        return {
            "success": True,
            "message": "Сессия создана успешно",
            "session_name": f"kaspi-store-{store_id}",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка подключения сессии для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/status/{store_id}")
async def get_session_status(store_id: UUID):
    """Получение статуса WAHA сессии"""
    try:
        status = await session_manager.get_session_status(str(store_id))
        
        # Получаем дополнительную информацию из БД
        db = get_waha_db()
        session_info = await db.get_session_info(store_id)
        
        return {
            "success": True,
            "status": status,
            "session_info": session_info.dict() if session_info else None
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса сессии для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/restart/{store_id}")
async def restart_session(store_id: UUID):
    """Перезапуск WAHA сессии"""
    try:
        result = await session_manager.restart_session(str(store_id))
        
        # Обновляем статус в БД
        db = get_waha_db()
        await db.update_session_status(store_id, "restarting")
        
        return {
            "success": True,
            "message": "Сессия перезапущена",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка перезапуска сессии для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/stop/{store_id}")
async def stop_session(store_id: UUID):
    """Остановка WAHA сессии"""
    try:
        result = await session_manager.stop_session(str(store_id))
        
        # Обновляем статус в БД
        db = get_waha_db()
        await db.update_session_status(store_id, "stopped", False)
        
        return {
            "success": True,
            "message": "Сессия остановлена",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка остановки сессии для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== УПРАВЛЕНИЕ ШАБЛОНАМИ ====================

@router.post("/templates/{store_id}")
async def create_template(
    store_id: UUID, 
    template_data: WhatsAppTemplateCreate,
    tm: TemplateManager = Depends(get_template_manager)
):
    """Создание нового шаблона сообщения"""
    try:
        template = await tm.create_template(store_id, template_data)
        
        return {
            "success": True,
            "message": "Шаблон создан успешно",
            "template": template.dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания шаблона для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{store_id}")
async def get_templates(
    store_id: UUID,
    tm: TemplateManager = Depends(get_template_manager)
):
    """Получение всех шаблонов магазина"""
    try:
        templates = await tm.get_templates(store_id)
        
        return {
            "success": True,
            "templates": [template.dict() for template in templates]
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения шаблонов для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/template/{template_id}")
async def get_template(
    template_id: UUID,
    tm: TemplateManager = Depends(get_template_manager)
):
    """Получение шаблона по ID"""
    try:
        template = await tm.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Шаблон не найден")
        
        return {
            "success": True,
            "template": template.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения шаблона {template_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(
    template_id: UUID,
    template_data: WhatsAppTemplateUpdate,
    tm: TemplateManager = Depends(get_template_manager)
):
    """Обновление шаблона"""
    try:
        template = await tm.update_template(template_id, template_data)
        
        return {
            "success": True,
            "message": "Шаблон обновлен успешно",
            "template": template.dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления шаблона {template_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: UUID,
    tm: TemplateManager = Depends(get_template_manager)
):
    """Удаление шаблона"""
    try:
        result = await tm.delete_template(template_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Шаблон не найден")
        
        return {
            "success": True,
            "message": "Шаблон удален успешно"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления шаблона {template_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/preview")
async def preview_template(
    template_text: str,
    sample_data: Dict[str, Any],
    tm: TemplateManager = Depends(get_template_manager)
):
    """Предварительный просмотр шаблона"""
    try:
        preview = tm.preview_template(template_text, sample_data)
        
        return {
            "success": True,
            "preview": preview.dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка предварительного просмотра шаблона: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/variables")
async def get_available_variables(tm: TemplateManager = Depends(get_template_manager)):
    """Получение списка доступных переменных"""
    try:
        variables = tm.get_available_variables()
        
        return {
            "success": True,
            "variables": variables
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения переменных: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== НАСТРОЙКИ WAHA ====================

@router.post("/settings/{store_id}")
async def create_or_update_settings(
    store_id: UUID,
    settings_data: WAHASettingsCreate,
    db: WAHA_Database = Depends(get_waha_db)
):
    """Создание или обновление настроек WAHA"""
    try:
        from .models import WAHASettings
        
        settings = WAHASettings(
            store_id=store_id,
            waha_server_url=settings_data.waha_server_url,
            waha_session_name=settings_data.waha_session_name,
            is_enabled=settings_data.is_enabled,
            webhook_url=settings_data.webhook_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        settings_id = await db.create_or_update_settings(settings)
        
        return {
            "success": True,
            "message": "Настройки сохранены успешно",
            "settings_id": str(settings_id)
        }
        
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{store_id}")
async def get_settings(
    store_id: UUID,
    db: WAHA_Database = Depends(get_waha_db)
):
    """Получение настроек WAHA"""
    try:
        settings = await db.get_settings(store_id)
        
        if not settings:
            return {
                "success": True,
                "settings": None,
                "message": "Настройки не найдены"
            }
        
        return {
            "success": True,
            "settings": settings.dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения настроек для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ОТПРАВКА СООБЩЕНИЙ ====================

@router.post("/send-test/{store_id}")
async def send_test_message(
    store_id: UUID,
    test_data: WhatsAppTestMessage,
    ms: WhatsAppMessageSender = Depends(get_message_sender)
):
    """Отправка тестового сообщения"""
    try:
        result = await ms.send_test_message(
            store_id,
            test_data.phone_number,
            test_data.template_text,
            test_data.sample_data
        )
        
        return {
            "success": result.success,
            "message_id": result.message_id,
            "error": result.error,
            "waha_response": result.waha_response
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки тестового сообщения для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-phone/{store_id}")
async def check_phone_number(
    store_id: UUID,
    phone_number: str,
    ms: WhatsAppMessageSender = Depends(get_message_sender)
):
    """Проверка существования номера телефона в WhatsApp"""
    try:
        result = await ms.check_phone_number(store_id, phone_number)
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка проверки номера телефона для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBHOOK ====================

@router.post("/webhook")
async def handle_webhook(
    webhook_data: Dict[str, Any],
    oi: OrderIntegration = Depends(get_order_integration)
):
    """Обработка webhook событий от WAHA"""
    try:
        result = await oi.handle_webhook_event(webhook_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== СТАТИСТИКА ====================

@router.get("/statistics/{store_id}")
async def get_statistics(
    store_id: UUID,
    days: int = 30,
    ms: WhatsAppMessageSender = Depends(get_message_sender)
):
    """Получение статистики отправленных сообщений"""
    try:
        stats = await ms.get_message_statistics(store_id, days)
        
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{store_id}")
async def get_message_logs(
    store_id: UUID,
    limit: int = 100,
    offset: int = 0,
    db: WAHA_Database = Depends(get_waha_db)
):
    """Получение логов отправленных сообщений"""
    try:
        logs = await db.get_message_logs(store_id, limit, offset)
        
        return {
            "success": True,
            "logs": [log.dict() for log in logs],
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения логов для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ИНТЕГРАЦИЯ С ЗАКАЗАМИ ====================

@router.post("/process-orders/{store_id}")
async def process_orders(
    store_id: UUID,
    orders_data: List[Dict[str, Any]],
    shop_name: str = "Магазин",
    oi: OrderIntegration = Depends(get_order_integration)
):
    """Обработка заказов и отправка уведомлений"""
    try:
        results = await oi.process_new_orders(store_id, orders_data, shop_name)
        
        return {
            "success": True,
            "processed_orders": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка обработки заказов для магазина {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== УТИЛИТЫ ====================

@router.get("/health")
async def health_check():
    """Проверка состояния WAHA интеграции"""
    try:
        # Проверяем доступность WAHA сервера
        async with waha_client:
            sessions = await waha_client.get_sessions()
        
        return {
            "success": True,
            "status": "healthy",
            "waha_sessions": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки состояния WAHA: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
