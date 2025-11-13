# nohup uvicorn main:app --reload &
# main.py fast api backend

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
from routes.products import router as products_router
from routes.kaspi import router as kaspi_router
from routes.admin import router as admin_router
from utils import set_supabase_client, has_existing_store
from db import create_pool
from config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router, prefix="/api/v1")
app.include_router(kaspi_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")

@app.get("/health/supabase")
async def health_check_supabase():
    try:
        from utils import get_supabase_client
        supabase = get_supabase_client()
        
        result = supabase.table("profiles").select("count", count="exact").limit(1).execute()
        
        return {
            "status": "healthy",
            "supabase": "connected",
            "profiles_count": result.count if hasattr(result, 'count') else "unknown",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Supabase health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "supabase": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True,
        "allowed_origins_regex": settings.CORS_ALLOWED_ORIGINS,
        "allowed_origins": [
            "http://localhost:*",
            "http://127.0.0.1:*"
        ]
    }


@app.get("/health/db")
async def health_check_db():
    try:
        # Проверяем подключение к Supabase
        from utils import get_supabase_client
        supabase = get_supabase_client()
        
        # Выполняем простой запрос для проверки соединения
        result = supabase.table("kaspi_stores").select("count", count="exact").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "mode": "supabase",
            "stores_count": result.count if hasattr(result, 'count') else "unknown",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.options("/kaspi/stores")
async def options_kaspi_stores():
    return {"message": "CORS preflight handled"}

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.on_event("startup")
async def startup_event():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    set_supabase_client(supabase)
    logging.info("Supabase client initialized")


print('Starting FastAPI application...')
# Настройка логгера
logging.basicConfig(level=logging.INFO)

logging.getLogger("postgrest").setLevel(logging.WARNING)

# Если используются httpx / urllib3 — тоже понизить им уровень
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Отключаем HTTP-логи Supabase/HTTPX в основном логе
for lib in ("supabase", "httpx", "httpcore", "urllib3", "postgrest", "gotrue"):
    lg = logging.getLogger(lib)
    lg.setLevel(logging.WARNING)
    lg.propagate = False

logger = logging.getLogger(__name__)

# Модели данных
class KaspiAuthRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    email: EmailStr = Field(..., description="Email для входа в Kaspi")
    password: str = Field(..., min_length=6, description="Пароль для входа в Kaspi")


class KaspiStore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: str  # Это обязательное поле для привязки к аккаунту
    merchant_id: str
    name: str
    api_key: str = "auto_generated_token"
    products_count: int = 0
    last_sync: Optional[str] = None
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "38269a19-dfc3-40c5-a7b7-e28489ade1b6",
                "created_at": "2025-06-24T19:39:24.963775+00:00",
                "updated_at": "2025-06-24T19:39:24.963775+00:00",
                "user_id": "7af6685a-812f-4525-ba67-6157097f43c3",
                "merchant_id": "kaspi_1750793959893",
                "name": "Магазин kaspidemping",
                "api_key": "auto_generated_token",
                "products_count": 0,
                "last_sync": "2025-06-24T19:39:19.893+00:00",
                "is_active": True
            }
        }


@app.post("/kaspi/auth")
async def authenticate_kaspi_store(auth_data: KaspiAuthRequest):
    try:
        
        # 1. Аутентификация в Kaspi
        cookie_jar, merchant_uid, shop_name, guid = await login_and_get_merchant_info(
            auth_data.email,
            auth_data.password,
            auth_data.user_id
        )

        if not merchant_uid:
            raise HTTPException(status_code=401, detail="Ошибка аутентификации в Kaspi")

        # 2. Проверяем, привязан ли уже такой магазин
        pool = await create_pool()
        async with pool.acquire() as conn:
            existing = await conn.fetch(
                """
                SELECT *
                FROM kaspi_stores
                WHERE user_id = $1 AND merchant_id = $2
                """,
                auth_data.user_id, merchant_uid
            )

        if existing:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE kaspi_stores
                    SET guid = $1, name = $2, updated_at = $3, last_sync = NULL
                    WHERE user_id = $4 AND merchant_id = $5
                    """,
                    guid, shop_name, datetime.now().isoformat(), auth_data.user_id, merchant_uid
                )
                
                # fetch updated store
                updated_store = await conn.fetchrow(
                    """
                    SELECT * FROM kaspi_stores
                    WHERE user_id = $1 AND merchant_id = $2
                    """,
                    auth_data.user_id, merchant_uid
                )

            return {
                "success": True,
                "store_id": updated_store["id"],
                "name": updated_store["name"],
                "message": "Сессия магазина успешно обновлена",
                "api_key": updated_store["api_key"],
                "is_replaced": True
            }

        # 3. Если магазина нет — создаём новую запись
        store_data = {
            "user_id": auth_data.user_id,
            "merchant_id": merchant_uid,
            "name": shop_name,
            "api_key": f"kaspi_{secrets.token_urlsafe(16)}",
            "guid": guid
        }
        
        async with pool.acquire() as conn:
            new_store = await conn.fetchrow(
                """
                INSERT INTO kaspi_stores (user_id, merchant_id, name, api_key, guid)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                store_data["user_id"], store_data["merchant_id"], store_data["name"],
                store_data["api_key"], store_data["guid"]
            )

        if not new_store:
            raise HTTPException(
                status_code=400,
                detail="Ошибка сохранения магазина"
            )

        return {
            "success": True,
            "store_id": new_store["id"],
            "name": new_store["name"],
            "message": "Магазин успешно привязан к вашему аккаунту",
            "api_key": store_data["api_key"],
            "is_replaced": False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при привязке/обновлении магазина: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Непредвиденная ошибка при подключении к Kaspi"
        )


