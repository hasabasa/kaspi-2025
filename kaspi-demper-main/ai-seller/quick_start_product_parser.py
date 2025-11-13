#!/usr/bin/env python3
# quick_start_product_parser.py
"""
Быстрый запуск парсера товаров для AI-продажника
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

def print_banner():
    """Печать баннера"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🛍️  ПАРСЕР ТОВАРОВ AI-ПРОДАЖНИКА        ║
║                                                              ║
║  Автоматический парсинг товаров Kaspi.kz для базы знаний   ║
║  Создание XML/JSON файлов и интеграция с AI-продажником     ║
╚══════════════════════════════════════════════════════════════╝
""")

def print_menu():
    """Печать меню"""
    print("""
📋 ВЫБЕРИТЕ ДЕЙСТВИЕ:

1. 🚀 Запустить парсинг товаров
2. 🧪 Запустить тесты
3. 🌐 Запустить API сервер
4. 📊 Показать статистику базы знаний
5. 🔍 Поиск товаров
6. 📁 Показать файлы данных
7. ❌ Выход

""")

async def run_product_parsing():
    """Запуск парсинга товаров"""
    print("\n🚀 ЗАПУСК ПАРСИНГА ТОВАРОВ")
    print("="*50)
    
    shop_id = input("Введите Shop ID: ").strip()
    if not shop_id:
        print("❌ Shop ID не может быть пустым!")
        return
    
    try:
        from product_parser import parse_products_for_ai_seller
        
        print(f"📋 Парсинг товаров для магазина: {shop_id}")
        print("⏳ Это может занять несколько минут...")
        
        result = await parse_products_for_ai_seller(shop_id)
        
        if result.get("success"):
            print(f"\n✅ ПАРСИНГ ЗАВЕРШЕН УСПЕШНО!")
            print(f"📦 Обработано товаров: {result.get('total_products', 0)}")
            print(f"📄 XML файл: {result.get('xml_file', 'N/A')}")
            print(f"📄 JSON файл: {result.get('json_file', 'N/A')}")
            print(f"🧠 База знаний обновлена: {'Да' if result.get('knowledge_base_updated') else 'Нет'}")
            
            # Показываем примеры товаров
            products = result.get('products', [])
            if products:
                print(f"\n📋 ПРИМЕРЫ ТОВАРОВ:")
                for i, product in enumerate(products[:3]):
                    print(f"  {i+1}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')} тенге")
        else:
            print(f"\n❌ ОШИБКА ПАРСИНГА: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")

def run_tests():
    """Запуск тестов"""
    print("\n🧪 ЗАПУСК ТЕСТОВ")
    print("="*50)
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_product_parser.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Ошибки:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")

def run_api_server():
    """Запуск API сервера"""
    print("\n🌐 ЗАПУСК API СЕРВЕРА")
    print("="*50)
    print("API сервер будет доступен по адресу: http://localhost:8081")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "product_api.py"])
    except KeyboardInterrupt:
        print("\n🛑 API сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска API сервера: {e}")

def show_knowledge_base_stats():
    """Показать статистику базы знаний"""
    print("\n📊 СТАТИСТИКА БАЗЫ ЗНАНИЙ")
    print("="*50)
    
    try:
        from knowledge_base_integration import knowledge_base_integration
        
        stats = knowledge_base_integration.get_knowledge_base_stats()
        
        if stats:
            print(f"📦 Всего товаров: {stats.get('total_products', 0)}")
            print(f"📂 Категорий: {stats.get('categories_count', 0)}")
            print(f"💰 Средняя цена: {stats.get('avg_price', 0):.2f} тенге")
            print(f"⭐ Средний рейтинг: {stats.get('avg_rating', 0):.2f}/5")
            print(f"💬 Всего отзывов: {stats.get('total_reviews', 0)}")
            
            price_range = stats.get('price_range', {})
            print(f"💵 Диапазон цен: {price_range.get('min', 0):.2f} - {price_range.get('max', 0):.2f} тенге")
        else:
            print("❌ Статистика недоступна")
            
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")

def search_products():
    """Поиск товаров"""
    print("\n🔍 ПОИСК ТОВАРОВ")
    print("="*50)
    
    query = input("Введите поисковый запрос: ").strip()
    if not query:
        print("❌ Поисковый запрос не может быть пустым!")
        return
    
    category = input("Введите категорию (необязательно): ").strip()
    
    try:
        from knowledge_base_integration import search_products_in_knowledge_base
        
        results = search_products_in_knowledge_base(query, category if category else None)
        
        if results:
            print(f"\n✅ НАЙДЕНО ТОВАРОВ: {len(results)}")
            print("-" * 50)
            
            for i, product in enumerate(results[:10]):  # Показываем первые 10
                print(f"{i+1}. {product.get('name', 'N/A')}")
                print(f"   SKU: {product.get('sku', 'N/A')}")
                print(f"   Категория: {product.get('category', 'N/A')}")
                print(f"   Цена: {product.get('price', 'N/A')} тенге")
                print(f"   Рейтинг: {product.get('rating', 'N/A')}/5")
                print(f"   Ссылка: {product.get('merchant_url', 'N/A')}")
                print()
        else:
            print("❌ Товары не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")

def show_data_files():
    """Показать файлы данных"""
    print("\n📁 ФАЙЛЫ ДАННЫХ")
    print("="*50)
    
    try:
        knowledge_base_dir = Path(__file__).parent / "knowledge_base"
        
        if knowledge_base_dir.exists():
            files = list(knowledge_base_dir.glob("*"))
            
            if files:
                print(f"📂 Папка: {knowledge_base_dir}")
                print(f"📄 Найдено файлов: {len(files)}")
                print("-" * 50)
                
                for file in files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"📄 {file.name}")
                    print(f"   Размер: {size_mb:.2f} MB")
                    print(f"   Тип: {file.suffix}")
                    print()
            else:
                print("❌ Файлы не найдены")
        else:
            print("❌ Папка knowledge_base не найдена")
            
        # Проверяем основной файл базы знаний
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        if knowledge_base_file.exists():
            size_mb = knowledge_base_file.stat().st_size / (1024 * 1024)
            print(f"🧠 Основная база знаний: knowledge_base.json ({size_mb:.2f} MB)")
        else:
            print("❌ Основная база знаний не найдена")
            
    except Exception as e:
        print(f"❌ Ошибка получения информации о файлах: {e}")

async def main():
    """Основная функция"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("Введите номер действия (1-7): ").strip()
            
            if choice == "1":
                await run_product_parsing()
            elif choice == "2":
                run_tests()
            elif choice == "3":
                run_api_server()
            elif choice == "4":
                show_knowledge_base_stats()
            elif choice == "5":
                search_products()
            elif choice == "6":
                show_data_files()
            elif choice == "7":
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\nНажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа завершена.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
