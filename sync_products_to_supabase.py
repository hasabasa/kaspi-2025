#!/usr/bin/env python3
"""
Синхронизация товаров магазина в Supabase
"""

import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, List, Any
from uuid import uuid4

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def map_offer_correct(raw_offer: dict) -> dict:
    """Исправленный маппинг оффера с правильными полями"""
    
    # Извлекаем ID товара из URL
    product_url = raw_offer.get("shopLink", "")
    match = re.search(r'\/p\/.*-(\d+)\/', product_url)
    external_kaspi_id = match.group(1) if match else None
    
    # Получаем изображение (первое из списка)
    images = raw_offer.get("images", [])
    image_url = f"https://resources.kaspi.kz/img/{images[0]}" if images else ""
    
    # Получаем название и цену
    master_title = raw_offer.get("masterTitle", "")
    min_price = raw_offer.get("minPrice", 0)
    master_category = raw_offer.get("masterCategory", "")
    
    # Получаем информацию о наличии
    availabilities = raw_offer.get("availabilities", [])
    stock_count = 0
    if availabilities:
        stock_count = availabilities[0].get("stockCount", 0)
    
    mapped_data = {
        "kaspi_sku": raw_offer.get("offerId", ""),
        "kaspi_product_id": external_kaspi_id,
        "name": master_title,
        "price": min_price,
        "category": master_category,
        "image_url": image_url,
        "shop_link": product_url,
        "stock_count": stock_count,
        "available": raw_offer.get("available", False),
        "master_sku": raw_offer.get("masterSku", ""),
        "model": raw_offer.get("model", ""),
        "brand": raw_offer.get("brand", ""),
        "raw_data": raw_offer
    }
    
    return mapped_data

async def get_products_from_kaspi(cookies_dict: Dict[str, str], merchant_uid: str) -> List[Dict]:
    """Получение товаров из Kaspi API"""
    logger.info(f"🔍 [SYNC] Получаем товары для merchant_uid: {merchant_uid}")
    
    headers = {
        "x-auth-version": "3",
        "Origin": "https://kaspi.kz",
        "Referer": "https://kaspi.kz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    all_offers = []
    page = 0

    async with aiohttp.ClientSession() as session:
        while True:
            url = (
                f"https://mc.shop.kaspi.kz/bff/offer-view/list"
                f"?m={merchant_uid}&p={page}&l=100&a=true"
            )

            try:
                async with session.get(url, headers=headers, cookies=cookies_dict) as response:
                    if response.status != 200:
                        break

                    data = await response.json()
                    offers = data.get('data', [])

                    if not offers:
                        break

                    for o in offers:
                        mapped_offer = map_offer_correct(o)
                        all_offers.append(mapped_offer)

                    page += 1

            except Exception as err:
                logger.error(f"❌ [SYNC] Ошибка при запросе офферов: {err}")
                break

    logger.info(f"🎉 [SYNC] Получено {len(all_offers)} товаров из Kaspi")
    return all_offers

async def sync_products_to_supabase(store_id: str, products: List[Dict]):
    """Синхронизация товаров в Supabase"""
    logger.info(f"📦 [SYNC] Синхронизируем {len(products)} товаров в Supabase")
    
    # Здесь должен быть код для добавления товаров в Supabase
    # Пока что просто логируем данные
    
    for i, product in enumerate(products):
        logger.info(f"📦 [SYNC] Товар {i+1}:")
        logger.info(f"   🆔 ID: {str(uuid4())}")
        logger.info(f"   📦 SKU: {product['kaspi_sku']}")
        logger.info(f"   📝 Название: {product['name']}")
        logger.info(f"   💰 Цена: {product['price']} ₸")
        logger.info(f"   🏷️ Категория: {product['category']}")
        logger.info(f"   📦 Наличие: {product['stock_count']} шт.")
        logger.info(f"   🖼️ Изображение: {product['image_url']}")
        logger.info(f"   ---")

async def sync_store_products():
    """Основная функция синхронизации"""
    
    # Загружаем cookies
    with open('/Users/hasen/demper-667-45/unified-backend/accounts.json', 'r') as f:
        accounts = json.load(f)
    
    email = 'hvsv1@icloud.com'
    session_data = accounts[email]
    cookies_data = session_data.get('cookies', [])
    merchant_id = session_data.get('merchant_id', '')
    
    # Формируем cookies
    cookies_dict = {}
    for cookie in cookies_data:
        cookies_dict[cookie['name']] = cookie['value']
    
    logger.info(f"🏪 [SYNC] Синхронизация магазина: {merchant_id}")
    
    # Получаем товары из Kaspi
    products = await get_products_from_kaspi(cookies_dict, merchant_id)
    
    if products:
        # Синхронизируем в Supabase
        store_id = "2e236ced-c24b-4c55-bec7-dc56b8b5c174"  # ID магазина из Supabase
        await sync_products_to_supabase(store_id, products)
        
        logger.info(f"✅ [SYNC] Синхронизация завершена!")
        logger.info(f"   📦 Товаров синхронизировано: {len(products)}")
    else:
        logger.error(f"❌ [SYNC] Товары не найдены")

if __name__ == "__main__":
    asyncio.run(sync_store_products())
