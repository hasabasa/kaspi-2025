"""
Сервисы для работы с предзаказами
Адаптировано из unified-backend/api_parser.py
"""
import os
import json
import uuid
import logging
import requests
import pandas as pd
from typing import List, Dict
from django.utils import timezone
from api.models import Preorder
from kaspi_auth.session_manager import SessionManager

logger = logging.getLogger(__name__)

OUTPUT_DIR = 'preorder_exports'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_preorders(store_id: str, limit: int = None, offset: int = 0) -> List[Dict]:
    """Получает предзаказы по store_id"""
    queryset = Preorder.objects.filter(store_id=store_id).order_by('-created_at')
    
    if limit:
        queryset = queryset[offset:offset + limit]
    else:
        queryset = queryset[offset:]
    
    result = []
    for preorder in queryset:
        item = {
            'id': str(preorder.id),
            'product_id': str(preorder.product_id) if preorder.product else None,
            'store_id': str(preorder.store_id),
            'article': preorder.article,
            'name': preorder.name,
            'brand': preorder.brand,
            'price': preorder.price,
            'status': preorder.status,
            'warehouses': preorder.warehouses if isinstance(preorder.warehouses, dict) else {},
            'delivery_days': preorder.delivery_days,
            'created_at': preorder.created_at.isoformat() if preorder.created_at else None,
            'updated_at': preorder.updated_at.isoformat() if preorder.updated_at else None,
        }
        result.append(item)
    
    return result


def process_preorders_for_excel(rows: List[Dict]) -> List[Dict]:
    """Обрабатывает предзаказы для экспорта в Excel"""
    preorders_list = []
    for row in rows:
        wh_data = row.get('warehouses') or {}
        if isinstance(wh_data, str):
            try:
                wh_data = json.loads(wh_data)
            except json.JSONDecodeError:
                wh_data = {}
        
        counts = {f'pp{i}': 0 for i in range(1, 6)}
        total = 0
        
        if isinstance(wh_data, dict):
            for key, value in wh_data.items():
                if isinstance(value, dict):
                    wid = value.get('id', key)
                    qty = value.get('quantity', 0)
                    key_name = f'pp{wid}'
                    if key_name in counts:
                        counts[key_name] = qty
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


def generate_preorder_xlsx(preorders: List[Dict], store_id: str) -> str:
    """Генерирует .xlsx файл с предзаказами"""
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
    logger.info(f"✅ Excel сохранён: {filepath}")
    return filepath


def upload_preorder_to_kaspi(filepath: str, merchant_uid: str, cookies: dict):
    """Загружает файл предзаказов на Kaspi"""
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
    
    with open(filepath, 'rb') as f:
        files = {'file': (
            os.path.basename(filepath), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        resp = requests.post(url, headers=headers, cookies=cookies, files=files, timeout=60)
    
    resp.raise_for_status()
    logger.info(f"📤 Успешно загружено на Kaspi, статус {resp.status_code}")


def handle_upload_preorder(store_id: str):
    """Обрабатывает загрузку предзаказов на Kaspi"""
    try:
        rows = fetch_preorders(store_id)
        if not rows:
            logger.warning(f"Нет предзаказов для магазина {store_id}")
            return
        
        # Формируем список для Excel
        preorders_list = process_preorders_for_excel(rows)
        
        # Генерируем файл
        filepath = generate_preorder_xlsx(preorders_list, store_id)
        
        # Загружаем на Kaspi
        session_manager = SessionManager(shop_uid=store_id)
        if not session_manager.load():
            raise Exception("Сессия истекла, пожалуйста, войдите заново.")
        
        cookies = session_manager.get_cookies()
        merchant_id = session_manager.merchant_uid
        
        upload_preorder_to_kaspi(filepath, merchant_id, cookies)
        
        logger.info(f"✅ Предзаказы для магазина {store_id} успешно загружены")
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке предзаказов: {e}")
        raise

