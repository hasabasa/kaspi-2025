# models.py
"""
Pydantic модели для WAHA интеграции
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class WAHASessionConfig(BaseModel):
    """Конфигурация WAHA сессии"""
    webhook: str = Field(..., description="URL для webhook уведомлений")
    webhookEvents: List[str] = Field(
        default=["message", "messageStatus", "sessionStatus"],
        description="События для webhook"
    )
    browserArgs: Optional[List[str]] = Field(
        default=None,
        description="Аргументы браузера"
    )


class WAHASessionCreate(BaseModel):
    """Создание WAHA сессии"""
    name: str = Field(..., description="Имя сессии")
    config: Optional[WAHASessionConfig] = Field(None, description="Конфигурация сессии")


class WhatsAppTemplate(BaseModel):
    """Шаблон WhatsApp сообщения"""
    id: Optional[UUID] = Field(None, description="ID шаблона")
    store_id: UUID = Field(..., description="ID магазина")
    template_name: str = Field(..., min_length=1, max_length=255, description="Название шаблона")
    template_text: str = Field(..., min_length=1, description="Текст шаблона")
    is_active: bool = Field(True, description="Активен ли шаблон")
    created_at: Optional[datetime] = Field(None, description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    
    @field_validator('template_text')
    @classmethod
    def validate_template_text(cls, v):
        """Валидация текста шаблона"""
        if not v.strip():
            raise ValueError("Текст шаблона не может быть пустым")
        return v.strip()


class WhatsAppTemplateCreate(BaseModel):
    """Создание шаблона WhatsApp сообщения"""
    template_name: str = Field(..., min_length=1, max_length=255, description="Название шаблона")
    template_text: str = Field(..., min_length=1, description="Текст шаблона")


class WhatsAppTemplateUpdate(BaseModel):
    """Обновление шаблона WhatsApp сообщения"""
    template_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название шаблона")
    template_text: Optional[str] = Field(None, min_length=1, description="Текст шаблона")
    is_active: Optional[bool] = Field(None, description="Активен ли шаблон")


class WAHASettings(BaseModel):
    """Настройки WAHA"""
    id: Optional[UUID] = Field(None, description="ID настроек")
    store_id: UUID = Field(..., description="ID магазина")
    waha_server_url: str = Field(..., description="URL сервера WAHA")
    waha_session_name: str = Field("kaspi-session", description="Имя сессии WAHA")
    is_enabled: bool = Field(True, description="Включены ли уведомления")
    webhook_url: str = Field(..., description="URL для webhook")
    created_at: Optional[datetime] = Field(None, description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    
    @field_validator('waha_server_url')
    @classmethod
    def validate_waha_url(cls, v):
        """Валидация URL WAHA сервера"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v.rstrip('/')


class WAHASettingsCreate(BaseModel):
    """Создание настроек WAHA"""
    waha_server_url: str = Field(..., description="URL сервера WAHA")
    waha_session_name: str = Field("kaspi-session", description="Имя сессии WAHA")
    is_enabled: bool = Field(True, description="Включены ли уведомления")
    webhook_url: str = Field(..., description="URL для webhook")


