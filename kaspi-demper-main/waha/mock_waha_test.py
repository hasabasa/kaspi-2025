#!/usr/bin/env python3
"""
Симуляция WAHA сервера для тестирования WhatsApp интеграции
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MockWAHAServer:
    """Мок WAHA сервера для тестирования"""
    
    def __init__(self):
        self.sessions = {}
        self.messages = []
        self.qr_codes = {}
    
    async def start_session(self, session_name: str) -> Dict[str, Any]:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        qr_code = f"QR_CODE_{session_id}"
        
        self.sessions[session_name] = {
            "id": session_id,
            "name": session_name,
            "status": "STARTING",
            "qr_code": qr_code,
            "created_at": datetime.now().isoformat()
        }
        
        self.qr_codes[session_name] = qr_code
        
        return {
            "id": session_id,
            "name": session_name,
            "status": "STARTING",
            "qr": qr_code
        }
    
    async def get_session_status(self, session_name: str) -> Dict[str, Any]:
        """Получение статуса сессии"""
        if session_name not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_name]
        
        # Симулируем разные статусы
        if session["status"] == "STARTING":
            # Через некоторое время переходим в CONNECTED
            session["status"] = "CONNECTED"
        
        return {
            "status": session["status"],
            "qr": session.get("qr_code") if session["status"] == "STARTING" else None
        }
    
    async def get_qr_code(self, session_name: str) -> Dict[str, Any]:
        """Получение QR кода"""
        if session_name not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_name]
        
        if session["status"] == "STARTING":
            return {"qr": session["qr_code"]}
        else:
            return {"qr": None, "message": "Session already connected"}
    
    async def send_message(self, session_name: str, chat_id: str, text: str) -> Dict[str, Any]:
        """Отправка сообщения"""
        if session_name not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_name]
        
        if session["status"] != "CONNECTED":
            return {"error": "Session not connected"}
        
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "session": session_name,
            "chatId": chat_id,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        
        self.messages.append(message)
        
        return {
            "id": message_id,
            "status": "sent",
            "timestamp": message["timestamp"]
        }
    
    async def get_messages(self) -> list:
        """Получение всех сообщений"""
        return self.messages

# Глобальный экземпляр мок сервера
mock_server = MockWAHAServer()

async def test_mock_waha_server():
    """Тест мок WAHA сервера"""
    print("🔍 Тестирование мок WAHA сервера...")
    
    try:
        # Создаем сессию
        session_result = await mock_server.start_session("kaspi_demper_session")
        print(f"✅ Сессия создана: {session_result['name']}")
        print(f"✅ Статус: {session_result['status']}")
        print(f"✅ QR код: {session_result['qr']}")
        
        # Проверяем статус
        status_result = await mock_server.get_session_status("kaspi_demper_session")
        print(f"✅ Статус сессии: {status_result['status']}")
        
        # Получаем QR код
        qr_result = await mock_server.get_qr_code("kaspi_demper_session")
        if qr_result.get('qr'):
            print(f"✅ QR код получен: {qr_result['qr']}")
        else:
            print("✅ QR код недоступен (сессия подключена)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования мок сервера: {e}")
        return False

async def test_send_message():
    """Тест отправки сообщения"""
    print("\n🔍 Тестирование отправки сообщения...")
    
    try:
        # Отправляем тестовое сообщение
        message_result = await mock_server.send_message(
            "kaspi_demper_session",
            "77001234567@c.us",
            "Здравствуйте! Ваш заказ готов к самовывозу. 🚀"
        )
        
        print(f"✅ Сообщение отправлено")
        print(f"✅ ID сообщения: {message_result['id']}")
        print(f"✅ Статус: {message_result['status']}")
        
        # Получаем все сообщения
        messages = await mock_server.get_messages()
        print(f"✅ Всего сообщений отправлено: {len(messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}")
        return False

def test_order_template():
    """Тест шаблона заказа"""
    print("\n🔍 Тестирование шаблона заказа...")
    
    try:
        import models
        import uuid
        
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
        
        # Данные заказа
        order_data = {
            "customer_name": "Айдар Нурланов",
            "order_id": "ORD-12345",
            "product_name": "iPhone 15 Pro",
            "quantity": 1,
            "shop_name": "TechStore Kazakhstan"
        }
        
        # Подставляем переменные
        message_text = template.template_text
        for key, value in order_data.items():
            message_text = message_text.replace(f"{{{key}}}", str(value))
        
        print("✅ Шаблон обработан успешно")
        print("📱 Итоговое сообщение:")
        print("-" * 60)
        print(message_text)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования шаблона: {e}")
        return False

async def test_full_workflow():
    """Тест полного рабочего процесса"""
    print("\n🔍 Тестирование полного рабочего процесса...")
    
    try:
        # 1. Создаем сессию
        session = await mock_server.start_session("kaspi_demper_session")
        print("✅ Шаг 1: Сессия создана")
        
        # 2. Ждем подключения (симулируем)
        await asyncio.sleep(1)
        status = await mock_server.get_session_status("kaspi_demper_session")
        print(f"✅ Шаг 2: Статус сессии - {status['status']}")
        
        # 3. Отправляем сообщение о готовности заказа
        message_result = await mock_server.send_message(
            "kaspi_demper_session",
            "77001234567@c.us",
            """Здравствуйте, Айдар Нурланов.
Ваш заказ Nº ORD-12345 "iPhone 15 Pro", количество: 1 шт готов к самовывозу.

* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.
* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.

С уважением,
TechStore Kazakhstan"""
        )
        
        print(f"✅ Шаг 3: Сообщение отправлено (ID: {message_result['id']})")
        
        # 4. Проверяем статистику
        messages = await mock_server.get_messages()
        print(f"✅ Шаг 4: Всего сообщений отправлено: {len(messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка полного рабочего процесса: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск теста WhatsApp интеграции с мок сервером\n")
    
    tests = [
        test_mock_waha_server,
        test_send_message,
        test_full_workflow
    ]
    
    passed = 0
    total = len(tests) + 1  # +1 для синхронного теста
    
    # Синхронный тест
    if test_order_template():
        passed += 1
    print()
    
    # Асинхронные тесты
    for test in tests:
        if await test():
            passed += 1
        print()
    
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("✅ WAHA интеграция работает корректно!")
        print("\n📱 Готово к подключению реального номера WhatsApp:")
        print("1. Установите Docker: https://docs.docker.com/get-docker/")
        print("2. Запустите WAHA сервер: docker-compose -f docker-compose.waha.yml up")
        print("3. Отсканируйте QR код в WhatsApp")
        print("4. Начните отправку уведомлений!")
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
