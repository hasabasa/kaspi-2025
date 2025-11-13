#!/usr/bin/env python3
"""
Упрощенный тестовый бэкенд на основе kaspi-demper-main
Работает без базы данных для тестирования интеграции с фронтендом
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kaspi Demper API (Test)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=(
        r"^(https:\/\/([a-z0-9-]+\.)?(kaspi-price\.kz|mark-bot\.kz)"
        r"|http:\/\/localhost(:\d+)?)$"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class KaspiAuthRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    email: EmailStr = Field(..., description="Email для входа в Kaspi")
    password: str = Field(..., min_length=6, description="Пароль для входа в Kaspi")

class KaspiStore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: str
    merchant_id: str
    name: str
    api_key: str = "auto_generated_token"
    products_count: int = 0
    last_sync: Optional[str] = None
    is_active: bool = True

class SMSStartRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    phone: str = Field(..., description="Номер телефона для SMS-авторизации")

class SMSVerifyRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    session_id: str = Field(..., description="ID SMS-сессии из /sms/start")
    code: str = Field(..., description="Код из SMS")

# Временное хранилище (вместо базы данных)
stores_db = {}
sms_sessions = {}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True,
        "allowed_origins": [
            "http://localhost:8080",
            "http://localhost:3000",
            "http://localhost:5173"
        ]
    }

@app.get("/health/supabase")
async def health_check_supabase():
    return {
        "status": "healthy",
        "supabase": "mocked",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health/db")
async def health_check_db():
    return {
        "status": "healthy",
        "database": "mocked",
        "timestamp": datetime.now().isoformat()
    }

@app.options("/kaspi/stores")
async def options_kaspi_stores():
    return {"message": "CORS preflight handled"}

@app.post("/kaspi/auth")
async def authenticate_kaspi_store(auth_data: KaspiAuthRequest):
    try:
        logger.info(f"Попытка аутентификации для {auth_data.email}")
        
        # Симулируем проверку валидности email и пароля
        if "@" not in auth_data.email or len(auth_data.password) < 6:
            raise HTTPException(
                status_code=401, 
                detail="Неверные данные для входа в Kaspi.kz"
            )
        
        # Создаем мок данные магазина
        merchant_id = f"kaspi_{int(datetime.now().timestamp())}"
        shop_name = f"Магазин {auth_data.email.split('@')[0].title()}"
        
        # Проверяем, есть ли уже магазин у пользователя
        existing_store = None
        for store in stores_db.values():
            if store["user_id"] == auth_data.user_id:
                existing_store = store
                break
        
        if existing_store:
            # Обновляем существующий магазин
            existing_store.update({
                "merchant_id": merchant_id,
                "name": shop_name,
                "updated_at": datetime.now().isoformat(),
                "last_sync": None
            })
            
            logger.info(f"Магазин {shop_name} обновлен для пользователя {auth_data.user_id}")
            return {
                "success": True,
                "store_id": existing_store["id"],
                "name": existing_store["name"],
                "message": "Сессия магазина успешно обновлена",
                "api_key": existing_store["api_key"],
                "is_replaced": True
            }
        
        # Создаем новый магазин
        store_id = str(uuid.uuid4())
        new_store = {
            "id": store_id,
            "user_id": auth_data.user_id,
            "merchant_id": merchant_id,
            "name": shop_name,
            "api_key": f"kaspi_{uuid.uuid4().hex[:16]}",
            "products_count": 0,
            "last_sync": None,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        stores_db[store_id] = new_store
        
        logger.info(f"Магазин {shop_name} успешно подключен")
        return {
            "success": True,
            "store_id": store_id,
            "name": shop_name,
            "message": "Магазин успешно привязан к вашему аккаунту",
            "api_key": new_store["api_key"],
            "is_replaced": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при привязке магазина: {e}")
        raise HTTPException(
            status_code=500,
            detail="Непредвиденная ошибка при подключении к Kaspi"
        )

@app.get("/kaspi/stores")
async def get_user_stores(user_id: str):
    try:
        logger.info(f"Получение магазинов для пользователя: {user_id}")
        
        user_stores = [
            store for store in stores_db.values() 
            if store["user_id"] == user_id
        ]
        
        logger.info(f"Найдено {len(user_stores)} магазинов для пользователя {user_id}")
        return {"success": True, "stores": user_stores}
        
    except Exception as e:
        logger.error(f"Ошибка при получении магазинов: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении магазинов: {str(e)}"
        )

@app.post("/kaspi/stores/{store_id}/sync")
async def sync_store(store_id: str):
    try:
        if store_id not in stores_db:
            raise HTTPException(
                status_code=404,
                detail="Магазин не найден"
            )
        
        # Симулируем синхронизацию
        stores_db[store_id]["last_sync"] = datetime.now().isoformat()
        stores_db[store_id]["products_count"] = 42  # Мок данные
        
        logger.info(f"Синхронизация магазина {store_id} завершена")
        return {
            "success": True,
            "message": "Синхронизация завершена",
            "products_synced": 42,
            "last_sync": stores_db[store_id]["last_sync"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка синхронизации: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка синхронизации магазина"
        )

@app.post("/kaspi/auth/sms/start")
async def kaspi_sms_start(req: SMSStartRequest):
    """Шаг 1: отправляем номер в SMS-форму, возвращаем session_id"""
    try:
        logger.info(f"SMS авторизация начата для {req.phone}")
        
        session_id = str(uuid.uuid4())
        sms_sessions[session_id] = {
            "user_id": req.user_id,
            "phone": req.phone,
            "created_at": datetime.now().isoformat(),
            "verified": False
        }
        
        return {"session_id": session_id}
        
    except Exception as e:
        logger.error(f"Ошибка SMS старта: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при отправке SMS"
        )

@app.post("/kaspi/auth/sms/verify")
async def kaspi_sms_verify(req: SMSVerifyRequest):
    """Шаг 2: вводим код, получаем merchant_id, shop_name и сохраняем магазин"""
    try:
        logger.info(f"SMS верификация для сессии {req.session_id}")
        
        if req.session_id not in sms_sessions:
            raise HTTPException(
                status_code=404,
                detail="SMS сессия не найдена"
            )
        
        session = sms_sessions[req.session_id]
        
        # Простая проверка кода (в реальности здесь проверка с Kaspi)
        if req.code != "1234":  # Мок код для тестирования
            raise HTTPException(
                status_code=400,
                detail="Неверный код подтверждения"
            )
        
        # Создаем мок данные
        merchant_id = f"sms_kaspi_{int(datetime.now().timestamp())}"
        shop_name = f"SMS Магазин {session['phone'][-4:]}"
        
        # Проверяем существующий магазин
        existing_store = None
        for store in stores_db.values():
            if store["user_id"] == req.user_id:
                existing_store = store
                break
        
        if existing_store:
            # Обновляем существующий
            existing_store.update({
                "merchant_id": merchant_id,
                "name": shop_name,
                "updated_at": datetime.now().isoformat(),
                "last_sync": None
            })
            
            return {
                "success": True,
                "store_id": existing_store["id"],
                "message": "Сессия магазина успешно обновлена через SMS",
                "is_replaced": True
            }
        
        # Создаем новый магазин
        store_id = str(uuid.uuid4())
        new_store = {
            "id": store_id,
            "user_id": req.user_id,
            "merchant_id": merchant_id,
            "name": shop_name,
            "api_key": f"kaspi_sms_{uuid.uuid4().hex[:16]}",
            "products_count": 0,
            "last_sync": None,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        stores_db[store_id] = new_store
        
        # Отмечаем сессию как верифицированную
        session["verified"] = True
        
        return {
            "success": True,
            "store_id": store_id,
            "message": "Магазин успешно привязан через SMS",
            "is_replaced": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка SMS верификации: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при верификации SMS"
        )

# Эндпоинты для продуктов (мок)
@app.get("/kaspi/products/{store_id}")
async def get_store_products(store_id: str):
    """Получить продукты магазина"""
    if store_id not in stores_db:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    
    # Мок данные продуктов
    mock_products = [
        {
            "id": str(uuid.uuid4()),
            "name": "iPhone 15 Pro",
            "price": 450000,
            "sku": "IPHONE15PRO",
            "category": "Смартфоны",
            "bot_active": True,
            "min_profit": 10000
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Samsung Galaxy S24",
            "price": 380000,
            "sku": "GALAXY_S24",
            "category": "Смартфоны", 
            "bot_active": False,
            "min_profit": 8000
        }
    ]
    
    return {"success": True, "products": mock_products}

if __name__ == "__main__":
    print("🚀 Запуск тестового бэкенда Kaspi Demper на порту 8010...")
    print("📱 Используйте код '1234' для SMS верификации")
    print("✨ Любой email и пароль (>6 символов) подойдут для тестирования")
    
    uvicorn.run("test_kaspi_backend:app", host="0.0.0.0", port=8010, reload=True)