@app.get("/kaspi/stores")
async def get_user_stores(user_id: str):
    try:
        logger.info(f"Fetching stores for user: {user_id}")
        
        from db import create_pool
        pool = await create_pool()
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id,
                       user_id,
                       merchant_id,
                       name,
                       api_key,
                       products_count,
                       last_sync,
                       is_active,
                       created_at,
                       updated_at
                FROM kaspi_stores
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                user_id
            )
        
        if not rows:
            logger.info(f"No stores found for user: {user_id}")
            return {"success": True, "stores": []}
        
        stores = [dict(r) for r in rows]
        logger.info(f"Successfully fetched {len(stores)} stores for user {user_id}")
        
        return {"success": True, "stores": stores}
        
    except Exception as e:
        logger.error(f"Error fetching stores for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stores: {str(e)}"
        )


@app.post("/kaspi/stores/{store_id}/sync")
async def sync_store(store_id: str):
    try:
        return await sync_store_api(store_id)
    except HTTPException as http_exc:
        logging.error(f"❌ Ошибка синхронизации: {http_exc.detail}", exc_info=True)
        raise http_exc
    except Exception as e:
        if hasattr(e, 'status_code') and e.status_code == 429:
            logging.warning(f"⚠️ Rate limit hit during sync: {e}")
            raise HTTPException(
                status_code=429,
                detail="Слишком много запросов к Kaspi. Пожалуйста, подождите немного и попробуйте снова."
            )
        
        logging.error(f"❌ Необработанная ошибка: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Ошибка синхронизации магазина"
        )