class WhatsAppMessageLog(BaseModel):
    """Лог отправленных WhatsApp сообщений"""
    id: Optional[UUID] = Field(None, description="ID записи")
    store_id: UUID = Field(..., description="ID магазина")
    order_id: Optional[str] = Field(None, description="ID заказа")
    customer_phone: str = Field(..., description="Телефон покупателя")
    message_text: str = Field(..., description="Текст сообщения")
    template_id: Optional[UUID] = Field(None, description="ID шаблона")
    status: str = Field("pending", description="Статус сообщения")
    waha_response: Optional[Dict[str, Any]] = Field(None, description="Ответ WAHA")
    sent_at: Optional[datetime] = Field(None, description="Время отправки")
    delivered_at: Optional[datetime] = Field(None, description="Время доставки")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Валидация статуса"""
        allowed_statuses = ['pending', 'sent', 'delivered', 'failed', 'read']
        if v not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {allowed_statuses}")
        return v


class WhatsAppTestMessage(BaseModel):
    """Тестовое WhatsApp сообщение"""
    phone_number: str = Field(..., description="Номер телефона для теста")
    template_text: str = Field(..., description="Текст шаблона")
    sample_data: Dict[str, Any] = Field(..., description="Тестовые данные для подстановки")


class OrderData(BaseModel):
    """Данные заказа для WhatsApp уведомления"""
    customer_name: str = Field(..., description="Имя покупателя")
    customer_phone: str = Field(..., description="Телефон покупателя")
    order_id: str = Field(..., description="ID заказа")
    product_name: str = Field(..., description="Название товара")
    quantity: int = Field(..., description="Количество")
    total_amount: float = Field(..., description="Общая сумма")
    delivery_type: str = Field(..., description="Тип доставки")
    order_date: str = Field(..., description="Дата заказа")
    shop_name: str = Field(..., description="Название магазина")


class WAHAWebhookEvent(BaseModel):
    """Событие webhook от WAHA"""
    event: str = Field(..., description="Тип события")
    session: str = Field(..., description="Имя сессии")
    payload: Dict[str, Any] = Field(..., description="Данные события")
    timestamp: Optional[datetime] = Field(None, description="Время события")


class WAHAWebhookMessage(BaseModel):
    """Сообщение из webhook WAHA"""
    id: str = Field(..., description="ID сообщения")
    from_: str = Field(..., alias="from", description="От кого")
    to: str = Field(..., description="Кому")
    body: str = Field(..., description="Текст сообщения")
    timestamp: int = Field(..., description="Время сообщения")
    type: str = Field(..., description="Тип сообщения")
    chatId: str = Field(..., description="ID чата")


class WAHAWebhookMessageStatus(BaseModel):
    """Статус сообщения из webhook WAHA"""
    id: str = Field(..., description="ID сообщения")
    status: str = Field(..., description="Статус сообщения")
    timestamp: int = Field(..., description="Время статуса")


class WAHAWebhookSessionStatus(BaseModel):
    """Статус сессии из webhook WAHA"""
    session: str = Field(..., description="Имя сессии")
    status: str = Field(..., description="Статус сессии")
    timestamp: int = Field(..., description="Время статуса")


class WAHASessionStatus(BaseModel):
    """Статус WAHA сессии"""
    session: str = Field(..., description="Имя сессии")
    status: str = Field(..., description="Статус сессии")
    phone: Optional[str] = Field(None, description="Номер телефона")
    name: Optional[str] = Field(None, description="Имя профиля")
    profilePictureUrl: Optional[str] = Field(None, description="URL аватара")
    isConnected: bool = Field(..., description="Подключена ли сессия")


class WhatsAppSendResponse(BaseModel):
    """Ответ на отправку WhatsApp сообщения"""
    success: bool = Field(..., description="Успешность отправки")
    message_id: Optional[str] = Field(None, description="ID сообщения")
    error: Optional[str] = Field(None, description="Ошибка")
    waha_response: Optional[Dict[str, Any]] = Field(None, description="Ответ WAHA")


class WhatsAppTemplatePreview(BaseModel):
    """Предварительный просмотр шаблона"""
    template_text: str = Field(..., description="Текст шаблона")
    sample_data: Dict[str, Any] = Field(..., description="Тестовые данные")
    preview_text: str = Field(..., description="Текст с подстановкой")


class WAHASessionInfo(BaseModel):
    """Информация о WAHA сессии"""
    session_name: str = Field(..., description="Имя сессии")
    status: str = Field(..., description="Статус сессии")
    phone: Optional[str] = Field(None, description="Номер телефона")
    is_connected: bool = Field(..., description="Подключена ли сессия")
    created_at: datetime = Field(..., description="Время создания")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
