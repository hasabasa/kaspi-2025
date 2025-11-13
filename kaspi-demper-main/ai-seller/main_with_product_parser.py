# main_with_product_parser.py
"""
Обновленный AI-продажник с интеграцией парсера товаров
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, request, jsonify
import openai
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

# Импорты для парсера товаров
from product_parser import ProductParser, parse_products_for_ai_seller
from knowledge_base_integration import (
    knowledge_base_integration,
    get_product_info,
    search_products_in_knowledge_base,
    get_product_recommendations_for_customer,
    generate_product_context_for_ai,
    get_sales_scripts_for_product
)

# --- 1. ИНИЦИАЛИЗАЦИЯ И НАСТРОЙКА ---

app = Flask(__name__)

# Загрузка базы знаний со сценариями
try:
    with open('knowledge_base.json', 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)
    app.logger.info("База знаний 'knowledge_base.json' успешно загружена.")
except Exception as e:
    app.logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить knowledge_base.json: {e}")
    knowledge_base = {}

# Обязательные переменные окружения
REQUIRED_VARS = [
    "OPENAI_API_KEY", "WAHA_API_ENDPOINT", "WAHA_SESSION_ID",
    "FUNCTION_URL", "GOOGLE_SHEET_URL"
]
missing_vars = [v for v in REQUIRED_VARS if not os.environ.get(v)]
if missing_vars:
    raise RuntimeError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WAHA_API_ENDPOINT = os.environ["WAHA_API_ENDPOINT"]
WAHA_SESSION_ID = os.environ["WAHA_SESSION_ID"]
FUNCTION_URL = os.environ["FUNCTION_URL"]
GOOGLE_SHEET_URL = os.environ["GOOGLE_SHEET_URL"]

# Ключ-файл используется для аутентификации в Google
KEY_PATH = "kaspiseller-57379-firebase-adminsdk-fbsvc-1c22a63a88.json"

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Подключение к Google Sheets
try:
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
    app.logger.info("Подключение к Google Sheets успешно.")
except Exception as e:
    app.logger.error(f"ОШИБКА: Не удалось подключиться к Google Sheets: {e}")
    sheet = None

# --- 2. ФУНКЦИИ ДЛЯ РАБОТЫ С ПАРСЕРОМ ТОВАРОВ ---

async def update_products_knowledge_base(shop_id: str):
    """Обновление базы знаний товаров"""
    try:
        app.logger.info(f"Обновление базы знаний товаров для магазина: {shop_id}")
        
        # Запускаем парсинг товаров
        result = await parse_products_for_ai_seller(shop_id)
        
        if result.get("success"):
            app.logger.info(f"База знаний обновлена: {result.get('total_products', 0)} товаров")
            return True
        else:
            app.logger.error(f"Ошибка обновления базы знаний: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        app.logger.error(f"Ошибка обновления базы знаний: {e}")
        return False

def get_enhanced_product_context(product_sku: str, customer_data: dict = None) -> str:
    """Получение расширенного контекста о товаре для AI"""
    try:
        # Базовый контекст товара
        product_context = generate_product_context_for_ai(product_sku)
        
        # Получаем скрипты продаж
        sales_scripts = get_sales_scripts_for_product(product_sku)
        
        # Добавляем скрипты к контексту
        if sales_scripts:
            product_context += "\n\nСкрипты продаж:\n"
            for script in sales_scripts:
                product_context += f"- {script}\n"
        
        # Добавляем рекомендации, если есть данные о клиенте
        if customer_data and customer_data.get("order"):
            recommendations = get_product_recommendations_for_customer(customer_data["order"])
            if recommendations:
                product_context += "\n\nРекомендуемые товары:\n"
                for rec in recommendations[:3]:
                    product_context += f"- {rec.get('name', 'N/A')} ({rec.get('price', 'N/A')} тенге)\n"
        
        return product_context
        
    except Exception as e:
        app.logger.error(f"Ошибка получения контекста товара: {e}")
        return f"Информация о товаре {product_sku} недоступна"

# --- 3. ОБНОВЛЕННЫЕ ФУНКЦИИ AI ---

def generate_ai_response_with_products(stage_id: str, customer_data: dict, product_context: str = "") -> str:
    """Генерация ответа AI с учетом информации о товарах"""
    try:
        # Получаем сценарий для этапа
        scenario = knowledge_base.get("knowledge_base", {}).get("scenarios", {}).get(stage_id, {})
        
        if not scenario:
            return "Извините, я не могу обработать этот запрос."
        
        # Формируем промпт с учетом контекста товара
        prompt = f"""
Ты - AI-продажник для интернет-магазина на Kaspi.kz.

Этап: {stage_id}
Клиент: {customer_data.get('name', 'N/A')}
Телефон: {customer_data.get('phone', 'N/A')}

Контекст товара:
{product_context}

Сценарий для этого этапа:
{scenario.get('script', '')}

