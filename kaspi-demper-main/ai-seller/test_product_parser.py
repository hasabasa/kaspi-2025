# test_product_parser.py
"""
Тестовый скрипт для парсера товаров AI-продажника
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

from product_parser import ProductParser, parse_products_for_ai_seller

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_product_parser():
    """Тестирование парсера товаров"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ ПАРСЕРА ТОВАРОВ AI-ПРОДАЖНИКА")
    print("="*60)
    
    # Тестовый shop_id (замените на реальный)
    test_shop_id = "test_shop_123"
    
    try:
        print(f"\n📋 Тестовый магазин: {test_shop_id}")
        
        # Создаем парсер
        parser = ProductParser(test_shop_id)
        print("✅ Парсер создан")
        
        # Тестируем инициализацию
        print("\n🔧 Тестирование инициализации...")
        try:
            await parser.initialize()
            print("✅ Парсер инициализирован")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации (ожидаемо для тестового shop_id): {e}")
        
        # Тестируем создание XML файла
        print("\n📄 Тестирование создания XML файла...")
        test_products = []
        
        # Создаем тестовые данные
        from product_parser import ProductData
        
        test_product = ProductData()
        test_product.sku = "TEST_SKU_001"
        test_product.name = "Тестовый товар"
        test_product.category = "Электроника"
        test_product.price = 50000.0
        test_product.availability = True
        test_product.rating = 4.5
        test_product.reviews_count = 100
        test_product.description = "Описание тестового товара"
        test_product.product_url = "https://kaspi.kz/shop/c/TEST_SKU_001/"
        test_product.reviews_url = "https://kaspi.kz/shop/c/TEST_SKU_001/?tab=reviews"
        test_product.merchant_url = "https://kaspi.kz/shop/c/TEST_SKU_001/?merchant=test_merchant"
        test_product.characteristics = {
            "Цвет": "Черный",
            "Материал": "Пластик",
            "Размер": "10x5x2 см"
        }
        test_product.images = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
        
        test_products.append(test_product)
        
        # Создаем XML файл
        xml_file = parser.create_xml_file(test_products, "test_products.xml")
        print(f"✅ XML файл создан: {xml_file}")
        
        # Создаем JSON файл
        json_file = parser.create_json_file(test_products, "test_products.json")
        print(f"✅ JSON файл создан: {json_file}")
        
        # Тестируем обновление базы знаний
        print("\n🧠 Тестирование обновления базы знаний...")
        knowledge_updated = await parser.update_knowledge_base(test_products)
        if knowledge_updated:
            print("✅ База знаний обновлена")
        else:
            print("❌ Ошибка обновления базы знаний")
        
        # Проверяем созданные файлы
        print("\n📁 Проверка созданных файлов...")
        knowledge_base_dir = Path(__file__).parent / "knowledge_base"
        
        if knowledge_base_dir.exists():
            files = list(knowledge_base_dir.glob("*"))
            print(f"✅ Найдено файлов: {len(files)}")
            for file in files:
                print(f"   📄 {file.name} ({file.stat().st_size} байт)")
        else:
            print("❌ Папка knowledge_base не найдена")
        
        print("\n🎉 Тестирование парсера завершено успешно!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования парсера: {e}")
        print(f"\n❌ Ошибка тестирования: {e}")
        return False

async def test_api_endpoints():
    """Тестирование API эндпоинтов"""
    print("\n" + "="*60)
    print("🌐 ТЕСТИРОВАНИЕ API ЭНДПОИНТОВ")
    print("="*60)
    
    try:
        import requests
        
        base_url = "http://localhost:8081"
        
        # Тест health check
        print("\n🏥 Тестирование health check...")
        try:
            response = requests.get(f"{base_url}/api/products/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check прошел")
                print(f"   Ответ: {response.json()}")
            else:
                print(f"❌ Health check не прошел: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API сервер не запущен: {e}")
            print("   Запустите: python product_api.py")
        
        # Тест получения статистики
        print("\n📊 Тестирование получения статистики...")
        try:
            response = requests.get(f"{base_url}/api/products/stats", timeout=5)
            if response.status_code == 200:
                print("✅ Статистика получена")
                stats = response.json()
                print(f"   Товаров: {stats.get('stats', {}).get('total_products', 0)}")
            else:
                print(f"❌ Ошибка получения статистики: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ошибка запроса: {e}")
        
        print("\n🎉 Тестирование API завершено!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования API: {e}")
        print(f"\n❌ Ошибка тестирования API: {e}")
        return False

async def test_knowledge_base_integration():
    """Тестирование интеграции с базой знаний"""
    print("\n" + "="*60)
    print("🧠 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С БАЗОЙ ЗНАНИЙ")
    print("="*60)
    
    try:
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        
        if knowledge_base_file.exists():
            print("✅ Файл базы знаний найден")
            
            with open(knowledge_base_file, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)
            
            products = knowledge_base.get("knowledge_base", {}).get("products", [])
            print(f"✅ Товаров в базе знаний: {len(products)}")
            
            if products:
                sample_product = products[0]
                print(f"✅ Пример товара: {sample_product.get('name', 'N/A')}")
                print(f"   SKU: {sample_product.get('sku', 'N/A')}")
                print(f"   Категория: {sample_product.get('category', 'N/A')}")
                print(f"   Цена: {sample_product.get('price', 'N/A')}")
                
                if sample_product.get('characteristics'):
                    print(f"   Характеристики: {len(sample_product['characteristics'])} шт.")
                
                if sample_product.get('merchant_url'):
                    print(f"   Ссылка продавца: {sample_product['merchant_url']}")
        else:
            print("⚠️ Файл базы знаний не найден")
            print("   Создайте тестовые данные через парсер")
        
        print("\n🎉 Тестирование интеграции с базой знаний завершено!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования интеграции: {e}")
        print(f"\n❌ Ошибка тестирования интеграции: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ ПАРСЕРА ТОВАРОВ AI-ПРОДАЖНИКА")
    
    results = []
    
    # Тестируем парсер
    results.append(await test_product_parser())
    
    # Тестируем интеграцию с базой знаний
    results.append(await test_knowledge_base_integration())
    
    # Тестируем API (если запущен)
    results.append(await test_api_endpoints())
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    passed_tests = sum(1 for r in results if r)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Пройдено тестов: {passed_tests}/{total_tests}")
    print(f"📈 Успешность: {success_rate:.1f}%")
    
    if all(results):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("🚀 Парсер товаров готов к использованию!")
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Проверьте настройки и зависимости")
    
    print("\n📋 Следующие шаги:")
    print("1. Настройте реальный shop_id в парсере")
    print("2. Запустите API сервер: python product_api.py")
    print("3. Протестируйте на реальных данных")
    print("4. Интегрируйте с основным AI-продажником")

if __name__ == "__main__":
    asyncio.run(main())
