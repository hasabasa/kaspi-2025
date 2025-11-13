#!/usr/bin/env python3
"""
Тест API Kaspi для получения реальных данных магазина
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def test_kaspi_api():
    """Тест API Kaspi"""
    
    # Загружаем cookies из файла accounts.json
    try:
        with open('/Users/hasen/demper-667-45/unified-backend/accounts.json', 'r') as f:
            accounts = json.load(f)
        
        email = 'hvsv1@icloud.com'
        if email in accounts:
            cookies_data = accounts[email].get('cookies', [])
            logger.info(f"🍪 [API-TEST] Найдено {len(cookies_data)} cookies для {email}")
            
            # Формируем cookies для запроса
            cookies_dict = {}
            for cookie in cookies_data:
                cookies_dict[cookie['name']] = cookie['value']
            
            logger.info(f"🍪 [API-TEST] Cookies: {list(cookies_dict.keys())}")
            
            # Заголовки для API
            headers = {
                "x-auth-version": "3",
                "Origin": "https://kaspi.kz",
                "Referer": "https://kaspi.kz/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
            
            # Тест 1: Получение списка магазинов
            logger.info(f"🌐 [API-TEST] Тест 1: Получение списка магазинов...")
            url1 = "https://mc.shop.kaspi.kz/s/m"
            
            try:
                response1 = requests.get(url1, headers=headers, cookies=cookies_dict, timeout=10)
                logger.info(f"📊 [API-TEST] Статус ответа: {response1.status_code}")
                
                if response1.status_code == 200:
                    data1 = response1.json()
                    logger.info(f"📊 [API-TEST] Ответ API: {data1}")
                    
                    # Извлекаем merchant_uid
                    if isinstance(data1.get('merchants'), list) and len(data1['merchants']) > 0:
                        merchant_uid = data1['merchants'][0]['uid']
                        logger.info(f"✅ [API-TEST] Найден merchant_uid: {merchant_uid}")
                        
                        # Тест 2: Получение названия через GraphQL
                        logger.info(f"🌐 [API-TEST] Тест 2: GraphQL запрос...")
                        
                        payload = {
                            "operationName": "getMerchant",
                            "variables": {"id": merchant_uid},
                            "query": """
                                query getMerchant($id: String!) {
                                  merchant(id: $id) {
                                    id
                                    name
                                    logo {
                                      url
                                    }
                                  }
                                }
                            """
                        }
                        
                        url2 = "https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getMerchant"
                        
                        try:
                            response2 = requests.post(url2, json=payload, headers=headers, cookies=cookies_dict, timeout=10)
                            logger.info(f"📊 [API-TEST] GraphQL статус: {response2.status_code}")
                            
                            if response2.status_code == 200:
                                data2 = response2.json()
                                logger.info(f"📊 [API-TEST] GraphQL ответ: {data2}")
                                
                                if 'data' in data2 and 'merchant' in data2['data']:
                                    store_name = data2['data']['merchant']['name']
                                    logger.info(f"✅ [API-TEST] Название магазина: {store_name}")
                                    
                                    logger.info(f"🎉 [API-TEST] УСПЕХ! Реальные данные:")
                                    logger.info(f"   🆔 Merchant ID: {merchant_uid}")
                                    logger.info(f"   🏪 Store Name: {store_name}")
                                else:
                                    logger.error(f"❌ [API-TEST] Неверная структура GraphQL ответа")
                            else:
                                logger.error(f"❌ [API-TEST] GraphQL ошибка: {response2.status_code}")
                                logger.error(f"❌ [API-TEST] Ответ: {response2.text[:200]}")
                                
                        except Exception as e:
                            logger.error(f"❌ [API-TEST] GraphQL исключение: {e}")
                    else:
                        logger.error(f"❌ [API-TEST] Неверная структура ответа API")
                else:
                    logger.error(f"❌ [API-TEST] API ошибка: {response1.status_code}")
                    logger.error(f"❌ [API-TEST] Ответ: {response1.text[:200]}")
                    
            except Exception as e:
                logger.error(f"❌ [API-TEST] API исключение: {e}")
        else:
            logger.error(f"❌ [API-TEST] Аккаунт {email} не найден в accounts.json")
            
    except Exception as e:
        logger.error(f"❌ [API-TEST] Исключение: {e}")

if __name__ == "__main__":
    test_kaspi_api()
