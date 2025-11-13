#!/usr/bin/env python3
"""
Локальный веб-сервер для тестирования WAHA интеграции
"""

import asyncio
import json
import uuid
import webbrowser
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MockWAHAServer:
    """Мок WAHA сервер для локального тестирования"""
    
    def __init__(self):
        self.sessions = {}
        self.messages = []
        self.qr_codes = {}
        self.port = 3000
        
    def start_session(self, session_name: str) -> Dict[str, Any]:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        qr_code = f"WAHA_QR_{session_id[:16].upper()}"
        
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
    
    def get_session_status(self, session_name: str) -> Dict[str, Any]:
        """Получение статуса сессии"""
        if session_name not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_name]
        
        # Симулируем подключение через некоторое время
        if session["status"] == "STARTING":
            # В реальном приложении здесь будет проверка подключения
            session["status"] = "CONNECTED"
        
        return {
            "status": session["status"],
            "qr": session.get("qr_code") if session["status"] == "STARTING" else None
        }
    
    def get_qr_code(self, session_name: str) -> Dict[str, Any]:
        """Получение QR кода"""
        if session_name not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_name]
        
        if session["status"] == "STARTING":
            return {"qr": session["qr_code"]}
        else:
            return {"qr": None, "message": "Session already connected"}
    
    def send_message(self, session_name: str, chat_id: str, text: str) -> Dict[str, Any]:
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
    
    def get_messages(self) -> list:
        """Получение всех сообщений"""
        return self.messages

# Глобальный экземпляр мок сервера
mock_server = MockWAHAServer()

class WAHARequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов для WAHA API"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')
        
        try:
            if path_parts[2] == 'health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
                
            elif path_parts[2] == 'sessions':
                if len(path_parts) >= 5:
                    session_name = path_parts[3]
                    action = path_parts[4]
                    
                    if action == 'status':
                        result = mock_server.get_session_status(session_name)
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        
                    elif action == 'qr':
                        result = mock_server.get_qr_code(session_name)
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        
                    elif action == 'messages':
                        result = mock_server.get_messages()
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        
                    else:
                        self.send_error(404)
                else:
                    self.send_error(404)
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')
        
        try:
            if path_parts[2] == 'sessions' and path_parts[3] == 'start':
                # Создание сессии
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                session_name = data.get('name', 'default_session')
                result = mock_server.start_session(session_name)
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            elif path_parts[2] == 'sendText':
                # Отправка сообщения
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                session_name = data.get('session')
                chat_id = data.get('chatId')
                text = data.get('text')
                
                result = mock_server.send_message(session_name, chat_id, text)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        """Отключение логов"""
        pass

def start_web_server():
    """Запуск веб-сервера"""
    server = HTTPServer(('localhost', 3000), WAHARequestHandler)
    print(f"🚀 WAHA мок сервер запущен на http://localhost:3000")
    print(f"📱 API доступен по адресу: http://localhost:3000/api/")
    server.serve_forever()

def test_whatsapp_connection():
    """Тест подключения WhatsApp"""
    print("\n🔍 Тестирование подключения WhatsApp...")
    
    # Создаем сессию
    session_result = mock_server.start_session("kaspi_demper_session")
    print(f"✅ Сессия создана: {session_result['name']}")
    print(f"✅ QR код: {session_result['qr']}")
    
    # Получаем QR код
    qr_result = mock_server.get_qr_code("kaspi_demper_session")
    if qr_result.get('qr'):
        print(f"✅ QR код получен: {qr_result['qr']}")
        print("\n📱 Инструкции для подключения:")
        print("1. Откройте WhatsApp на телефоне")
        print("2. Перейдите в Настройки → Связанные устройства")
        print("3. Нажмите 'Связать устройство'")
        print("4. Отсканируйте QR код")
        print(f"5. QR код: {qr_result['qr']}")
    
    # Проверяем статус
    status_result = mock_server.get_session_status("kaspi_demper_session")
    print(f"✅ Статус сессии: {status_result['status']}")
    
    return True

def test_send_message():
    """Тест отправки сообщения"""
    print("\n📤 Тестирование отправки сообщения...")
    
    # Отправляем тестовое сообщение
    message_result = mock_server.send_message(
        "kaspi_demper_session",
        "77001234567@c.us",
        "Здравствуйте! Ваш заказ готов к самовывозу. 🚀"
    )
    
    print(f"✅ Сообщение отправлено")
    print(f"✅ ID сообщения: {message_result['id']}")
    print(f"✅ Статус: {message_result['status']}")
    
    return True

def test_order_notification():
    """Тест уведомления о заказе"""
    print("\n🛍️ Тестирование уведомления о заказе...")
    
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
            "order_id": "KASPI-ORD-2024-001",
            "product_name": "iPhone 15 Pro 256GB Space Black",
            "quantity": 1,
            "shop_name": "TechStore Kazakhstan"
        }
        
        # Подставляем переменные
        message_text = template.template_text
        for key, value in order_data.items():
            message_text = message_text.replace(f"{{{key}}}", str(value))
        
        print("📱 Готовое сообщение:")
        print("=" * 60)
        print(message_text)
        print("=" * 60)
        
        # Отправляем сообщение
        result = mock_server.send_message(
            "kaspi_demper_session",
            "77001234567@c.us",
            message_text
        )
        
        if result.get('id'):
            print("✅ Уведомление о заказе отправлено успешно!")
            return True
        else:
            print(f"❌ Ошибка отправки: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка тестирования уведомления: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Запуск локального WAHA сервера для тестирования")
    print("=" * 60)
    
    # Запускаем тесты
    tests = [
        test_whatsapp_connection,
        test_send_message,
        test_order_notification
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("✅ WAHA сервер готов к работе!")
        
        print("\n🌐 Веб-интерфейс доступен по адресам:")
        print("📱 API: http://localhost:3000/api/")
        print("🔍 Health: http://localhost:3000/api/health")
        print("📊 Sessions: http://localhost:3000/api/sessions/")
        
        print("\n📱 Команды для тестирования:")
        print("# Создать сессию:")
        print('curl -X POST http://localhost:3000/api/sessions/start \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"name": "kaspi_demper_session"}\'')
        print()
        print("# Получить QR код:")
        print("curl http://localhost:3000/api/sessions/kaspi_demper_session/qr")
        print()
        print("# Проверить статус:")
        print("curl http://localhost:3000/api/sessions/kaspi_demper_session/status")
        print()
        print("# Отправить сообщение:")
        print('curl -X POST http://localhost:3000/api/sendText \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"session": "kaspi_demper_session", "chatId": "77001234567@c.us", "text": "Тест!"}\'')
        
        print("\n🚀 Запуск веб-сервера...")
        
        # Запускаем веб-сервер в отдельном потоке
        server_thread = threading.Thread(target=start_web_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Открываем браузер
        try:
            webbrowser.open('http://localhost:3000/api/health')
        except:
            pass
        
        print("\n⏳ Сервер работает... Нажмите Ctrl+C для остановки")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
        
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
