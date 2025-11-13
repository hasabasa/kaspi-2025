#!/usr/bin/env python3
"""
Тест парсинга данных Kaspi с подробными логами
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Добавляем путь к kaspi-demper-main
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'kaspi-demper-main', 'backend'))

import asyncio
import logging
from api_parser import parse_product_by_sku

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_kaspi_parsing():
    """Тест парсинга данных Kaspi"""
    print("🔍 Тестируем парсинг данных Kaspi...")
    
    # Тестовый SKU (можно заменить на реальный)
    test_sku = "123456789"
    
    try:
        print(f"📦 Тестируем парсинг для SKU: {test_sku}")
        
        # Вызываем функцию парсинга
        result = await parse_product_by_sku(test_sku)
        
        print(f"📊 Результат парсинга:")
        print(f"  Количество предложений: {len(result)}")
        
        if result:
            print("💰 Найденные предложения:")
            for i, offer in enumerate(result):
                print(f"    {i+1}. Merchant ID: {offer.get('merchant_id')}, Цена: {offer.get('price')}")
        else:
            print("⚠️ Предложения не найдены")
        
        return len(result) > 0
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_kaspi_parsing())
    print(f"\n{'✅ Тест успешен' if success else '❌ Тест провален'}")
    sys.exit(0 if success else 1)