def get_kaspi_reviews_all(url: str, limit: int = 200, delay: float = 0.3) -> list:
    match = re.search(r'/product/(\d+)', url) or re.search(r'/p/[^/]*-(\d+)', url)
    if not match:
        raise ValueError("Не удалось извлечь product_id из ссылки")

    product_id = match.group(1)
    all_reviews = []
    page = 0

    while True:
        reviews_url = f"https://kaspi.kz/yml/review-view/api/v1/reviews/product/{product_id}"
        params = {
            "filter": "COMMENT",
            "sort": "POPULARITY",
            "limit": limit,
            "withAgg": "true",
        }
        if page > 0:
            params["page"] = page

        headers = {
            "accept": "application/json, text/*",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": f"https://kaspi.kz/shop/p/product-{product_id}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
        }

        response = requests.get(reviews_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        items = data.get("data", [])
        if not items:
            break

        all_reviews.extend(items)
        print(f"📄 Загружено отзывов: {len(all_reviews)}")
        page += 1
        time.sleep(delay)  # чтобы не спамить

    return all_reviews


def analyze_reviews_mapped(reviews: list, product_name: str = "Товар") -> dict:
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    three_months_ago = now - timedelta(days=90)
    six_months_ago = now - timedelta(days=180)
    one_year_ago = now - timedelta(days=365)

    def parse_date(date_str: str) -> datetime:
        return datetime.strptime(date_str, "%d.%m.%Y")

    total = len(reviews)

    # Группировка по времени
    def filter_by_range(min_date): return [r for r in reviews if parse_date(r["date"]) >= min_date]

    def est_sales(count): return count * 8

    stats = {
        "product_name": product_name,
        "total_reviews": total,
        "estimated_sales": est_sales(total),
        "periods": {
            "1m": {
                "reviews": len(filter_by_range(one_month_ago)),
                "estimated_sales": est_sales(len(filter_by_range(one_month_ago)))
            },
            "3m": {
                "reviews": len(filter_by_range(three_months_ago)),
                "estimated_sales": est_sales(len(filter_by_range(three_months_ago)))
            },
            "6m": {
                "reviews": len(filter_by_range(six_months_ago)),
                "estimated_sales": est_sales(len(filter_by_range(six_months_ago)))
            },
            "1y": {
                "reviews": len(filter_by_range(one_year_ago)),
                "estimated_sales": est_sales(len(filter_by_range(one_year_ago)))
            }
        }
    }

    return stats


class ReviewRequest(BaseModel):
    product_url: str


def extract_product_name(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        heading = soup.find("h1", class_="item__heading")
        return heading.text.strip() if heading else "Неизвестный товар"
    except Exception as e:
        logger.warning(f"❗ Не удалось спарсить имя товара: {e}")
        return "Неизвестный товар"


@app.post("/kaspi/reviews")
def analyze_reviews_from_body(payload: ReviewRequest):
    try:
        reviews = get_kaspi_reviews_all(payload.product_url)

        product_name = extract_product_name(payload.product_url)

        result = analyze_reviews_mapped(reviews, product_name)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Ошибка при получении магазинов: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении списка магазинов"
        )


class ProductRequest(BaseModel):
    sku: str


@app.post("/kaspi/offers_by_product")
def kaspi_offers_by_products(payload: ProductRequest):
    try:
        offers = parse_product_by_sku(payload.sku)

        return {
            "success": True,
            "data": offers
        }
    except Exception as e:
        logger.error(f"Ошибка при получении офферов: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении офферов"
        )


class PriceUpdateRequest(BaseModel):
    product_id: str
    price: Decimal = Field(..., description="Новая цена для обновления товара")


@app.post("/kaspi/update_product_price")
async def update_product_price(payload: PriceUpdateRequest):
    try:
        result = await sync_product(payload.product_id, payload.price)

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Ошибка при обновлений цены: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при обновлений цены"
        )


@app.get("/kaspi/get_sells_info/{shop_id}")
async def get_sells_info(shop_id):
    try:
        success, result = await get_sells(shop_id)

        return {
            "success": success,
            "data": result
        }
    except Exception as e:
        logger.error(f"Ошибка при обновлений цены: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при обновлений цены"
        )


async def check_and_update_prices():
    clogger = logging.getLogger("price_checker")
    clogger.setLevel(logging.INFO)

    # Если вы не хотите, чтобы сообщения этого логгера шли в корневой хендлер,
    # можно отключить распространение:
    clogger.propagate = False

    # А добавить свой хендлер, например в файл:
    chandler = logging.FileHandler("demping_cron.log", encoding="utf-8")
    chandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    clogger.addHandler(chandler)
    
    pool = await create_pool()
    
    while True:
        try:
            clogger.info("Начинаем работу демпера...")
            async with pool.acquire() as conn:
                products = await conn.fetch(
                    """
                    SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
                    FROM products
                    WHERE bot_active = TRUE
                    """
                )
            
            clogger.info(f"Нашли {len(products)} активных продуктов.")
            for product in products:
                product_id = product["id"]
                product_external_id = product["external_kaspi_id"]
                sku = product["kaspi_sku"]
                current_price = Decimal(product["price"])
                # clogger.info(f"Processing product ID: {product_id}, SKU: {sku}, Current price: {current_price}")

                product_data = await parse_product_by_sku(product_external_id)
                if product_data and len(product_data):
                    min_offer_price = min(Decimal(offer["price"]) for offer in product_data)
                    # clogger.info(f"Minimum offer price for SKU {sku} is {min_offer_price}")

                    if current_price > max(min_offer_price, product['min_profit']):
                        new_price = min_offer_price - Decimal('1.00')

                        # clogger.info(f"Attempting to sync product {product_id} with new price {new_price}")
                        sync_result = await sync_product(product_id, new_price)

                        if sync_result.get('success'):
                            # clogger.info(f"Sync successful for product ID {product_id}, updating price in database.")
                            async with pool.acquire() as conn:
                                await conn.execute(
                                    """
                                    UPDATE products
                                    SET price = $1
                                    WHERE id = $2
                                    """,
                                    int(new_price), product_id
                                )
                            clogger.info(f"Демпер: Успешно - [{sku}] -> {new_price}")
                            # clogger.info(f"Update response: {update_response}")
                        else:
                            pass
                            # clogger.warning(f"Sync failed for product ID {product_id}, price not updated in database.")

                    else:
                        pass
                        # clogger.info(
                        #     f"No update needed for product ID {product_id}. Current price {current_price} is already optimal.")
                else:
                    clogger.warning(f"Конкурентов нет [{sku}]")
                time.sleep(random.uniform(0.1, 0.3))
            store_ids = {p["store_id"] for p in products}
            for sid in store_ids:
                try:
                    result = await sync_store_api(sid)
                    clogger.info(f"Синхронизирован магазин {sid}: {result}")
                except Exception as e:
                    clogger.error(f"Ошибка sync_store_api для {sid}: {e}", exc_info=True)
        except Exception as e:
            clogger.error(f"Error during price check/update: {e}", exc_info=True)

        await asyncio.sleep(5)


class SMSStartRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    phone: str = Field(..., description="Номер телефона для SMS-авторизации")


class SMSVerifyRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    session_id: str = Field(..., description="ID SMS-сессии из /sms/start")
    code: str = Field(..., description="Код из SMS")


@app.post("/kaspi/auth/sms/start")
async def kaspi_sms_start(req: SMSStartRequest):
    """
    Шаг 1: отправляем номер в SMS-форму, возвращаем session_id
    """
    session_id = await sms_login_start(req.user_id, req.phone)
    return {"session_id": session_id}


@app.post("/kaspi/auth/sms/verify")
async def kaspi_sms_verify(req: SMSVerifyRequest):
    """
    Шаг 2: вводим код, получаем merchant_id, shop_name и сохраняем (или обновляем) магазин в БД.
    """
    cookies, merchant_uid, shop_name, guid = await sms_login_verify(
        req.session_id, req.user_id, req.code
    )

    # Получаем пул соединений
    from db import create_pool
    pool = await create_pool()

    # check if user already has a store
    async with pool.acquire() as connection:
        existing = await connection.fetch(
            """
            SELECT id, user_id
            FROM kaspi_stores
            WHERE user_id = $1
            LIMIT 1
            """,
            req.user_id
        )

    now = datetime.now()
    if existing:
        # update existing store with new session data
        async with pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE kaspi_stores
                SET merchant_id = $1,
                    name = $2,
                    guid = $3,
                    updated_at = $4,
                    last_sync = NULL
                WHERE user_id = $5
                """,
                merchant_uid, shop_name, json.dumps(guid), now, req.user_id
            )
            
            # fetch updated store
            updated_store = await connection.fetchrow(
                """
                SELECT * FROM kaspi_stores
                WHERE user_id = $1
                """,
                req.user_id
            )
            
        return {
            "success": True,
            "store_id": updated_store['id'],
            "message": "Сессия магазина успешно обновлена через SMS",
            "is_replaced": True
        }

    # Иначе — создаём новую запись
    store_data = {
        "user_id": req.user_id,
        "merchant_id": merchant_uid,
        "name": shop_name,
        "api_key": f"kaspi_{secrets.token_urlsafe(16)}",
        "guid": guid,
        "created_at": now,
        "updated_at": now
    }

    # Вставка новой записи в базу данных
    async with pool.acquire() as connection:
        resp = await connection.execute(
            """
            INSERT INTO kaspi_stores (user_id, merchant_id, name, api_key, guid, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            store_data["user_id"], store_data["merchant_id"], store_data["name"],
            store_data["api_key"], json.dumps(store_data["guid"]), datetime.now(),
            datetime.now()
        )

    # Получаем id вставленной записи
    store_id = resp.split()[-1]  # Получаем последний элемент, который будет ID вставленной записи

    return {
        "success": True,
        "store_id": store_id,
        "message": "Магазин успешно привязан через SMS",
        "is_replaced": False
    }


class PreorderRequest(BaseModel):
    store_id: str = Field(..., description="ID SMS-сессии из /sms/start")


@app.post("/kaspi/preorder")
async def preorder_upload(req: PreorderRequest):
    await handle_upload_preorder(req.store_id)
    return {
        "success": True,
        "message": f"Файл предзаказов для магазина {req.store_id} успешно сформирован и отправлен"
    }


class PreorderBatchRequest(BaseModel):
    store_id: str
    products: list


