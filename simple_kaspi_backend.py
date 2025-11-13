#!/usr/bin/env python3
"""
Простейший HTTP сервер для тестирования интеграции с фронтендом
"""

import json
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class KaspiHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == '/health':
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "cors_enabled": True
            }
        elif path == '/kaspi/stores':
            user_id = query.get('user_id', [None])[0]
            response = {
                "success": True,
                "stores": [
                    {
                        "id": "test-store-1",
                        "name": "Тестовый магазин",
                        "merchant_id": "test_merchant",
                        "is_active": True,
                        "products_count": 10,
                        "last_sync": datetime.now().isoformat()
                    }
                ] if user_id else []
            }
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = urlparse(self.path).path
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}
        
        if path == '/kaspi/auth':
            response = {
                "success": True,
                "store_id": str(uuid.uuid4()),
                "name": f"Магазин {data.get('email', 'test').split('@')[0]}",
                "message": "Магазин успешно подключен",
                "api_key": f"kaspi_{uuid.uuid4().hex[:16]}",
                "is_replaced": False
            }
        elif path.startswith('/kaspi/auth/sms/start'):
            response = {
                "session_id": str(uuid.uuid4())
            }
        elif path.startswith('/kaspi/auth/sms/verify'):
            response = {
                "success": True,
                "store_id": str(uuid.uuid4()),
                "message": "Магазин подключен через SMS",
                "is_replaced": False
            }
        else:
            response = {"success": True, "message": "OK"}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def run_server():
    server = HTTPServer(('localhost', 8010), KaspiHandler)
    print("🚀 Простой HTTP сервер запущен на http://localhost:8010")
    print("📡 Готов к тестированию интеграции с фронтендом")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
