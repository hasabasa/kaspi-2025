#!/usr/bin/env python3
"""
Тест получения товаров магазина через API Kaspi
"""

import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def get_products_from_kaspi(cookies_dict: Dict[str, str], merchant_uid: str, page_size: int = 100) -> List[Dict]:
    """
    Получает все товары продавца по пагинации (как в kaspi-demper-main)
    """
    logger.info(f"🔍 [PRODUCTS] Начинаем получение товаров для merchant_uid: {merchant_uid}")
    logger.info(f"📦 [PRODUCTS] Размер страницы: {page_size}")
    
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
    logger.info(f"📋 [PRODUCTS] Заголовки запроса: {headers}")
    logger.info(f"🍪 [PRODUCTS] Cookies: {list(cookies_dict.keys())}")

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

                    # Если на странице нет офферов — выходим из цикла
                    if not offers:
                        logger.info(f"🏁 [PRODUCTS] Страница {page} пустая, завершаем пагинацию")
                        break

                    # Добавляем офферы в общий список
                    processed_count = 0
                    for o in offers:
                        mapped_offer = map_offer(o)
                        all_offers.append(mapped_offer)
                        processed_count += 1
                        logger.info(f"✅ [PRODUCTS] Обработан оффер {processed_count}: SKU={mapped_offer.get('kaspi_sku')}, название={mapped_offer.get('name', 'N/A')[:50]}...")

                    logger.info(f"📊 [PRODUCTS] Получено {len(offers)} офферов на странице {page}")
                    logger.info(f"📈 [PRODUCTS] Всего накоплено офферов: {len(all_offers)}")

                    page += 1

            except Exception as err:
                logger.error(f"❌ [PRODUCTS] Ошибка при запросе офферов: {err}")
                break

    logger.info(f"🎉 [PRODUCTS] Всего получено офферов: {len(all_offers)}")
    return all_offers

def map_offer(raw_offer: dict) -> dict:
    """Маппинг оффера (как в kaspi-demper-main)"""
    # Извлекаем ID товара из URL
    product_url = raw_offer.get("shopLink", "")
    match = re.search(r'\/p\/.*-(\d+)\/', product_url)
    external_kaspi_id = match.group(1) if match else None
    
    logger.info(f"🔍 [MAPPER] Начинаем маппинг оффера: {raw_offer.get('offerId', 'N/A')}")
    logger.info(f"🔗 [MAPPER] URL товара: {product_url}")
    logger.info(f"🆔 [MAPPER] Извлеченный external_kaspi_id: {external_kaspi_id}")
    
    mapped_data = {
        "kaspi_sku": raw_offer.get("offerId", ""),
        "name": raw_offer.get("name", ""),
        "price": raw_offer.get("price", 0),
        "category": raw_offer.get("category", ""),
        "image_url": raw_offer.get("imageUrl", ""),
        "external_kaspi_id": external_kaspi_id,
        "shop_link": product_url,
        "raw_data": raw_offer
    }
    
    logger.info(f"✅ [MAPPER] Результат маппинга:")
    logger.info(f"   📦 SKU: {mapped_data['kaspi_sku']}")
    logger.info(f"   📝 Название: {mapped_data['name'][:50] if mapped_data['name'] else 'N/A'}...")
    logger.info(f"   💰 Цена: {mapped_data['price']}")
    logger.info(f"   🏷️ Категория: {mapped_data['category']}")
    logger.info(f"   🖼️ Изображение: {mapped_data['image_url']}")
    
    return mapped_data

async def test_get_products():
    """Тест получения товаров"""
    
    # Загружаем cookies из файла accounts.json
    try:
        with open('/Users/hasen/demper-667-45/unified-backend/accounts.json', 'r') as f:
            accounts = json.load(f)
        
        email = 'hvsv1@icloud.com'
        if email in accounts:
            session_data = accounts[email]
            cookies_data = session_data.get('cookies', [])
            merchant_id = session_data.get('merchant_id', '')
            
            logger.info(f"🍪 [TEST] Найдена сессия для {email}")
            logger.info(f"🆔 [TEST] Merchant ID: {merchant_id}")
            logger.info(f"🍪 [TEST] Cookies: {len(cookies_data)}")
            
            # Формируем cookies для запроса
            cookies_dict = {}
            for cookie in cookies_data:
                cookies_dict[cookie['name']] = cookie['value']
            
            logger.info(f"🍪 [TEST] Cookies dict: {list(cookies_dict.keys())}")
            
            # Получаем товары
            products = await get_products_from_kaspi(cookies_dict, merchant_id)
            
            logger.info(f"🎯 [TEST] Результат:")
            logger.info(f"   📦 Всего товаров: {len(products)}")
            
            if products:
                logger.info(f"   📋 Первые 3 товара:")
                for i, product in enumerate(products[:3]):
                    logger.info(f"   {i+1}. {product['name'][:50]}... - {product['price']} ₸")
            else:
                logger.info(f"   ⚠️ Товары не найдены")
                
        else:
            logger.error(f"❌ [TEST] Аккаунт {email} не найден в accounts.json")
            
    except Exception as e:
        logger.error(f"❌ [TEST] Исключение: {e}")

if __name__ == "__main__":
    asyncio.run(test_get_products())
