#!/usr/bin/env python3
"""
Анализ сырых данных товаров для исправления маппинга
"""

import asyncio
import aiohttp
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def analyze_raw_products():
    """Анализ сырых данных товаров"""
    
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
    
    url = f"https://mc.shop.kaspi.kz/bff/offer-view/list?m={merchant_id}&p=0&l=100&a=true"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, cookies=cookies_dict) as response:
            data = await response.json()
            offers = data.get('data', [])
            
            logger.info(f"📊 [ANALYZE] Получено {len(offers)} офферов")
            
            if offers:
                # Анализируем первый оффер
                first_offer = offers[0]
                logger.info(f"🔍 [ANALYZE] Структура первого оффера:")
                logger.info(f"📋 [ANALYZE] Ключи: {list(first_offer.keys())}")
                
                # Выводим все данные первого оффера
                logger.info(f"📄 [ANALYZE] Полные данные первого оффера:")
                logger.info(json.dumps(first_offer, indent=2, ensure_ascii=False))
                
                # Анализируем все офферы
                logger.info(f"📊 [ANALYZE] Анализ всех офферов:")
                for i, offer in enumerate(offers):
                    logger.info(f"   {i+1}. ID: {offer.get('offerId', 'N/A')}")
                    logger.info(f"      Название: {offer.get('name', 'N/A')}")
                    logger.info(f"      Цена: {offer.get('price', 'N/A')}")
                    logger.info(f"      Категория: {offer.get('category', 'N/A')}")
                    logger.info(f"      URL: {offer.get('shopLink', 'N/A')}")
                    logger.info(f"      Изображение: {offer.get('imageUrl', 'N/A')}")
                    logger.info(f"      ---")

if __name__ == "__main__":
    asyncio.run(analyze_raw_products())
