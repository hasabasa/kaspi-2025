# knowledge_base_integration.py
"""
Интеграция парсера товаров с базой знаний AI-продажника
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class KnowledgeBaseIntegration:
    """Интеграция с базой знаний AI-продажника"""
    
    def __init__(self):
        self.knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Загрузка базы знаний"""
        try:
            if self.knowledge_base_file.exists():
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем базовую структуру
                return {
                    "knowledge_base": {
                        "products": [],
                        "scenarios": [],
                        "scripts": []
                    }
                }
        except Exception as e:
            logger.error(f"Ошибка загрузки базы знаний: {e}")
            return {"knowledge_base": {"products": [], "scenarios": [], "scripts": []}}
    
    def save_knowledge_base(self):
        """Сохранение базы знаний"""
        try:
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            logger.info("База знаний сохранена")
        except Exception as e:
            logger.error(f"Ошибка сохранения базы знаний: {e}")
    
    def add_product(self, product_data: Dict[str, Any]):
        """Добавление товара в базу знаний"""
        try:
            if "products" not in self.knowledge_base["knowledge_base"]:
                self.knowledge_base["knowledge_base"]["products"] = []
            
            # Проверяем, есть ли уже такой товар
            existing_products = self.knowledge_base["knowledge_base"]["products"]
            for i, existing_product in enumerate(existing_products):
                if existing_product.get("sku") == product_data.get("sku"):
                    # Обновляем существующий товар
                    existing_products[i] = product_data
                    logger.info(f"Товар {product_data.get('sku')} обновлен")
                    return
            
            # Добавляем новый товар
            existing_products.append(product_data)
            logger.info(f"Товар {product_data.get('sku')} добавлен")
            
        except Exception as e:
            logger.error(f"Ошибка добавления товара: {e}")
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Получение товара по SKU"""
        try:
            products = self.knowledge_base["knowledge_base"].get("products", [])
            for product in products:
                if product.get("sku") == sku:
                    return product
            return None
        except Exception as e:
            logger.error(f"Ошибка поиска товара по SKU: {e}")
            return None
    
    def search_products(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Поиск товаров по запросу"""
        try:
            products = self.knowledge_base["knowledge_base"].get("products", [])
            results = []
            
            query_lower = query.lower()
            
            for product in products:
                name_match = query_lower in product.get("name", "").lower()
                category_match = not category or category.lower() in product.get("category", "").lower()
                
                if name_match and category_match:
                    results.append(product)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска товаров: {e}")
            return []
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Получение товаров по категории"""
        try:
            products = self.knowledge_base["knowledge_base"].get("products", [])
            return [p for p in products if category.lower() in p.get("category", "").lower()]
        except Exception as e:
            logger.error(f"Ошибка получения товаров по категории: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Получение списка категорий"""
        try:
            products = self.knowledge_base["knowledge_base"].get("products", [])
            categories = set()
            for product in products:
                category = product.get("category", "")
                if category:
                    categories.add(category)
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"Ошибка получения категорий: {e}")
            return []
    
    def get_product_recommendations(self, customer_order: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение рекомендаций товаров на основе заказа клиента"""
        try:
            ordered_product_sku = customer_order.get("product_sku")
            ordered_product = self.get_product_by_sku(ordered_product_sku)
            
            if not ordered_product:
                return []
            
            ordered_category = ordered_product.get("category", "")
            ordered_price = ordered_product.get("price", 0)
            
            # Ищем товары в той же категории с похожей ценой
            recommendations = []
            products = self.knowledge_base["knowledge_base"].get("products", [])
            
            for product in products:
                if product.get("sku") == ordered_product_sku:
                    continue
                
                product_category = product.get("category", "")
                product_price = product.get("price", 0)
                
                # Проверяем совпадение категории и ценового диапазона
                if (product_category == ordered_category and 
                    abs(product_price - ordered_price) <= ordered_price * 0.5):
                    recommendations.append(product)
            
            # Сортируем по рейтингу
            recommendations.sort(key=lambda x: x.get("rating", 0), reverse=True)
            
            return recommendations[:5]  # Возвращаем топ-5 рекомендаций
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            return []
    
    def generate_product_context(self, product_sku: str) -> str:
        """Генерация контекста о товаре для AI"""
        try:
            product = self.get_product_by_sku(product_sku)
            if not product:
                return f"Товар с SKU {product_sku} не найден в базе знаний"
            
            context = f"""
Товар: {product.get('name', 'N/A')}
Категория: {product.get('category', 'N/A')}
Цена: {product.get('price', 'N/A')} тенге
Рейтинг: {product.get('rating', 'N/A')}/5
Количество отзывов: {product.get('reviews_count', 'N/A')}
Описание: {product.get('description', 'N/A')}
"""
            
            if product.get('characteristics'):
                context += "\nХарактеристики:\n"
                for name, value in product['characteristics'].items():
                    context += f"- {name}: {value}\n"
            
            return context.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации контекста: {e}")
            return f"Ошибка получения информации о товаре {product_sku}"
    
    def get_sales_scripts_for_product(self, product_sku: str) -> List[str]:
        """Получение скриптов продаж для товара"""
        try:
            product = self.get_product_by_sku(product_sku)
            if not product:
                return []
            
            category = product.get("category", "")
            price = product.get("price", 0)
            rating = product.get("rating", 0)
            
            scripts = []
            
            # Скрипты на основе категории
            if "электроника" in category.lower():
                scripts.extend([
                    "Этот товар из категории электроники имеет высокое качество и современные технологии.",
                    "Электронные товары нашего магазина проходят строгий контроль качества.",
                    "Мы предлагаем гарантию на всю электронику в нашем магазине."
                ])
            
            # Скрипты на основе цены
            if price > 100000:
                scripts.extend([
                    "Это премиум товар с отличным соотношением цена-качество.",
                    "Для дорогих товаров мы предлагаем рассрочку и специальные условия."
                ])
            elif price < 10000:
                scripts.extend([
                    "Отличное предложение по доступной цене!",
                    "Этот товар идеально подходит для тех, кто ищет качество за разумные деньги."
                ])
            
            # Скрипты на основе рейтинга
            if rating >= 4.5:
                scripts.extend([
                    "Этот товар имеет отличные отзывы покупателей!",
                    "Высокий рейтинг подтверждает качество товара."
                ])
            
            return scripts
            
        except Exception as e:
            logger.error(f"Ошибка получения скриптов продаж: {e}")
            return []
    
    def update_product_statistics(self, product_sku: str, event_type: str):
        """Обновление статистики товара"""
        try:
            product = self.get_product_by_sku(product_sku)
            if not product:
                return
            
            if "statistics" not in product:
                product["statistics"] = {
                    "views": 0,
                    "orders": 0,
                    "recommendations": 0,
                    "last_activity": None
                }
            
            if event_type == "view":
                product["statistics"]["views"] += 1
            elif event_type == "order":
                product["statistics"]["orders"] += 1
            elif event_type == "recommendation":
                product["statistics"]["recommendations"] += 1
            
            product["statistics"]["last_activity"] = datetime.now().isoformat()
            
            logger.info(f"Статистика товара {product_sku} обновлена: {event_type}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Получение статистики базы знаний"""
        try:
            products = self.knowledge_base["knowledge_base"].get("products", [])
            
            stats = {
                "total_products": len(products),
                "categories_count": len(self.get_categories()),
                "avg_price": sum(p.get("price", 0) for p in products) / len(products) if products else 0,
                "avg_rating": sum(p.get("rating", 0) for p in products) / len(products) if products else 0,
                "total_reviews": sum(p.get("reviews_count", 0) for p in products),
                "price_range": {
                    "min": min(p.get("price", 0) for p in products) if products else 0,
                    "max": max(p.get("price", 0) for p in products) if products else 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики базы знаний: {e}")
            return {}

# Глобальный экземпляр интеграции
knowledge_base_integration = KnowledgeBaseIntegration()

# Функции для использования в основном AI-продажнике
def get_product_info(product_sku: str) -> Optional[Dict[str, Any]]:
    """Получение информации о товаре"""
    return knowledge_base_integration.get_product_by_sku(product_sku)

def search_products_in_knowledge_base(query: str, category: str = None) -> List[Dict[str, Any]]:
    """Поиск товаров в базе знаний"""
    return knowledge_base_integration.search_products(query, category)

def get_product_recommendations_for_customer(customer_order: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Получение рекомендаций товаров для клиента"""
    return knowledge_base_integration.get_product_recommendations(customer_order)

def generate_product_context_for_ai(product_sku: str) -> str:
    """Генерация контекста о товаре для AI"""
    return knowledge_base_integration.generate_product_context(product_sku)

def get_sales_scripts_for_product(product_sku: str) -> List[str]:
    """Получение скриптов продаж для товара"""
    return knowledge_base_integration.get_sales_scripts_for_product(product_sku)

if __name__ == "__main__":
    # Тестирование интеграции
    print("🧠 Тестирование интеграции с базой знаний")
    
    # Создаем тестовый товар
    test_product = {
        "sku": "TEST_001",
        "name": "Тестовый товар",
        "category": "Электроника",
        "price": 50000,
        "rating": 4.5,
        "reviews_count": 100,
        "description": "Описание тестового товара",
        "characteristics": {
            "Цвет": "Черный",
            "Материал": "Пластик"
        }
    }
    
    # Добавляем товар
    knowledge_base_integration.add_product(test_product)
    
    # Тестируем поиск
    results = knowledge_base_integration.search_products("тестовый")
    print(f"Найдено товаров: {len(results)}")
    
    # Тестируем получение контекста
    context = knowledge_base_integration.generate_product_context("TEST_001")
    print(f"Контекст: {context[:100]}...")
    
    # Сохраняем базу знаний
    knowledge_base_integration.save_knowledge_base()
    
    print("✅ Тестирование завершено")
