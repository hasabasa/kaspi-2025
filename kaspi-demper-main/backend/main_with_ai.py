# main_with_ai.py
"""
Модифицированный main.py с интеграцией AI-продажника
"""

import asyncio
import datetime
import json
import logging
import random
import re
import secrets
import time
import uuid
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client, Client
from contextlib import asynccontextmanager

# Импортируем оригинальные функции
from api_parser import create_preorder_from_product
from api_parser import (
    login_and_get_merchant_info,
    sync_store_api,
    parse_product_by_sku,
    sync_product,
    get_sells,
    handle_upload_preorder,
    fetch_preorders,
    generate_preorder_xlsx,
    process_preorders_for_excel,
    sms_login_start,
    sms_login_verify
)

# Импортируем AI интеграцию
from api_parser_with_ai import (
    get_sells_with_ai,
    initialize_ai_seller,
    cleanup_ai_seller,
    get_ai_seller_metrics,
    reset_ai_seller_metrics,
    trigger_ai_seller_for_delivered_order
)

from routes.products import router as products_router
from routes.kaspi import router as kaspi_router
from routes.admin import router as admin_router
from utils import set_supabase_client, has_active_subscription, has_existing_store
from db import create_pool

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при запуске
    logger.info("Запуск приложения с AI-продажником...")
    
    try:
        # Инициализация AI-продажника
        await initialize_ai_seller()
        logger.info("AI-продажник инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации AI-продажника: {e}")
    
    yield
    
    # Очистка при завершении
    logger.info("Завершение приложения...")
    
    try:
        # Очистка AI-продажника
        await cleanup_ai_seller()
        logger.info("AI-продажник очищен")
    except Exception as e:
        logger.error(f"Ошибка очистки AI-продажника: {e}")

app = FastAPI(lifespan=lifespan)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(kaspi_router, prefix="/kaspi", tags=["kaspi"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

# Инициализация базы данных
pool = None

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    global pool
    pool = await create_pool()
    logger.info("База данных подключена")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие завершения приложения"""
    if pool:
        await pool.close()
        logger.info("База данных отключена")

# Модифицированный эндпоинт для получения данных о продажах с AI-продажником
@app.get("/kaspi/get_sells_info/{shop_id}")
async def get_sells_info_with_ai(shop_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Получение информации о продажах с интеграцией AI-продажника
    """
    try:
        # Проверяем подписку
        if not await has_active_subscription(credentials.credentials):
            raise HTTPException(status_code=403, detail="Нет активной подписки")
        
        # Получаем данные с AI-продажником
        success, result = await get_sells_with_ai(shop_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=result)
        
        return {
            "success": True,
            "data": result,
            "ai_seller_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_sells_info_with_ai: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

# Новый эндпоинт для метрик AI-продажника
@app.get("/ai-seller/metrics")
async def get_ai_seller_metrics_endpoint(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Получение метрик AI-продажника
    """
    try:
        # Проверяем подписку
        if not await has_active_subscription(credentials.credentials):
            raise HTTPException(status_code=403, detail="Нет активной подписки")
        
        metrics = get_ai_seller_metrics()
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения метрик AI-продажника: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения метрик: {str(e)}")

# Эндпоинт для сброса метрик AI-продажника
@app.post("/ai-seller/reset-metrics")
async def reset_ai_seller_metrics_endpoint(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Сброс метрик AI-продажника
    """
    try:
        # Проверяем подписку
        if not await has_active_subscription(credentials.credentials):
            raise HTTPException(status_code=403, detail="Нет активной подписки")
        
        reset_ai_seller_metrics()
        return {
            "success": True,
            "message": "Метрики AI-продажника сброшены",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка сброса метрик AI-продажника: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сброса метрик: {str(e)}")

# Эндпоинт для триггера AI-продажника для доставленного заказа
@app.post("/ai-seller/trigger-delivered/{order_id}")
async def trigger_delivered_order(
    order_id: str, 
    order_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """
    Триггер AI-продажника для доставленного заказа
    """
    try:
        # Проверяем подписку
        if not await has_active_subscription(credentials.credentials):
            raise HTTPException(status_code=403, detail="Нет активной подписки")
        
        # Получаем shop_id из order_data или используем дефолтный
        shop_id = order_data.get('shop_id', 'default')
        
        # Триггерим AI-продажника
        success = await trigger_ai_seller_for_delivered_order(order_data, shop_id)
        
        if success:
            return {
                "success": True,
                "message": f"AI-продажник обработал доставку заказа {order_id}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"AI-продажник не смог обработать заказ {order_id}",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Ошибка триггера AI-продажника для заказа {order_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки заказа: {str(e)}")

# Эндпоинт для проверки статуса AI-продажника
@app.get("/ai-seller/status")
async def get_ai_seller_status(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Проверка статуса AI-продажника
    """
    try:
        # Проверяем подписку
        if not await has_active_subscription(credentials.credentials):
            raise HTTPException(status_code=403, detail="Нет активной подписки")
        
        metrics = get_ai_seller_metrics()
        is_enabled = metrics.get('enabled', False)
        
        return {
            "success": True,
            "status": "enabled" if is_enabled else "disabled",
            "enabled": is_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки статуса AI-продажника: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка проверки статуса: {str(e)}")

# Оригинальный эндпоинт (для обратной совместимости)
@app.get("/kaspi/get_sells_info_original/{shop_id}")
async def get_sells_info_original(shop_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Оригинальный эндпоинт без AI-продажника (для обратной совместимости)
    """
    try:
        # Проверяем подписку
        if not await has_active_subscription(credentials.credentials):
            raise HTTPException(status_code=403, detail="Нет активной подписки")
        
        # Получаем данные без AI-продажника
        success, result = await get_sells(shop_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=result)
        
        return {
            "success": True,
            "data": result,
            "ai_seller_enabled": False,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_sells_info_original: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

# Остальные эндпоинты остаются без изменений...
# (здесь должны быть все остальные эндпоинты из оригинального main.py)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
