#!/usr/bin/env python3
"""
Исправленный маппинг товаров с правильными полями
"""

import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, List, Any

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
    
    logger.info(f"✅ [MAPPER] Результат маппинга:")
    logger.info(f"   📦 SKU: {mapped_data['kaspi_sku']}")
    logger.info(f"   📝 Название: {mapped_data['name'][:50] if mapped_data['name'] else 'N/A'}...")
    logger.info(f"   💰 Цена: {mapped_data['price']} ₸")
    logger.info(f"   🏷️ Категория: {mapped_data['category']}")
    logger.info(f"   🖼️ Изображение: {mapped_data['image_url']}")
    logger.info(f"   📦 Наличие: {mapped_data['stock_count']} шт.")
    
    return mapped_data

async def get_products_correct(cookies_dict: Dict[str, str], merchant_uid: str, page_size: int = 100) -> List[Dict]:
    """Получение товаров с исправленным маппингом"""
    logger.info(f"🔍 [PRODUCTS] Начинаем получение товаров для merchant_uid: {merchant_uid}")
    
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
                f"?m={merchant_uid}&p={page}&l={page_size}&a=true"
            )
            logger.info(f"🌐 [PRODUCTS] Запрос страницы {page}: {url}")

            try:
                async with session.get(url, headers=headers, cookies=cookies_dict) as response:
                    logger.info(f"📊 [PRODUCTS] Ответ страницы {page}: статус {response.status}")
                    
                    if response.status == 401:
                        logger.error(f"❌ [PRODUCTS] Ошибка авторизации: 401 Unauthorized")
                        break
                    
                    if response.status == 429:
                        logger.error(f"❌ [PRODUCTS] Превышен лимит запросов: 429 Too Many Requests")
                        break

                    response.raise_for_status()

                    data = await response.json()
                    offers = data.get('data', [])
                    logger.info(f"📦 [PRODUCTS] Получено сырых офферов на странице {page}: {len(offers)}")

                    if not offers:
                        logger.info(f"🏁 [PRODUCTS] Страница {page} пустая, завершаем пагинацию")
                        break

                    # Добавляем офферы с исправленным маппингом
                    processed_count = 0
                    for o in offers:
                        mapped_offer = map_offer_correct(o)
                        all_offers.append(mapped_offer)
                        processed_count += 1

                    logger.info(f"📊 [PRODUCTS] Получено {len(offers)} офферов на странице {page}")
                    logger.info(f"📈 [PRODUCTS] Всего накоплено офферов: {len(all_offers)}")

                    page += 1

            except Exception as err:
                logger.error(f"❌ [PRODUCTS] Ошибка при запросе офферов: {err}")
                break

    logger.info(f"🎉 [PRODUCTS] Всего получено офферов: {len(all_offers)}")
    return all_offers

async def test_correct_products():
    """Тест получения товаров с исправленным маппингом"""
    
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
    
    # Получаем товары с исправленным маппингом
    products = await get_products_correct(cookies_dict, merchant_id)
    
    logger.info(f"🎯 [TEST] Результат:")
    logger.info(f"   📦 Всего товаров: {len(products)}")
    
    if products:
        logger.info(f"   📋 Все товары:")
        for i, product in enumerate(products):
            logger.info(f"   {i+1}. {product['name']}")
            logger.info(f"      💰 Цена: {product['price']} ₸")
            logger.info(f"      🏷️ Категория: {product['category']}")
            logger.info(f"      📦 Наличие: {product['stock_count']} шт.")
            logger.info(f"      🖼️ Изображение: {product['image_url']}")
            logger.info(f"      ---")
    else:
        logger.info(f"   ⚠️ Товары не найдены")

if __name__ == "__main__":
    asyncio.run(test_correct_products())