@app.post("/kaspi/preorder/batch")
async def batch_preorder(req: PreorderBatchRequest):
    results = []
    for p in req.products:
        res = await create_preorder_from_product(p, req.store_id)
        results.append(res)
    return {"results": results}


@app.get("/kaspi/preorders/stores/{user_id}")
async def get_user_stores_for_preorders(user_id: str):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, name, merchant_id, products_count, last_sync, is_active, created_at
                FROM kaspi_stores
                WHERE user_id = $1 AND is_active = true
                ORDER BY name
                """,
                user_id
            )
        return {"success": True, "stores": [dict(r) for r in rows]}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/kaspi/preorders/products/{store_id}")
async def get_store_products_for_preorders(store_id: str):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, kaspi_product_id, name, price, image_url, category, 
                       kaspi_sku, external_kaspi_id, created_at
                FROM products
                WHERE store_id = $1
                ORDER BY name
                """,
                store_id
            )
        return {"success": True, "products": [dict(r) for r in rows]}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/kaspi/preorders/list/{store_id}")
async def get_store_preorders(store_id: str):
    try:
        preorders_data = await fetch_preorders(store_id)
        return {"success": True, "preorders": preorders_data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/kaspi/preorders/create")
async def create_preorder_item(preorder_data: dict):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            existing = await conn.fetchval(
                """
                SELECT id FROM preorders 
                WHERE store_id = $1 AND product_id = $2
                """,
                preorder_data["store_id"], preorder_data.get("product_id")
            )
            
            if existing:
                return {"success": False, "error": "Предзаказ уже существует для этого товара"}
            
            warehouses_json = json.dumps(preorder_data["warehouses"])
            
            preorder_id = await conn.fetchval(
                """
                INSERT INTO preorders (store_id, product_id, article, name, brand, price,
                                     warehouses, delivery_days, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
                """,
                preorder_data["store_id"],
                preorder_data.get("product_id"),
                preorder_data["article"],
                preorder_data["name"],
                preorder_data.get("brand", ""),
                preorder_data["price"],
                warehouses_json,
                preorder_data["delivery_days"],
                "processing",
                datetime.now(),
                datetime.now()
            )
            
        return {"success": True, "preorder_id": preorder_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/kaspi/preorders/{preorder_id}/status")
async def update_preorder_status(preorder_id: str, status_data: dict):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE preorders 
                SET status = $1, updated_at = $2
                WHERE id = $3
                """,
                status_data["status"],
                datetime.now(),
                preorder_id
            )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/kaspi/preorders/{preorder_id}")
async def delete_preorder_item(preorder_id: str):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM preorders WHERE id = $1",
                preorder_id
            )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/kaspi/preorders/stats/{store_id}")
async def get_preorder_stats(store_id: str):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM preorders WHERE store_id = $1",
                store_id
            )
            
            status_counts = await conn.fetch(
                """
                SELECT status, COUNT(*) as count
                FROM preorders 
                WHERE store_id = $1
                GROUP BY status
                """,
                store_id
            )
            
            total_quantity = await conn.fetchval(
                """
                SELECT COALESCE(SUM(
                    (warehouses->>'quantity')::int
                ), 0)
                FROM preorders 
                WHERE store_id = $1
                """,
                store_id
            )
            
        return {
            "success": True,
            "stats": {
                "total_preorders": total,
                "status_counts": {r["status"]: r["count"] for r in status_counts},
                "total_quantity": total_quantity
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/kaspi/preorders/upload/{store_id}")
async def upload_preorders_to_kaspi(store_id: str):
    try:
        await handle_upload_preorder(store_id)
        return {
            "success": True, 
            "message": f"Предзаказы для магазина {store_id} успешно загружены на Kaspi"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/kaspi/preorders/generate-excel/{store_id}")
async def generate_preorder_excel(store_id: str):
    try:
        preorders_data = await fetch_preorders(store_id)
        if not preorders_data:
            return {"success": False, "error": "Нет предзаказов для генерации Excel файла"}
        
        processed_data = process_preorders_for_excel(preorders_data)
        
        filepath = generate_preorder_xlsx(processed_data, store_id)
        return {
            "success": True, 
            "filepath": filepath,
            "message": "Excel файл успешно сгенерирован"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/kaspi/preorders/create-from-product")
async def create_preorder_from_existing_product(preorder_data: dict):
    try:
        result = await create_preorder_from_product(preorder_data, preorder_data["store_id"])
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Вместо app используем строку с указанием пути
    uvicorn.run("main:app", host="0.0.0.0", port=8010)