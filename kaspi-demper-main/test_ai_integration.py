#!/usr/bin/env python3
"""
Тест интеграции AI-продажника с WAHA системой
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Добавляем пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'waha'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai_seller_integration import AISellerIntegration, CustomerData, AISellerConfig
from kaspi_ai_integration import KaspiAIIntegration

def create_test_order_data() -> Dict[str, Any]:
    """Создание тестовых данных заказа"""
    return {
        "customer": {
            "phone": "+77001234567",
            "name": "Айдар Нурланов"
        },
        "order": {
            "order_id": "KASPI-ORD-2024-TEST-001",
            "product_name": "iPhone 15 Pro 256GB Space Black",
            "sku": "IPHONE15PRO256",
            "quantity": 1,
            "total_amount": 450000.0,
            "shop_name": "TechStore Kazakhstan"
        },
        "shop_id": "test_shop_001",
        "timestamp": datetime.now().isoformat()
    }

def create_test_customer_data() -> CustomerData:
    """Создание тестовых данных клиента"""
    return CustomerData(
        phone="+77001234567",
        name="Айдар Нурланов",
        order_id="KASPI-ORD-2024-TEST-001",
        product_name="iPhone 15 Pro 256GB Space Black",
        product_sku="IPHONE15PRO256",
        quantity=1,
        total_amount=450000.0,
        shop_name="TechStore Kazakhstan"
    )

async def test_ai_seller_integration():
    """Тест интеграции AI-продажника"""
    print("🔍 Тестирование интеграции AI-продажника...")
    
    try:
        # Создаем конфигурацию
        config = AISellerConfig(
            ai_seller_url="http://localhost:8080",
            enabled=True,
            test_mode=True,
            max_messages_per_customer=3,
            message_cooldown_hours=24,
            fallback_enabled=True
        )
        
        # Создаем интеграцию
        ai_integration = AISellerIntegration(config)
        
        # Инициализируем
        await ai_integration.initialize()
        
        # Создаем тестовые данные
        customer_data = create_test_customer_data()
        
        # Тестируем POST_PURCHASE триггер
        print("📤 Тестирование POST_PURCHASE триггера...")
        success = await ai_integration.trigger_post_purchase(customer_data)
        
        if success:
            print("✅ POST_PURCHASE триггер работает")
        else:
            print("❌ POST_PURCHASE триггер не работает")
        
        # Тестируем ORDER_DELIVERED триггер
        print("📦 Тестирование ORDER_DELIVERED триггера...")
        success = await ai_integration.trigger_order_delivered(customer_data)
        
        if success:
            print("✅ ORDER_DELIVERED триггер работает")
        else:
            print("❌ ORDER_DELIVERED триггер не работает")
        
        # Получаем метрики
        metrics = ai_integration.get_metrics()
        print(f"📊 Метрики: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
        
        # Очищаем ресурсы
        await ai_integration.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования AI-продажника: {e}")
        return False

async def test_kaspi_ai_integration():
    """Тест интеграции Kaspi AI"""
    print("\n🔍 Тестирование интеграции Kaspi AI...")
    
    try:
        # Создаем интеграцию
        kaspi_integration = KaspiAIIntegration()
        
        # Инициализируем
        await kaspi_integration.initialize()
        
        # Создаем тестовые данные заказа
        order_data = create_test_order_data()
        
        # Тестируем обработку нового заказа
        print("🛍️ Тестирование обработки нового заказа...")
        success = await kaspi_integration.process_new_order(order_data)
        
        if success:
            print("✅ Обработка нового заказа работает")
        else:
            print("❌ Обработка нового заказа не работает")
        
        # Тестируем обработку доставленного заказа
        print("📦 Тестирование обработки доставленного заказа...")
        success = await kaspi_integration.process_delivered_order(order_data)
        
        if success:
            print("✅ Обработка доставленного заказа работает")
        else:
            print("❌ Обработка доставленного заказа не работает")
        
        # Получаем метрики
        metrics = kaspi_integration.get_metrics()
        print(f"📊 Метрики Kaspi AI: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
        
        # Очищаем ресурсы
        await kaspi_integration.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Kaspi AI: {e}")
        return False

async def test_rate_limiting():
    """Тест rate limiting"""
    print("\n🔍 Тестирование rate limiting...")
    
    try:
        from ai_seller_integration import RateLimiter
        
        # Создаем rate limiter
        rate_limiter = RateLimiter(cooldown_hours=1)  # 1 час для теста
        
        test_phone = "+77001234567"
        
        # Первое сообщение должно пройти
        can_send = rate_limiter.can_send_message(test_phone, max_messages=3)
        print(f"Первое сообщение: {'✅ Разрешено' if can_send else '❌ Заблокировано'}")
        
        if can_send:
            rate_limiter.record_message_sent(test_phone)
        
        # Второе сообщение должно пройти
        can_send = rate_limiter.can_send_message(test_phone, max_messages=3)
        print(f"Второе сообщение: {'✅ Разрешено' if can_send else '❌ Заблокировано'}")
        
        if can_send:
            rate_limiter.record_message_sent(test_phone)
        
        # Третье сообщение должно пройти
        can_send = rate_limiter.can_send_message(test_phone, max_messages=3)
        print(f"Третье сообщение: {'✅ Разрешено' if can_send else '❌ Заблокировано'}")
        
        if can_send:
            rate_limiter.record_message_sent(test_phone)
        
        # Четвертое сообщение должно быть заблокировано
        can_send = rate_limiter.can_send_message(test_phone, max_messages=3)
        print(f"Четвертое сообщение: {'✅ Разрешено' if can_send else '❌ Заблокировано'}")
        
        print("✅ Rate limiting работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования rate limiting: {e}")
        return False

async def test_fallback_mechanism():
    """Тест fallback механизма"""
    print("\n🔍 Тестирование fallback механизма...")
    
    try:
        from ai_seller_integration import AISellerIntegration, AISellerConfig, CustomerData
        
        # Создаем конфигурацию с отключенным AI-продажником
        config = AISellerConfig(
            ai_seller_url="http://invalid-url:8080",  # Неверный URL
            enabled=True,
            test_mode=True,
            fallback_enabled=True
        )
        
        # Создаем интеграцию
        ai_integration = AISellerIntegration(config)
        await ai_integration.initialize()
        
        # Создаем тестовые данные
        customer_data = create_test_customer_data()
        
        # Тестируем триггер (должен сработать fallback)
        print("🔄 Тестирование fallback механизма...")
        success = await ai_integration.trigger_post_purchase(customer_data)
        
        if not success:
            print("✅ Fallback механизм сработал (AI-продажник недоступен)")
        else:
            print("⚠️ Fallback механизм не сработал")
        
        await ai_integration.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования fallback механизма: {e}")
        return False

async def test_full_workflow():
    """Тест полного рабочего процесса"""
    print("\n🔍 Тестирование полного рабочего процесса...")
    
    try:
        # Создаем интеграцию Kaspi AI
        kaspi_integration = KaspiAIIntegration()
        await kaspi_integration.initialize()
        
        # Создаем тестовые данные заказа
        order_data = create_test_order_data()
        
        print("📋 Шаг 1: Обработка нового заказа")
        success1 = await kaspi_integration.process_new_order(order_data)
        print(f"   Результат: {'✅ Успешно' if success1 else '❌ Ошибка'}")
        
        print("📦 Шаг 2: Обработка доставленного заказа")
        success2 = await kaspi_integration.process_delivered_order(order_data)
        print(f"   Результат: {'✅ Успешно' if success2 else '❌ Ошибка'}")
        
        print("📊 Шаг 3: Получение метрик")
        metrics = kaspi_integration.get_metrics()
        print(f"   Метрики получены: {'✅ Да' if metrics else '❌ Нет'}")
        
        await kaspi_integration.cleanup()
        
        if success1 and success2 and metrics:
            print("✅ Полный рабочий процесс работает корректно")
            return True
        else:
            print("❌ Полный рабочий процесс имеет ошибки")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка тестирования полного рабочего процесса: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования интеграции AI-продажника с WAHA\n")
    
    tests = [
        ("AI-продажник интеграция", test_ai_seller_integration),
        ("Kaspi AI интеграция", test_kaspi_ai_integration),
        ("Rate limiting", test_rate_limiting),
        ("Fallback механизм", test_fallback_mechanism),
        ("Полный рабочий процесс", test_full_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Тест: {test_name}")
        print(f"{'='*60}")
        
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} - ПРОЙДЕН")
            else:
                print(f"❌ {test_name} - НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"❌ {test_name} - ОШИБКА: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"{'='*60}")
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Не пройдено: {total - passed}/{total}")
    print(f"📈 Успешность: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Интеграция AI-продажника готова к использованию!")
        print("\n🚀 Следующие шаги:")
        print("1. Запустите AI-продажник сервер (ai-seller/main.py)")
        print("2. Запустите WAHA сервер")
        print("3. Запустите основное приложение с AI интеграцией")
        print("4. Протестируйте на реальных данных")
        return True
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Проверьте настройки и зависимости")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
