import json
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
from fastapi import HTTPException
from core.logger import logger
from database.manager import DatabaseManager
from api_parser import SessionManager, get_formatted_cookies
import requests

OUTPUT_DIR = 'preorder_exports'
os.makedirs(OUTPUT_DIR, exist_ok=True)


class PreorderService:
    """Сервис для работы с предзаказами"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def fetch_preorders(self, store_id: str, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает предзаказы по store_id
        """
        try:
            logger.info(f"🔍 [PREORDERS] Получаем предзаказы для магазина: {store_id}")
            
            query = """
                SELECT id,
                       product_id,
                       store_id,
                       article,
                       name,
                       brand,
                       price,
                       status,
                       warehouses,
                       delivery_days,
                       created_at,
                       updated_at
                FROM preorders
                WHERE store_id = $1
                ORDER BY created_at DESC
                OFFSET $2 LIMIT COALESCE($3, 9223372036854775807)
            """
            
            rows = await self.db_manager.execute_query(query, store_id, offset, limit)
            
            result = []
            for row in rows:
                item = dict(row)
                
                if isinstance(item.get('warehouses'), str):
                    try:
                        item['warehouses'] = json.loads(item['warehouses'])
                    except (json.JSONDecodeError, TypeError):
                        item['warehouses'] = []
                elif item.get('warehouses') is None:
                    item['warehouses'] = []
                result.append(item)
            
            logger.info(f"✅ [PREORDERS] Найдено предзаказов: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ [PREORDERS] Ошибка получения предзаказов: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка получения предзаказов: {str(e)}")
    
    def generate_preorder_xlsx(self, preorders: List[Dict], store_id: str) -> str:
        """
        Генерирует .xlsx с колонками:
        SKU, model, brand, price, PP1, PP2, PP3, PP4, PP5, preorder
        Возвращает путь к файлу.
        """
        if not preorders:
            raise ValueError("No preorders data provided")
        
        df_data = []
        for preorder in preorders:
            row = {
                'SKU': preorder.get('sku', ''),
                'model': preorder.get('model', ''),
                'brand': preorder.get('brand', ''),
                'price': preorder.get('price', 0),
                'PP1': preorder.get('pp1', 0),
                'PP2': preorder.get('pp2', 0),
                'PP3': preorder.get('pp3', 0),
                'PP4': preorder.get('pp4', 0),
                'PP5': preorder.get('pp5', 0),
                'preorder': preorder.get('preorder', 0)
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        required_columns = ['SKU', 'model', 'brand', 'price', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5', 'preorder']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''

        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        filename = f"preorders_{store_id}_{timestamp}_{unique_id}.xlsx"
        filepath = os.path.join(OUTPUT_DIR, filename)

        df.to_excel(filepath, index=False)
        logger.info(f"✅ [PREORDERS] Excel сохранён: {filepath}")
        return filepath
    
    def process_preorders_for_excel(self, rows: List[Dict]) -> List[Dict]:
        """Обрабатывает предзаказы для Excel"""
        preorders_list = []
        for row in rows:
            wh_data = row.get('warehouses') or []
            if isinstance(wh_data, str):
                try:
                    wh_data = json.loads(wh_data)
                except json.JSONDecodeError:
                    wh_data = []
            
            counts = {f'pp{i}': 0 for i in range(1, 6)}
            total = 0
            for wh in wh_data:
                wid = wh.get('id')
                qty = wh.get('quantity', 0)
                key = f'pp{wid}'
                if key in counts:
                    counts[key] = qty
                    total += qty
            
            preorders_list.append({
                'sku': row.get('article', ''),
                'model': row.get('name', ''),
                'brand': row.get('brand', ''),
                'price': row.get('price', 0),
                **counts,
                'preorder': total
            })
        
        return preorders_list
    
    def upload_preorder_to_kaspi(self, filepath: str, merchant_uid: str, cookies: Dict[str, str]):
        """
        Заливает файл на Kaspi через multipart POST.
        """
        url = f"https://mc.shop.kaspi.kz/pricefeed/upload/merchant/upload?merchantUid={merchant_uid}"
        headers = {
            'Origin': 'https://kaspi.kz',
            'Referer': 'https://kaspi.kz/',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0'
            ),
        }
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (
                    os.path.basename(filepath), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                resp = requests.post(url, headers=headers, cookies=cookies, files=files, timeout=60)
            resp.raise_for_status()
            logger.info(f"📤 [PREORDERS] Успешно загружено на Kaspi, статус {resp.status_code}")
        except Exception as e:
            logger.error(f"❌ [PREORDERS] Ошибка загрузки на Kaspi: {e}")
            raise
    
    async def handle_upload_preorder(self, store_id: str):
        """Обрабатывает загрузку предзаказов на Kaspi"""
        try:
            logger.info(f"🚀 [PREORDERS] Начинаем загрузку предзаказов для магазина: {store_id}")
            
            # 1) Получаем предзаказы
            rows = await self.fetch_preorders(store_id)
            if not rows:
                logger.warning(f"⚠️ [PREORDERS] Нет предзаказов для магазина {store_id}")
                return

            # 2) Формируем список для Excel
            preorders_list = self.process_preorders_for_excel(rows)

            # 3) Генерируем и сохраняем файл с уникальным именем
            filepath = self.generate_preorder_xlsx(preorders_list, store_id)

            # 4) Загружаем на Kaspi, получая куки через SessionManager
            session_manager = SessionManager(shop_uid=store_id)
            if not await session_manager.load():
                raise HTTPException(status_code=400, detail="Сессия истекла, пожалуйста, войдите заново.")
            
            cookies = session_manager.get_cookies()
            merchant_id = session_manager.merchant_uid
            
            # 5) Загружаем файл на Kaspi
            self.upload_preorder_to_kaspi(filepath, merchant_id, cookies)
            
            logger.info(f"✅ [PREORDERS] Предзаказы для магазина {store_id} успешно загружены на Kaspi")
            
        except Exception as e:
            logger.error(f"❌ [PREORDERS] Ошибка при загрузке предзаказов для магазина {store_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка при загрузке предзаказов: {str(e)}")
    
    async def create_preorder_from_product(self, product: Dict[str, Any], store_id: str) -> Dict[str, Any]:
        """
        Создаёт предзаказ на основе товара по product_id для указанного магазина.
        Возвращает статусы: success | already_preordered | not_found | db_error
        """
        try:
            logger.info(f"🔍 [PREORDERS] Создаем предзаказ для товара: {product.get('product_id')}")
            
            # Валидация входных данных
            if not product or "product_id" not in product:
                return {"success": False, "status": "not_found", "product_id": None}

            product_id_raw = product["product_id"]

            # Приведение product_id к UUID
            try:
                product_id = uuid.UUID(str(product_id_raw))
            except (ValueError, TypeError):
                return {"success": False, "status": "not_found", "product_id": product_id_raw}

            # Проверяем существующий предзаказ
            check_query = """
                SELECT 1
                FROM preorders
                WHERE product_id = $1
                  AND store_id = $2
            """
            existing = await self.db_manager.execute_query(check_query, str(product_id), store_id)
            
            if existing:
                return {"success": False, "status": "already_preordered", "product_id": str(product_id)}

            # Получаем данные о товаре
            product_query = """
                SELECT id, kaspi_sku, name, category, price
                FROM products
                WHERE id = $1
            """
            prod_rows = await self.db_manager.execute_query(product_query, str(product_id))
            
            if not prod_rows:
                return {"success": False, "status": "not_found", "product_id": str(product_id)}
            
            prod = prod_rows[0]

            # Готовим данные предзаказа
            warehouses = product.get("warehouses", [])
            delivery_days = int(product.get("delivery_days", 30))
            created_at = datetime.now()

            # Вставляем предзаказ
            insert_query = """
                INSERT INTO preorders (product_id, store_id, article, name, brand, status,
                                       price, warehouses, delivery_days, created_at)
                VALUES ($1, $2, $3, $4, $5, 'processing', $6, $7, $8, $9)
                RETURNING id
            """
            
            result = await self.db_manager.execute_query(
                insert_query,
                str(product_id),
                store_id,
                prod["kaspi_sku"] or "",
                prod["name"] or "",
                prod["category"] or "",
                int(float(prod["price"] or 0)),
                json.dumps(warehouses),
                delivery_days,
                created_at.isoformat()
            )
            
            if result:
                logger.info(f"✅ [PREORDERS] Предзаказ создан для товара: {product_id}")
                return {"success": True, "status": "success", "product_id": str(product_id)}
            else:
                return {"success": False, "status": "db_error", "product_id": str(product_id)}

        except Exception as e:
            logger.error(f"❌ [PREORDERS] Ошибка создания предзаказа: {e}")
            return {"success": False, "status": "db_error", "product_id": str(product_id), "error": str(e)}