Инструкции:
- Используй информацию о товаре для персонализации сообщения
- Предлагай сопутствующие товары, если это уместно
- Будь дружелюбным и профессиональным
- Пиши на русском языке
- Максимум 200 символов

Ответ:
"""
        
        # Генерируем ответ через OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты - профессиональный продажник интернет-магазина."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        app.logger.error(f"Ошибка генерации AI ответа: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса."

# --- 4. ОБНОВЛЕННЫЕ API ЭНДПОИНТЫ ---

@app.route('/event_handler', methods=['POST'])
def handle_event_with_products():
    """Обработчик событий с интеграцией парсера товаров"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        stage_id = data.get('waha_stage_id')
        customer = data.get('customer', {})
        order = data.get('order', {})
        
        app.logger.info(f"Получено событие: {stage_id} для клиента {customer.get('name', 'N/A')}")
        
        # Получаем контекст товара, если есть SKU в заказе
        product_context = ""
        if order.get('product_sku'):
            product_context = get_enhanced_product_context(order['product_sku'], data)
        
        # Генерируем ответ AI
        ai_response = generate_ai_response_with_products(stage_id, customer, product_context)
        
        # Отправляем сообщение через WAHA
        message_sent = send_whatsapp_message(customer.get('phone', ''), ai_response)
        
        # Сохраняем в Google Sheets
        if sheet:
            save_to_sheets(stage_id, customer, order, ai_response, message_sent)
        
        return jsonify({
            "status": "success",
            "message": ai_response,
            "sent": message_sent,
            "product_context_used": bool(product_context)
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка обработки события: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/parse/<shop_id>', methods=['POST'])
def trigger_product_parsing(shop_id: str):
    """Запуск парсинга товаров для магазина"""
    try:
        # Запускаем парсинг в фоновом режиме
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(update_products_knowledge_base(shop_id))
        
        return jsonify({
            "success": result,
            "message": "Парсинг товаров запущен" if result else "Ошибка парсинга товаров",
            "shop_id": shop_id
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка запуска парсинга: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/search', methods=['POST'])
def search_products_api():
    """API для поиска товаров в базе знаний"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        category = data.get('category', '')
        
        results = search_products_in_knowledge_base(query, category)
        
        return jsonify({
            "success": True,
            "query": query,
            "category": category,
            "results": results,
            "total_found": len(results)
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка поиска товаров: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/recommendations', methods=['POST'])
def get_product_recommendations_api():
    """API для получения рекомендаций товаров"""
    try:
        data = request.get_json()
        customer_order = data.get('order', {})
        
        recommendations = get_product_recommendations_for_customer(customer_order)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка получения рекомендаций: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/knowledge-base/stats', methods=['GET'])
def get_knowledge_base_stats():
    """Получение статистики базы знаний товаров"""
    try:
        stats = knowledge_base_integration.get_knowledge_base_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({"error": str(e)}), 500

# --- 5. СУЩЕСТВУЮЩИЕ ФУНКЦИИ (без изменений) ---

def send_whatsapp_message(phone: str, message: str) -> bool:
    """Отправка сообщения через WAHA"""
    try:
        url = f"{WAHA_API_ENDPOINT}/api/sendText"
        payload = {
            "session": WAHA_SESSION_ID,
            "to": phone,
            "text": message
        }
        
        response = requests.post(url, json=payload)
        return response.status_code == 200
        
    except Exception as e:
        app.logger.error(f"Ошибка отправки WhatsApp сообщения: {e}")
        return False

def save_to_sheets(stage_id: str, customer: dict, order: dict, ai_response: str, message_sent: bool):
    """Сохранение данных в Google Sheets"""
    try:
        if not sheet:
            return
        
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stage_id,
            customer.get('name', ''),
            customer.get('phone', ''),
            order.get('product_name', ''),
            order.get('product_sku', ''),
            ai_response,
            "Да" if message_sent else "Нет"
        ]
        
        sheet.append_row(row)
        
    except Exception as e:
        app.logger.error(f"Ошибка сохранения в Google Sheets: {e}")

# --- 6. ПЛАНИРОВЩИК ЗАДАЧ ---

def scheduled_product_update():
    """Планируемое обновление базы знаний товаров"""
    try:
        # Получаем shop_id из переменных окружения или используем дефолтный
        shop_id = os.environ.get("KASPI_SHOP_ID", "default_shop")
        
        # Запускаем обновление в фоновом режиме
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(update_products_knowledge_base(shop_id))
        
        app.logger.info(f"Планируемое обновление товаров завершено: {result}")
        
    except Exception as e:
        app.logger.error(f"Ошибка планируемого обновления товаров: {e}")

# Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=scheduled_product_update,
    trigger="interval",
    hours=24,  # Обновляем каждый день
    id='product_update_job'
)
scheduler.start()

# --- 7. ЗАПУСК ПРИЛОЖЕНИЯ ---

if __name__ == '__main__':
    app.logger.info("AI-продажник с парсером товаров запущен")
    app.run(host='0.0.0.0', port=8080, debug=True)
