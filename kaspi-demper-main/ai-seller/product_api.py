# product_api.py
"""
API для управления парсером товаров AI-продажника
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

from product_parser import ProductParser, parse_products_for_ai_seller

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Глобальное хранилище результатов парсинга
parsing_results = {}

@app.route('/api/products/parse/<shop_id>', methods=['POST'])
async def parse_products(shop_id: str):
    """
    Запуск парсинга товаров для указанного магазина
    """
    try:
        logger.info(f"Запуск парсинга товаров для магазина: {shop_id}")
        
        # Запускаем парсинг
        result = await parse_products_for_ai_seller(shop_id)
        
        # Сохраняем результат
        parsing_results[shop_id] = {
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "completed" if result.get("success") else "failed"
        }
        
        return jsonify({
            "success": True,
            "message": "Парсинг товаров запущен",
            "shop_id": shop_id,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Ошибка парсинга товаров: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/status/<shop_id>', methods=['GET'])
def get_parsing_status(shop_id: str):
    """
    Получение статуса парсинга товаров
    """
    try:
        if shop_id not in parsing_results:
            return jsonify({
                "success": False,
                "message": "Парсинг не найден"
            }), 404
        
        result_data = parsing_results[shop_id]
        
        return jsonify({
            "success": True,
            "shop_id": shop_id,
            "status": result_data["status"],
            "timestamp": result_data["timestamp"],
            "result": result_data["result"]
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/files/<shop_id>', methods=['GET'])
def get_product_files(shop_id: str):
    """
    Получение списка файлов с данными товаров
    """
    try:
        knowledge_base_dir = Path(__file__).parent / "knowledge_base"
        
        if not knowledge_base_dir.exists():
            return jsonify({
                "success": False,
                "message": "Папка с файлами не найдена"
            }), 404
        
        # Получаем список файлов
        files = []
        for file_path in knowledge_base_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "type": file_path.suffix
                })
        
        return jsonify({
            "success": True,
            "shop_id": shop_id,
            "files": files
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения файлов: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/knowledge-base', methods=['GET'])
def get_knowledge_base():
    """
    Получение текущей базы знаний товаров
    """
    try:
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        
        if not knowledge_base_file.exists():
            return jsonify({
                "success": False,
                "message": "База знаний не найдена"
            }), 404
        
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        return jsonify({
            "success": True,
            "knowledge_base": knowledge_base
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения базы знаний: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/knowledge-base', methods=['POST'])
def update_knowledge_base():
    """
    Обновление базы знаний товаров
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Данные не предоставлены"
            }), 400
        
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        
        # Сохраняем обновленную базу знаний
        with open(knowledge_base_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "message": "База знаний обновлена"
        })
        
    except Exception as e:
        logger.error(f"Ошибка обновления базы знаний: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/search', methods=['POST'])
def search_products():
    """
    Поиск товаров в базе знаний
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "message": "Запрос не предоставлен"
            }), 400
        
        query = data['query'].lower()
        category = data.get('category', '').lower()
        
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        
        if not knowledge_base_file.exists():
            return jsonify({
                "success": False,
                "message": "База знаний не найдена"
            }), 404
        
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        products = knowledge_base.get("knowledge_base", {}).get("products", [])
        
        # Поиск товаров
        results = []
        for product in products:
            name_match = query in product.get('name', '').lower()
            category_match = not category or category in product.get('category', '').lower()
            
            if name_match and category_match:
                results.append(product)
        
        return jsonify({
            "success": True,
            "query": data['query'],
            "category": data.get('category', ''),
            "results": results,
            "total_found": len(results)
        })
        
    except Exception as e:
        logger.error(f"Ошибка поиска товаров: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/categories', methods=['GET'])
def get_categories():
    """
    Получение списка категорий товаров
    """
    try:
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        
        if not knowledge_base_file.exists():
            return jsonify({
                "success": False,
                "message": "База знаний не найдена"
            }), 404
        
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        products = knowledge_base.get("knowledge_base", {}).get("products", [])
        
        # Собираем уникальные категории
        categories = set()
        for product in products:
            category = product.get('category', '')
            if category:
                categories.add(category)
        
        return jsonify({
            "success": True,
            "categories": sorted(list(categories)),
            "total_categories": len(categories)
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/stats', methods=['GET'])
def get_products_stats():
    """
    Получение статистики по товарам
    """
    try:
        knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        
        if not knowledge_base_file.exists():
            return jsonify({
                "success": False,
                "message": "База знаний не найдена"
            }), 404
        
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        products = knowledge_base.get("knowledge_base", {}).get("products", [])
        
        # Статистика
        stats = {
            "total_products": len(products),
            "categories_count": len(set(p.get('category', '') for p in products if p.get('category'))),
            "avg_price": sum(p.get('price', 0) for p in products) / len(products) if products else 0,
            "avg_rating": sum(p.get('rating', 0) for p in products) / len(products) if products else 0,
            "total_reviews": sum(p.get('reviews_count', 0) for p in products),
            "price_range": {
                "min": min(p.get('price', 0) for p in products) if products else 0,
                "max": max(p.get('price', 0) for p in products) if products else 0
            }
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products/health', methods=['GET'])
def health_check():
    """
    Проверка состояния API
    """
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Product Parser API"
    })

# Обработчик ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запуск сервера
    app.run(host='0.0.0.0', port=8081, debug=True)
