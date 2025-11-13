# product_parser.py
"""
Парсер товаров для AI-продажника
Получает данные о товарах продавца и создает XML файл для базы знаний
"""

import asyncio
import aiohttp
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import os
import sys
from pathlib import Path

# Добавляем путь к основному модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api_parser import SessionManager, get_products, parse_product_by_sku

logger = logging.getLogger(__name__)

class ProductData:
    """Класс для хранения данных о товаре"""
    
    def __init__(self):
        self.sku = ""
        self.name = ""
        self.category = ""
        self.price = 0.0
        self.characteristics = {}
        self.reviews_url = ""
        self.product_url = ""
        self.merchant_url = ""
        self.description = ""
        self.images = []
        self.availability = False
        self.rating = 0.0
        self.reviews_count = 0

class ProductParser:
    """Парсер товаров для AI-продажника"""
    
    def __init__(self, shop_id: str):
        self.shop_id = shop_id
        self.session_manager = SessionManager(shop_uid=shop_id)
        self.products_data = []
        self.output_dir = Path(__file__).parent / "knowledge_base"
        self.output_dir.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Инициализация парсера"""
        try:
            if not await self.session_manager.load():
                raise Exception("Не удалось загрузить сессию")
            logger.info(f"Парсер товаров инициализирован для магазина {self.shop_id}")
        except Exception as e:
            logger.error(f"Ошибка инициализации парсера: {e}")
            raise
    
    async def get_all_products(self) -> List[Dict[str, Any]]:
        """Получение всех товаров продавца"""
        try:
            cookies = self.session_manager.get_cookies()
            merchant_uid = self.session_manager.merchant_uid
            
            logger.info(f"Получение товаров для merchant_uid: {merchant_uid}")
            
            # Получаем все товары
            products = await get_products(cookies, merchant_uid, page_size=100)
            
            logger.info(f"Получено {len(products)} товаров")
            return products
            
        except Exception as e:
            logger.error(f"Ошибка получения товаров: {e}")
            return []
    
    async def parse_product_details(self, product: Dict[str, Any]) -> ProductData:
        """Парсинг детальной информации о товаре"""
        product_data = ProductData()
        
        try:
            # Базовые данные из API
            product_data.sku = product.get('sku', '')
            product_data.name = product.get('name', '')
            product_data.category = product.get('category', {}).get('name', '')
            product_data.price = float(product.get('price', 0))
            product_data.availability = product.get('available', False)
            product_data.description = product.get('description', '')
            
            # Ссылки
            product_data.product_url = f"https://kaspi.kz/shop/c/{product_data.sku}/"
            product_data.reviews_url = f"https://kaspi.kz/shop/c/{product_data.sku}/?tab=reviews"
            product_data.merchant_url = f"https://kaspi.kz/shop/c/{product_data.sku}/?merchant={self.session_manager.merchant_uid}"
            
            # Получаем дополнительные данные через API
            await self._enrich_product_data(product_data)
            
            logger.info(f"Обработан товар: {product_data.name} (SKU: {product_data.sku})")
            
        except Exception as e:
            logger.error(f"Ошибка парсинга товара {product.get('sku', 'unknown')}: {e}")
        
        return product_data
    
    async def _enrich_product_data(self, product_data: ProductData):
        """Обогащение данных товара дополнительной информацией"""
        try:
            # Получаем данные через API Kaspi
            offers_data = await parse_product_by_sku(product_data.sku)
            
            if offers_data:
                # Берем первое предложение (обычно самое релевантное)
                offer = offers_data[0] if offers_data else {}
                
                # Обновляем данные
                if 'rating' in offer:
                    product_data.rating = float(offer.get('rating', 0))
                
                if 'reviewsCount' in offer:
                    product_data.reviews_count = int(offer.get('reviewsCount', 0))
                
                # Характеристики товара
                if 'characteristics' in offer:
                    product_data.characteristics = self._parse_characteristics(offer['characteristics'])
                
                # Изображения
                if 'images' in offer:
                    product_data.images = self._parse_images(offer['images'])
            
        except Exception as e:
            logger.error(f"Ошибка обогащения данных для {product_data.sku}: {e}")
    
    def _parse_characteristics(self, characteristics_data: List[Dict]) -> Dict[str, str]:
        """Парсинг характеристик товара"""
        characteristics = {}
        
        try:
            for char in characteristics_data:
                if isinstance(char, dict) and 'name' in char and 'value' in char:
                    characteristics[char['name']] = char['value']
        except Exception as e:
            logger.error(f"Ошибка парсинга характеристик: {e}")
        
        return characteristics
    
    def _parse_images(self, images_data: List[Dict]) -> List[str]:
        """Парсинг изображений товара"""
        images = []
        
        try:
            for img in images_data:
                if isinstance(img, dict) and 'url' in img:
                    images.append(img['url'])
        except Exception as e:
            logger.error(f"Ошибка парсинга изображений: {e}")
        
        return images
    
    def create_xml_file(self, products_data: List[ProductData], filename: str = None) -> str:
        """Создание XML файла с данными товаров"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products_knowledge_base_{timestamp}.xml"
        
        filepath = self.output_dir / filename
        
        try:
            # Создаем корневой элемент
            root = ET.Element("products_knowledge_base")
            root.set("shop_id", self.shop_id)
            root.set("merchant_uid", self.session_manager.merchant_uid)
            root.set("created_at", datetime.now().isoformat())
            root.set("total_products", str(len(products_data)))
            
            # Добавляем метаданные
            metadata = ET.SubElement(root, "metadata")
            ET.SubElement(metadata, "shop_id").text = self.shop_id
            ET.SubElement(metadata, "merchant_uid").text = self.session_manager.merchant_uid
            ET.SubElement(metadata, "created_at").text = datetime.now().isoformat()
            ET.SubElement(metadata, "total_products").text = str(len(products_data))
            
            # Добавляем товары
            products_element = ET.SubElement(root, "products")
            
            for product in products_data:
                product_element = ET.SubElement(products_element, "product")
                
                # Основная информация
                ET.SubElement(product_element, "sku").text = product.sku
                ET.SubElement(product_element, "name").text = product.name
                ET.SubElement(product_element, "category").text = product.category
                ET.SubElement(product_element, "price").text = str(product.price)
                ET.SubElement(product_element, "availability").text = str(product.availability)
                ET.SubElement(product_element, "rating").text = str(product.rating)
                ET.SubElement(product_element, "reviews_count").text = str(product.reviews_count)
                ET.SubElement(product_element, "description").text = product.description
                
                # Ссылки
                links_element = ET.SubElement(product_element, "links")
                ET.SubElement(links_element, "product_url").text = product.product_url
                ET.SubElement(links_element, "reviews_url").text = product.reviews_url
                ET.SubElement(links_element, "merchant_url").text = product.merchant_url
                
                # Характеристики
                if product.characteristics:
                    characteristics_element = ET.SubElement(product_element, "characteristics")
                    for name, value in product.characteristics.items():
                        char_element = ET.SubElement(characteristics_element, "characteristic")
                        char_element.set("name", name)
                        char_element.text = value
                
                # Изображения
                if product.images:
                    images_element = ET.SubElement(product_element, "images")
                    for img_url in product.images:
                        ET.SubElement(images_element, "image").text = img_url
            
            # Сохраняем XML файл
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"XML файл создан: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Ошибка создания XML файла: {e}")
            raise
    
    def create_json_file(self, products_data: List[ProductData], filename: str = None) -> str:
        """Создание JSON файла с данными товаров"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products_knowledge_base_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            # Подготавливаем данные для JSON
            json_data = {
                "metadata": {
                    "shop_id": self.shop_id,
                    "merchant_uid": self.session_manager.merchant_uid,
                    "created_at": datetime.now().isoformat(),
                    "total_products": len(products_data)
                },
                "products": []
            }
            
            for product in products_data:
                product_dict = {
                    "sku": product.sku,
                    "name": product.name,
                    "category": product.category,
                    "price": product.price,
                    "availability": product.availability,
                    "rating": product.rating,
                    "reviews_count": product.reviews_count,
                    "description": product.description,
                    "links": {
                        "product_url": product.product_url,
                        "reviews_url": product.reviews_url,
                        "merchant_url": product.merchant_url
                    },
                    "characteristics": product.characteristics,
                    "images": product.images
                }
                json_data["products"].append(product_dict)
            
            # Сохраняем JSON файл
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON файл создан: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Ошибка создания JSON файла: {e}")
            raise
    
    async def update_knowledge_base(self, products_data: List[ProductData]) -> bool:
        """Обновление базы знаний AI-продажника"""
        try:
            # Создаем JSON файл для базы знаний
            json_file = self.create_json_file(products_data, "current_products.json")
            
            # Обновляем knowledge_base.json
            knowledge_base_file = Path(__file__).parent / "knowledge_base.json"
            
            if knowledge_base_file.exists():
                with open(knowledge_base_file, 'r', encoding='utf-8') as f:
                    knowledge_base = json.load(f)
            else:
                knowledge_base = {"knowledge_base": {"products": []}}
            
            # Добавляем данные о товарах
            if "products" not in knowledge_base["knowledge_base"]:
                knowledge_base["knowledge_base"]["products"] = []
            
            # Обновляем данные о товарах
            knowledge_base["knowledge_base"]["products"] = [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "category": p.category,
                    "price": p.price,
                    "characteristics": p.characteristics,
                    "merchant_url": p.merchant_url,
                    "reviews_url": p.reviews_url,
                    "rating": p.rating,
                    "reviews_count": p.reviews_count
                }
                for p in products_data
            ]
            
            # Сохраняем обновленную базу знаний
            with open(knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
            
            logger.info(f"База знаний обновлена: {knowledge_base_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления базы знаний: {e}")
            return False
    
    async def run_full_parsing(self) -> Dict[str, Any]:
        """Запуск полного парсинга товаров"""
        try:
            logger.info("Начало полного парсинга товаров")
            
            # Получаем все товары
            products = await self.get_all_products()
            
            if not products:
                logger.warning("Товары не найдены")
                return {"success": False, "message": "Товары не найдены"}
            
            # Парсим детали каждого товара
            products_data = []
            for i, product in enumerate(products):
                logger.info(f"Обработка товара {i+1}/{len(products)}")
                product_data = await self.parse_product_details(product)
                products_data.append(product_data)
                
                # Небольшая задержка между запросами
                await asyncio.sleep(0.5)
            
            # Создаем файлы
            xml_file = self.create_xml_file(products_data)
            json_file = self.create_json_file(products_data)
            
            # Обновляем базу знаний
            knowledge_updated = await self.update_knowledge_base(products_data)
            
            result = {
                "success": True,
                "total_products": len(products_data),
                "xml_file": xml_file,
                "json_file": json_file,
                "knowledge_base_updated": knowledge_updated,
                "products": [
                    {
                        "sku": p.sku,
                        "name": p.name,
                        "category": p.category,
                        "price": p.price,
                        "merchant_url": p.merchant_url
                    }
                    for p in products_data
                ]
            }
            
            logger.info(f"Парсинг завершен успешно: {len(products_data)} товаров")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка полного парсинга: {e}")
            return {"success": False, "error": str(e)}

# Функция для запуска парсинга
async def parse_products_for_ai_seller(shop_id: str) -> Dict[str, Any]:
    """Основная функция для парсинга товаров для AI-продажника"""
    parser = ProductParser(shop_id)
    
    try:
        await parser.initialize()
        result = await parser.run_full_parsing()
        return result
    except Exception as e:
        logger.error(f"Ошибка парсинга товаров: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Пример использования
    async def main():
        shop_id = "test_shop"  # Замените на реальный shop_id
        result = await parse_products_for_ai_seller(shop_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(main())
