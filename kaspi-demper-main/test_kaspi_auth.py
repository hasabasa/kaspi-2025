#!/usr/bin/env python3
"""
Тестовый скрипт для проверки аутентификации Kaspi
"""
import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append('/Users/hasen/demper-667-45/kaspi-demper-main/backend')

from api_parser import login_and_get_merchant_info

async def test_kaspi_auth():
    """Тестирует аутентификацию с предоставленными учетными данными"""
    email = "hvsv1@icloud.com"
    password = "CIoD29g8U1"
    user_id = "test-user-123"
    
    print(f"🔐 Тестируем аутентификацию Kaspi...")
    print(f"📧 Email: {email}")
    print(f"👤 User ID: {user_id}")
    
    try:
        # Вызываем функцию аутентификации
        result = await login_and_get_merchant_info(email, password, user_id)
        
        if result:
            cookie_jar, merchant_uid, shop_name, guid = result
            
            print("✅ Аутентификация успешна!")
            print(f"🏪 Merchant ID: {merchant_uid}")
            print(f"🏬 Название магазина: {shop_name}")
            print(f"🔑 GUID: {guid}")
            print(f"🍪 Cookies: {len(cookie_jar) if cookie_jar else 0} cookies")
            
            return True
        else:
            print("❌ Аутентификация не удалась")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при аутентификации: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_kaspi_auth())
    sys.exit(0 if success else 1)

