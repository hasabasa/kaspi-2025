#!/usr/bin/env python3
"""
Тест подключения WhatsApp номера через WAHA
"""

import sys
import os
import uuid
import asyncio
import aiohttp
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_waha_server_connection():
    """Тест подключения к WAHA серверу"""
    print("🔍 Тестирование подключения к WAHA серверу...")
    
    waha_url = "http://localhost:3000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Проверяем статус сервера
            async with session.get(f"{waha_url}/api/health") as response:
                if response.status == 200:
                    print("✅ WAHA сервер доступен")
                    return True
                else:
                    print(f"❌ WAHA сервер недоступен (статус: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ Ошибка подключения к WAHA серверу: {e}")
        print("💡 Убедитесь, что WAHA сервер запущен на порту 3000")
        return False

async def test_create_session():
    """Тест создания сессии WAHA"""
    print("\n🔍 Тестирование создания сессии...")
    
    waha_url = "http://localhost:3000"
    session_name = "kaspi_demper_session"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Создаем сессию
            session_data = {
                "name": session_name,
                "config": {
                    "webhooks": [
                        {
                            "url": "http://localhost:8000/waha/webhook",
                            "events": ["message", "session.status"]
                        }
                    ]
                }
            }
            
            async with session.post(
                f"{waha_url}/api/sessions/start",
                json=session_data
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    print(f"✅ Сессия '{session_name}' создана успешно")
                    print(f"✅ Статус: {result.get('status', 'unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка создания сессии (статус: {response.status})")
                    print(f"❌ Ответ: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Ошибка создания сессии: {e}")
        return False

async def test_session_status():
    """Тест проверки статуса сессии"""
    print("\n🔍 Тестирование статуса сессии...")
    
    waha_url = "http://localhost:3000"
    session_name = "kaspi_demper_session"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{waha_url}/api/sessions/{session_name}/status") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Статус сессии: {result.get('status', 'unknown')}")
                    print(f"✅ QR код доступен: {result.get('qr', False)}")
                    return True
                else:
                    print(f"❌ Ошибка получения статуса (статус: {response.status})")
                    return False
                    
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

async def test_get_qr_code():
    """Тест получения QR кода для подключения"""
    print("\n🔍 Тестирование получения QR кода...")
    
    waha_url = "http://localhost:3000"
    session_name = "kaspi_demper_session"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{waha_url}/api/sessions/{session_name}/qr") as response:
                if response.status == 200:
                    result = await response.json()
                    qr_code = result.get('qr', '')
                    if qr_code:
                        print("✅ QR код получен успешно")
                        print("📱 Отсканируйте QR код в WhatsApp для подключения")
                        print(f"🔗 QR код: {qr_code[:50]}...")
                        return True
                    else:
                        print("⚠️  QR код пустой - возможно сессия уже подключена")
                        return True
                else:
                    print(f"❌ Ошибка получения QR кода (статус: {response.status})")
                    return False
                    
    except Exception as e:
        print(f"❌ Ошибка получения QR кода: {e}")
        return False

async def test_send_test_message():
    """Тест отправки тестового сообщения"""
    print("\n🔍 Тестирование отправки сообщения...")
    
    waha_url = "http://localhost:3000"
    session_name = "kaspi_demper_session"
    
    # Тестовый номер (замените на свой)
    test_phone = "77001234567@c.us"  # Формат WhatsApp
    
    try:
        async with aiohttp.ClientSession() as session:
            message_data = {
                "session": session_name,
                "chatId": test_phone,
                "text": "Тестовое сообщение от Kaspi Demper WAHA интеграции! 🚀"
            }
            
            async with session.post(
                f"{waha_url}/api/sendText",
                json=message_data
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    print(f"✅ Сообщение отправлено успешно")
                    print(f"✅ ID сообщения: {result.get('id', 'unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка отправки сообщения (статус: {response.status})")
                    print(f"❌ Ответ: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}")
        return False

def test_order_data_model():
    """Тест модели данных заказа"""
    print("\n🔍 Тестирование модели данных заказа...")
    
    try:
        import models
        
        # Создаем правильные данные заказа
        order = models.OrderData(
            customer_name="Айдар Нурланов",
            customer_phone="+77001234567",
            order_id="ORD-12345",
            product_name="iPhone 15 Pro",
            quantity=1,
            total_amount=450000.0,
            delivery_type="PICKUP",
            order_date=datetime.now().isoformat(),
            shop_name="TechStore Kazakhstan"
        )
        
        print("✅ Данные заказа созданы успешно")
        print(f"✅ Покупатель: {order.customer_name}")
        print(f"✅ Телефон: {order.customer_phone}")
        print(f"✅ Заказ: {order.order_id}")
        print(f"✅ Товар: {order.product_name}")
        print(f"✅ Сумма: {order.total_amount} тенге")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания данных заказа: {e}")
        return False

def test_message_template():
    """Тест шаблона сообщения с реальными данными"""
    print("\n🔍 Тестирование шаблона сообщения...")
    
    try:
        import models
        
        # Создаем шаблон
        template = models.WhatsAppTemplate(
            template_name="order_ready_template",
            template_text="""Здравствуйте, {customer_name}.
Ваш заказ Nº {order_id} "{product_name}", количество: {quantity} шт готов к самовывозу.

* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.
* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.

С уважением,
{shop_name}""",
            store_id=str(uuid.uuid4())
        )
        
        print("✅ Шаблон сообщения создан успешно")
        
        # Тестируем подстановку переменных
        test_data = {
            "customer_name": "Айдар Нурланов",
            "order_id": "ORD-12345",
            "product_name": "iPhone 15 Pro",
            "quantity": 1,
            "shop_name": "TechStore Kazakhstan"
        }
        
        # Простая подстановка переменных
        message_text = template.template_text
        for key, value in test_data.items():
            message_text = message_text.replace(f"{{{key}}}", str(value))
        
        print("✅ Подстановка переменных работает")
        print("📱 Пример сообщения:")
        print("-" * 50)
        print(message_text)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования шаблона: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск теста подключения WhatsApp номера\n")
    
    # Синхронные тесты
    sync_tests = [
        test_order_data_model,
        test_message_template
    ]
    
    # Асинхронные тесты
    async_tests = [
        test_waha_server_connection,
        test_create_session,
        test_session_status,
        test_get_qr_code,
        # test_send_test_message  # Раскомментируйте после подключения номера
    ]
    
    passed = 0
    total = len(sync_tests) + len(async_tests)
    
    # Запускаем синхронные тесты
    for test in sync_tests:
        if test():
            passed += 1
        print()
    
    # Запускаем асинхронные тесты
    for test in async_tests:
        if await test():
            passed += 1
        print()
    
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("✅ WAHA сервер готов к подключению номера!")
        print("\n📱 Следующие шаги:")
        print("1. Отсканируйте QR код в WhatsApp")
        print("2. Подтвердите подключение")
        print("3. Проверьте статус сессии")
        print("4. Отправьте тестовое сообщение")
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены")
        print("\n💡 Возможные решения:")
        print("1. Убедитесь, что WAHA сервер запущен")
        print("2. Проверьте доступность порта 3000")
        print("3. Проверьте настройки Docker")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
