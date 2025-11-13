import asyncio
import re
import time
from functools import wraps
from supabase import create_client, Client
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
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
        supabase = get_supabase_client()
        result = supabase.table("kaspi_stores").select("id").eq("id", str(store_id)).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error validating store_id {store_id}: {str(e)}, type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating store ID: {str(e)}"
        )

async def validate_product_ids(store_id: UUID, product_ids: List[str]) -> Tuple[List[str], List[str]]:
    start_time = time.time()
    try:
        supabase = get_supabase_client()
        result = supabase.table("products").select("kaspi_product_id").eq("store_id", str(store_id)).in_("kaspi_product_id", product_ids).execute()
        
        existing_ids = [row['kaspi_product_id'] for row in result.data]
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
        supabase = get_supabase_client()
        result = supabase.table("kaspi_stores").select("count", count="exact").limit(1).execute()
        logger.info(f"Supabase connection test successful: {result.count if hasattr(result, 'count') else 'unknown'}")
        return True
    except Exception as e:
        logger.error(f"Supabase connection test failed: {str(e)}, type: {type(e).__name__}")
        return False
    
# Удалены все функции подписки - больше не нужны

def normalize_date_string(date_string: str) -> Optional[datetime]:
    try:
        if isinstance(date_string, str):
            normalized = date_string.strip()
            
            if ' ' in normalized and 'T' not in normalized:
                normalized = normalized.replace(' ', 'T')
            
            if normalized.endswith('Z'):
                normalized = normalized.replace('Z', '+00:00')
            
            try:
                return datetime.fromisoformat(normalized)
            except ValueError:
                pass
            
            return _parse_date_manually(normalized)
        
        elif isinstance(date_string, datetime):
            return date_string
            
        return None
        
    except Exception as e:
        logger.error(f"Failed to normalize date string: {date_string}, error: {e}")
        return None

def _parse_date_manually(date_string: str) -> datetime:
    try:
        if '.' in date_string:
            parts = date_string.split('.')
            if len(parts) == 2:
                date_part = parts[0]
                timezone_part = parts[1]
                
                if '+' in timezone_part:
                    timezone_offset = timezone_part.split('+')[1]
                    microseconds_part = timezone_part.split('+')[0]
                elif '-' in timezone_part and timezone_part.count('-') > 1:
                    last_dash_index = timezone_part.rfind('-')
                    timezone_offset = timezone_part[last_dash_index:]
                    microseconds_part = timezone_part[:last_dash_index]
                else:
                    timezone_offset = '+00:00'
                    microseconds_part = timezone_part
                
                if microseconds_part:
                    if len(microseconds_part) > 6:
                        microseconds_part = microseconds_part[:6]
                    elif len(microseconds_part) < 6:
                        microseconds_part = microseconds_part.ljust(6, '0')
                    
                    date_string = f"{date_part}.{microseconds_part}{timezone_offset}"
                else:
                    date_string = f"{date_part}{timezone_offset}"
        
        if '+' in date_string and not date_string.endswith('+00:00'):
            timezone_part = date_string.split('+')[1]
            if ':' not in timezone_part and len(timezone_part) == 2:
                date_string = date_string.replace(f"+{timezone_part}", f"+{timezone_part}:00")
        
        try:
            return datetime.fromisoformat(date_string)
        except ValueError:
            pass
        
        return _parse_components_manually(date_string)
        
    except Exception as e:
        logger.error(f"Failed to parse date manually: {date_string}, error: {e}")
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

def _parse_components_manually(date_string: str) -> datetime:
    try:
        has_timezone = False
        timezone_offset = '+00:00'
        
        if '+' in date_string:
            has_timezone = True
            parts = date_string.split('+')
            date_part = parts[0]
            timezone_part = parts[1]
            if ':' in timezone_part:
                timezone_offset = f"+{timezone_part}"
            else:
                timezone_offset = f"+{timezone_part}:00"
        elif date_string.endswith('Z'):
            has_timezone = True
            date_part = date_string[:-1]
            timezone_offset = '+00:00'
        else:
            date_part = date_string
        
        if 'T' in date_part:
            date_str, time_str = date_part.split('T')
        else:
            date_str = date_part
            time_str = '00:00:00'
        
        year, month, day = map(int, date_str.split('-'))
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if len(time_parts) > 2:
            second_part = time_parts[2]
            if '.' in second_part:
                second_str, microsecond_str = second_part.split('.')
                second = int(second_str)
                if len(microsecond_str) > 6:
                    microsecond_str = microsecond_str[:6]
                elif len(microsecond_str) < 6:
                    microsecond_str = microsecond_str.ljust(6, '0')
                microsecond = int(microsecond_str)
            else:
                second = int(second_part)
                microsecond = 0
        else:
            second = 0
            microsecond = 0
        
        dt = datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)
        
        if has_timezone and timezone_offset != '+00:00':
            offset_str = timezone_offset[1:]
            if ':' in offset_str:
                hours, minutes = map(int, offset_str.split(':'))
            else:
                hours = int(offset_str)
                minutes = 0
            
            offset_seconds = hours * 3600 + minutes * 60
            if timezone_offset.startswith('-'):
                offset_seconds = -offset_seconds
            
            dt = dt.replace(tzinfo=timezone(timedelta(seconds=offset_seconds)))
        
        return dt
        
    except Exception as e:
        logger.error(f"Failed to parse date components: {date_string}, error: {e}")
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

async def has_existing_store(user_id: str) -> bool:
    try:
        supabase = get_supabase_client()
        result = supabase.table("kaspi_stores").select("id").eq("user_id", user_id).limit(1).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error checking existing stores for user {user_id}: {str(e)}", exc_info=True)
        return False

async def get_product_count(store_id: str) -> int:
    try:
        supabase = get_supabase_client()
        result = supabase.table("products").select("count", count="exact").eq("store_id", store_id).execute()
        return result.count if hasattr(result, 'count') else 0
    except Exception as e:
        logger.error(f"Error counting products for store {store_id}: {str(e)}", exc_info=True)
        return 0