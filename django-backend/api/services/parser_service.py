"""
Сервис парсинга товаров Kaspi
Адаптировано из unified-backend/api_parser.py
"""
import re
import random
import logging
import asyncio
import aiohttp
from decimal import Decimal
from typing import List, Dict, Optional
from api.services.proxy_service import get_proxy_url

logger = logging.getLogger(__name__)


def run_async(coro):
    """Запускает async функцию синхронно"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
]

ACCEPT_ENCODINGS = [
    "gzip, deflate, br",
    "gzip, deflate, br, zstd",
    "gzip, deflate"
]

ACCEPT_LANGUAGE = [
    "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "ru-RU,ru;q=0.8,en-US;q=0.7,en;q=0.6",
    "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7"
]

X_KS_CITY = [
    "750000000",  # Алматы
    "770000000",  # Астана
    "730000000",  # Шымкент
]


def get_random_headers(sku: str = None) -> dict:
    """Генерирует случайные заголовки для запросов"""
    return {
        "accept": random.choice([
            "application/json, text/*",
            "application/json, text/html, */*",
        ]),
        "accept-encoding": random.choice(ACCEPT_ENCODINGS),
        "accept-language": random.choice(ACCEPT_LANGUAGE),
        "cache-control": random.choice(["no-cache", "max-age=0"]),
        "connection": random.choice(["keep-alive", "close"]),
        "content-type": "application/json; charset=UTF-8",
        "host": "kaspi.kz",
        "origin": "https://kaspi.kz",
        "pragma": random.choice(["no-cache", ""]),
        "referer": f"https://kaspi.kz/shop/p/{sku}" if sku else "https://kaspi.kz/",
        "user-agent": random.choice(USER_AGENTS),
        "x-ks-city": X_KS_CITY[0],
    }


async def parse_product_by_sku(sku: str) -> List[Dict]:
    """Парсит данные о товаре по SKU через API Kaspi асинхронно"""
    logger.info(f"🔍 [PARSER] Начинаем парсинг товара SKU: {sku}")
    
    url = f"https://kaspi.kz/yml/offer-view/offers/{sku}"
    headers = get_random_headers(sku)
    
    body = {
        "cityId": "750000000",
        "id": sku,
        "merchantUID": [],
        "limit": 5,
        "page": 0,
        "sortOption": "PRICE",
        "highRating": None,
        "searchText": None,
        "zoneId": ["Magnum_ZONE1"],
        "installationId": "-1"
    }
    
    try:
        proxy_url = get_proxy_url(f"sku_{sku}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=headers, proxy=proxy_url) as response:
                if response.status == 429:
                    logger.error(f"❌ [PARSER] Rate limit для SKU {sku}")
                    return []
                
                response.raise_for_status()
                data = await response.json()
                
                if 'offers' not in data:
                    logger.warning(f"⚠️ [PARSER] Нет предложений для SKU {sku}")
                    return []
                
                offers = data['offers']
                parsed_offers = []
                
                for offer in offers:
                    parsed_offers.append({
                        'merchant_id': offer.get('merchantId'),
                        'price': offer.get('price', 0)
                    })
                
                logger.info(f"✅ [PARSER] Получено {len(parsed_offers)} предложений для SKU {sku}")
                return parsed_offers
                
    except aiohttp.ClientError as e:
        logger.error(f"❌ [PARSER] Ошибка HTTP запроса для SKU {sku}: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ [PARSER] Ошибка обработки данных для SKU {sku}: {e}")
        return []


async def sync_product(product_id: str, price: Decimal, cookies: dict, merchant_id: str, kaspi_sku: str) -> Dict:
    """Синхронизация цены товара в Kaspi"""
    url = "https://mc.shop.kaspi.kz/pricefeed/upload/merchant/process"
    
    headers = {
        "accept": "application/json, text/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "content-type": "application/json; charset=UTF-8",
        "host": "mc.shop.kaspi.kz",
        "origin": "https://kaspi.kz",
        "pragma": "no-cache",
        "referer": "https://kaspi.kz/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "x-ks-city": "750000000",
    }
    
    body = {
        "merchantUid": merchant_id,
        "availabilities": [{"available": "yes", "storeId": f"{merchant_id}_PP1", "stockEnabled": False}],
        "sku": kaspi_sku,
        "price": float(price)
    }
    
    try:
        proxy_url = get_proxy_url(f"merchant_{merchant_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=headers, cookies=cookies, proxy=proxy_url) as response:
                response.raise_for_status()
                response_data = await response.json()
                
                if 'status' in response_data and response_data['status'] == 'success':
                    logger.info(f"✅ Цена для товара {product_id} обновлена успешно")
                    return {
                        "success": True,
                        "message": f"Товар {product_id} успешно синхронизирован"
                    }
                else:
                    logger.warning(f"⚠️ Не удалось обновить цену для товара {product_id}")
                    return {
                        "success": False,
                        "message": f"Не удалось обновить цену: {response_data}"
                    }
                    
    except aiohttp.ClientError as e:
        logger.error(f"❌ Ошибка при обновлении цены: {e}")
        raise

