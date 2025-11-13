import asyncio
import re
import time
from functools import wraps
from supabase import create_client, Client
from db import create_pool
from uuid import UUID
from fastapi import HTTPException, status
from typing import Callable, TypeVar, Optional, Coroutine, List, Tuple, Any
from core.logger import logger
import os

T = TypeVar('T')

_supabase_client: Any = None

def set_supabase_client(client):
    """Set the global supabase client"""
    global _supabase_client
    _supabase_client = client

def get_supabase_client() -> Client:
    if _supabase_client is None:
        raise RuntimeError("Supabase client not initialized. Call set_supabase_client first.")
    return _supabase_client


class ParserError(Exception):
    """Базовый класс для ошибок парсера"""
    pass


class LoginError(ParserError):
    """Ошибка при входе в систему"""
    pass


class ProductNotFoundError(ParserError):
    """Ошибка при поиске товара"""
    pass


class NetworkError(ParserError):
    """Ошибка сети"""
    pass


async def retry_on_error(
        func: Callable[[], Coroutine],
        max_attempts: Optional[int] = None,
        delay: Optional[float] = None,
        exceptions: tuple = (Exception,)
) -> T:
    """
    Декоратор для повторных попыток выполнения функции при ошибках
    
    Args:
        func: Функция для выполнения
        max_attempts: Максимальное количество попыток (по умолчанию из конфига)
        delay: Задержка между попытками в секундах (по умолчанию из конфига)
        exceptions: Кортеж исключений, при которых нужно повторять попытку
    """
    max_attempts = max_attempts or 3
    delay = delay or 0.4

    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except exceptions as e:
            logger.error(f"Попытка {attempt} не удалась: {str(e)}")
            if attempt == max_attempts:
                raise
            await asyncio.sleep(delay)


def log_execution_time(func: Callable) -> Callable:
    """
    Декоратор для логирования времени выполнения функции
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Функция {func.__name__} выполнена за {execution_time:.2f} секунд")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Функция {func.__name__} завершилась с ошибкой после {execution_time:.2f} секунд: {str(e)}")
            raise

    return wrapper


def validate_product_data(product: dict) -> bool:
    """
    Валидация данных товара
    
    Args:
        product: Словарь с данными товара
        
    Returns:
        bool: True если данные валидны, False в противном случае
    """
    required = ['name', 'sku', 'current_price']
    missing = [k for k in required if not product.get(k)]
    if missing:
        logger.warning(f"Отсутствуют обязательные поля: {missing}")
        return False

    # Проверка типов данных
    if not isinstance(product['name'], str) or not product['name'].strip():
        logger.error("Название товара должно быть непустой строкой")
        return False

    if not isinstance(product['sku'], str) or not product['sku'].strip():
        logger.error("SKU должен быть непустой строкой")
        return False

    try:
        # Удаляем все нецифровые символы (кроме точки)
        price_str = re.sub(r'[^\d.]', '', str(product['current_price']))
        price = float(price_str)
        if price < 0:
            logger.error("Цена не может быть отрицательной")
            return False
    except ValueError:
        logger.error("Некорректный формат цены")
        return False

    return True


async def validate_store_id(store_id: UUID) -> bool:
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT id FROM kaspi_stores WHERE id = $1",
                str(store_id)
            )
        return bool(result)
    except Exception as e:
        logger.error(f"Error validating store_id {store_id}: {str(e)}, type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating store ID: {str(e)}"
        )

async def validate_product_ids(store_id: UUID, product_ids: List[str]) -> Tuple[List[str], List[str]]:
    start_time = time.time()
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT kaspi_product_id 
                FROM products 
                WHERE store_id = $1 AND kaspi_product_id = ANY($2)
                """,
                str(store_id), product_ids
            )
        
        existing_ids = [row['kaspi_product_id'] for row in result]
        failed_ids = [pid for pid in product_ids if pid not in existing_ids]
        valid_ids = [pid for pid in product_ids if pid in existing_ids]
        
        logger.info(f"Validated {len(product_ids)} product IDs in {time.time() - start_time:.2f} seconds")
        return valid_ids, failed_ids
    except Exception as e:
        logger.error(f"Error validating product IDs for store {store_id}: {str(e)}, took {time.time() - start_time:.2f} seconds")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating product IDs: {str(e)}"
        )

def sanitize_name_filter(name: str) -> str:
    if len(name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name filter must be at least 3 characters long"
        )
    sanitized = re.sub(r'[^\w\s-]', '', name).strip()
    if not sanitized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid name filter"
        )
    return sanitized

async def test_db_connection():
    try:
        pool = await create_pool()
        async with pool.acquire() as connection:
            result = await connection.fetchval("SELECT 1")
            logger.info(f"Database connection test successful: {result}")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}, type: {type(e).__name__}")
        return False
    
async def has_active_subscription(user_id: str) -> bool:
    """
    Проверка подписки отключена и всегда возвращает True.
    """
    logger.info(f"🔓 [SUBSCRIPTION] Проверка подписки отключена для пользователя {user_id}")
    return True

async def has_existing_store(user_id: str) -> bool:
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT id
                FROM kaspi_stores
                WHERE user_id = $1
                """,
                user_id
            )
        return bool(result)
    except Exception as e:
        logger.error(f"Error checking existing stores for user {user_id}: {str(e)}", exc_info=True)
        return False

async def get_product_count(store_id: str) -> int:
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM products
                WHERE store_id = $1
                """,
                store_id
            )
        return result or 0
    except Exception as e:
        logger.error(f"Error counting products for store {store_id}: {str(e)}", exc_info=True)
        return 0