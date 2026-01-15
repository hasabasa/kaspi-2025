"""
Сервис синхронизации товаров из Kaspi
Адаптировано из unified-backend/api_parser.py
"""
import re
import logging
import asyncio
import aiohttp
from decimal import Decimal
from typing import List, Dict, Optional
from django.utils import timezone
from api.models import KaspiStore, Product
from kaspi_auth.session_manager import SessionManager
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


async def get_products(cookie_jar: dict, merchant_uid: str, page_size: int = 100) -> List[Dict]:
    """
    Получает все товары продавца по пагинации асинхронно, с прокси и авторизацией.
    """
    logger.info(f"🔍 [PRODUCTS] Начинаем получение товаров для merchant_uid: {merchant_uid}")
    
    headers = {
        "x-auth-version": "3",
        "Origin": "https://kaspi.kz",
        "Referer": "https://kaspi.kz/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    # Получаем прокси
    proxy_url = get_proxy_url(f"merchant_{merchant_uid}")
    
    all_offers = []
    page = 0
    
    async with aiohttp.ClientSession() as session:
        while True:
            url = (
                f"https://mc.shop.kaspi.kz/bff/offer-view/list"
                f"?m={merchant_uid}&p={page}&l={page_size}&a=true"
            )
            
            try:
                async with session.get(url, headers=headers, cookies=cookie_jar, proxy=proxy_url) as response:
                    if response.status == 401:
                        logger.error("❌ [PRODUCTS] Ошибка авторизации: 401 Unauthorized")
                        raise Exception("Ошибка аутентификации: 401 Unauthorized")
                    
                    if response.status == 429:
                        logger.error("❌ [PRODUCTS] Превышен лимит запросов: 429")
                        raise Exception("Too Many Requests from Kaspi API")
                    
                    response.raise_for_status()
                    data = await response.json()
                    offers = data.get('data', [])
                    
                    if not offers:
                        break
                    
                    for o in offers:
                        mapped_offer = map_offer(o)
                        all_offers.append(mapped_offer)
                    
                    page += 1
                    
            except aiohttp.ClientError as err:
                logger.error(f"❌ [PRODUCTS] Ошибка при запросе: {err}")
                raise
    
    logger.info(f"🎉 [PRODUCTS] Всего получено офферов: {len(all_offers)}")
    return all_offers


def map_offer(raw_offer: dict) -> dict:
    """Преобразует сырой оффер в формат для БД"""
    product_url = raw_offer.get("shopLink", "")
    match = re.search(r'\/p\/.*-(\d+)\/', product_url)
    external_kaspi_id = match.group(1) if match else None
    
    # Обработка цены
    price_data = raw_offer.get("minPrice", {})
    if isinstance(price_data, dict):
        price = price_data.get("value", 0) * 100  # Конвертируем в тиыны
    else:
        price = int(price_data * 100) if price_data else 0
    
    return {
        "kaspi_product_id": raw_offer.get("offerId"),
        "kaspi_sku": raw_offer.get("sku"),
        "name": raw_offer.get("masterTitle", ""),
        "category": raw_offer.get("masterCategory"),
        "price": price,
        "image_url": f"https://resources.cdn-kaspi.kz/img/m/p/{raw_offer.get('images', [])[0]}" if raw_offer.get('images') else None,
        "external_kaspi_id": external_kaspi_id,
    }


async def insert_product_if_not_exists(product: dict, store_id: str):
    """Вставляет или обновляет товар в БД"""
    try:
        existing = Product.objects.filter(
            kaspi_sku=product["kaspi_sku"],
            store_id=store_id
        ).first()
        
        if existing:
            # Обновляем если цена или другие данные изменились
            if existing.price != product["price"] or existing.category != product.get('category') or existing.image_url != product.get('image_url'):
                existing.price = product["price"]
                existing.category = product.get('category')
                existing.image_url = product.get('image_url')
                existing.save()
                logger.info(f"🔄 Цена обновлена для товара: {product['name']}")
            return False
        
        # Создаем новый товар
        Product.objects.create(
            kaspi_product_id=product["kaspi_product_id"],
            kaspi_sku=product["kaspi_sku"],
            store_id=store_id,
            price=product["price"],
            name=product["name"],
            external_kaspi_id=product.get("external_kaspi_id"),
            category=product.get("category"),
            image_url=product.get("image_url"),
        )
        logger.info(f"✅ Добавлен товар: {product['name']}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при вставке товара: {e}")
        return False


async def sync_store_api(store_id: str) -> Dict:
    """Синхронизация товаров для указанного магазина"""
    try:
        # Загружаем сессию магазина
        session_manager = SessionManager(shop_uid=store_id)
        if not session_manager.load():
            raise Exception("Сессия истекла или отсутствуют учётные данные. Нужен повторный логин.")
        
        cookies = session_manager.get_cookies()
        if not cookies:
            raise Exception("Cookies для сессии не найдены")
        
        # Получение товаров для магазина
        merchant_id = session_manager.merchant_uid
        products = await get_products(cookies, merchant_id)
        
        current_count = len(products)
        
        # Вставка товаров, если они не существуют в базе данных
        for product in products:
            await insert_product_if_not_exists(product, store_id)
        
        # Обновление количества товаров и метки времени синхронизации
        store = KaspiStore.objects.get(id=store_id)
        existing_count = Product.objects.filter(store_id=store_id).count()
        
        store.products_count = existing_count
        store.last_sync = timezone.now()
        store.save()
        
        return {
            "success": True,
            "products_count": existing_count,
            "message": "Товары успешно синхронизированы"
        }
        
    except Exception as e:
        logger.error(f"Ошибка синхронизации магазина {store_id}: {e}")
        raise

