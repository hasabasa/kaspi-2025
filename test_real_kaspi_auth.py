#!/usr/bin/env python3
"""
Тест авторизации Kaspi с реальными данными
"""

import asyncio
import sys
import os
sys.path.append('/Users/hasen/demper-667-45/unified-backend')

from services.auth_manager import AuthManager
from core.logger import setup_logger

logger = setup_logger(__name__)

async def test_kaspi_auth():
    """Тест авторизации Kaspi с реальными данными"""
    
    # Реальные данные продавца
    email = "hvsv1@icloud.com"
    password = "CIoD29g8U1"
    auth_method = "selenium"  # или "playwright"
    
    logger.info(f"🧪 [TEST] Начинаем тест авторизации Kaspi")
    logger.info(f"📧 [TEST] Email: {email}")
    logger.info(f"🔑 [TEST] Метод: {auth_method}")
    
    try:
        # Создаем AuthManager
        auth_manager = AuthManager()
        
        # Выполняем авторизацию
        logger.info(f"🚀 [TEST] Вызываем auth_manager.login...")
        result = await auth_manager.login(email, password, auth_method)
        
        logger.info(f"📊 [TEST] Результат авторизации:")
        logger.info(f"   ✅ Success: {result.get('success', False)}")
        logger.info(f"   🏪 Merchant ID: {result.get('merchant_id', 'N/A')}")
        logger.info(f"   📝 Store Name: {result.get('store_name', 'N/A')}")
        logger.info(f"   🔑 Auth Method: {result.get('auth_method', 'N/A')}")
        logger.info(f"   📄 Session Data: {result.get('session_data', 'N/A')}")
        
        if result.get('error'):
            logger.error(f"❌ [TEST] Ошибка: {result.get('error')}")
        
        if result.get('success'):
            logger.info(f"🎉 [TEST] Авторизация успешна!")
            
            # Теперь попробуем запустить парсер
            logger.info(f"🔍 [TEST] Запускаем парсер товаров...")
            
            # Импортируем парсер
            from kaspi_demper_main.backend.api_parser import KaspiApiParser
            
            parser = KaspiApiParser()
            merchant_uid = result.get('merchant_id')
            
            if merchant_uid:
                logger.info(f"📦 [TEST] Получаем товары для merchant_uid: {merchant_uid}")
                products = await parser.get_products(merchant_uid)
                
                logger.info(f"📊 [TEST] Получено товаров: {len(products) if products else 0}")
                
                if products:
                    logger.info(f"📋 [TEST] Первые 3 товара:")
                    for i, product in enumerate(products[:3]):
                        logger.info(f"   {i+1}. {product.get('name', 'N/A')[:50]}... - {product.get('price', 'N/A')} ₸")
            else:
                logger.warning(f"⚠️ [TEST] Merchant ID не найден, пропускаем парсинг")
        else:
            logger.error(f"❌ [TEST] Авторизация не удалась")
            
    except Exception as e:
        logger.error(f"❌ [TEST] Критическая ошибка: {str(e)}")
        import traceback
        logger.error(f"🔍 [TEST] Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🧪 Запуск теста авторизации Kaspi с реальными данными...")
    asyncio.run(test_kaspi_auth())
