#!/usr/bin/env python3
"""
Новая авторизация Kaspi на основе Playwright (как в kaspi-demper-main)
"""

import asyncio
import aiohttp
import logging
from playwright.async_api import async_playwright, Page
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class KaspiPlaywrightAuth:
    """Авторизация Kaspi через Playwright (как в kaspi-demper-main)"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Авторизация в Kaspi"""
        try:
            logger.info(f"🔐 [PLAYWRIGHT] Начинаем авторизацию для {email}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Выполняем авторизацию
                success, cookies = await self._login_to_kaspi(page, email, password)
                
                if not success:
                    raise Exception("Ошибка авторизации")
                
                # Преобразуем cookies
                cookies_dict = self._get_formatted_cookies(cookies)
                
                # Получаем информацию о магазине
                merchant_info = await self._get_merchant_info_via_api(cookies_dict)
                
                await browser.close()
                
                return {
                    "success": True,
                    "merchant_id": merchant_info["merchant_id"],
                    "store_name": merchant_info["store_name"],
                    "session_data": {
                        "cookies": cookies,
                        "merchant_id": merchant_info["merchant_id"],
                        "store_name": merchant_info["store_name"],
                        "login_time": asyncio.get_event_loop().time()
                    },
                    "auth_method": "playwright"
                }
                
        except Exception as e:
            logger.error(f"❌ [PLAYWRIGHT] Ошибка авторизации: {e}")
            return {
                "success": False,
                "error": str(e),
                "auth_method": "playwright"
            }
    
    async def _login_to_kaspi(self, page: Page, email: str, password: str) -> tuple[bool, List[Dict]]:
        """Вход в кабинет Kaspi (как в kaspi-demper-main)"""
        try:
            logger.info("🌐 [PLAYWRIGHT] Переход на страницу входа...")
            await page.goto("https://idmc.shop.kaspi.kz/login")
            await page.wait_for_load_state('domcontentloaded')
            
            # Шаг 1: Ввод email
            logger.info("📧 [PLAYWRIGHT] Шаг 1: Ввод email...")
            await page.wait_for_selector('#user_email_field', timeout=30000)
            await page.fill('#user_email_field', email)
            await page.click('.button.is-primary')
            
            # Шаг 2: Ждём появление полей email и пароль
            logger.info("⏳ [PLAYWRIGHT] Шаг 2: Ожидание полей...")
            await page.wait_for_selector('#user_email_field', timeout=30000)
            await page.wait_for_selector('#password_field', timeout=30000)
            
            # Шаг 3: Ввод email и пароля
            logger.info("🔑 [PLAYWRIGHT] Шаг 3: Ввод email и пароля...")
            await page.fill('#user_email_field', email)
            await page.fill('#password_field', password)
            await page.click('.button.is-primary')
            
            # Шаг 4: Ждём загрузки панели навигации
            logger.info("⏳ [PLAYWRIGHT] Шаг 4: Ожидание навигации...")
            await page.wait_for_selector('nav.navbar', timeout=30000)
            
            # Шаг 5: Проверка ошибок входа
            logger.info("🔍 [PLAYWRIGHT] Шаг 5: Проверка ошибок...")
            error_element = await page.query_selector('.notification.is-danger')
            if error_element:
                error_text = await error_element.text_content()
                logger.error(f"❌ [PLAYWRIGHT] Ошибка входа: {error_text}")
                return False, []
            
            # Получение cookies
            logger.info("🍪 [PLAYWRIGHT] Получение cookies...")
            cookies = await page.context.cookies()
            logger.info(f"✅ [PLAYWRIGHT] Получено {len(cookies)} cookies")
            
            return True, cookies
            
        except Exception as e:
            logger.error(f"❌ [PLAYWRIGHT] Ошибка входа: {e}")
            return False, []
    
    def _get_formatted_cookies(self, cookies: List[Dict]) -> Dict[str, str]:
        """Преобразует cookies в словарь"""
        formatted_cookies = {}
        for cookie in cookies:
            if isinstance(cookie, dict):
                formatted_cookies[cookie['name']] = cookie['value']
        return formatted_cookies
    
    async def _get_merchant_info_via_api(self, cookies_dict: Dict[str, str]) -> Dict[str, Any]:
        """Получение информации о магазине через API (как в kaspi-demper-main)"""
        try:
            logger.info("🌐 [PLAYWRIGHT] Получение информации о магазине через API...")
            
            headers = {
                "x-auth-version": "3",
                "Origin": "https://kaspi.kz",
                "Referer": "https://kaspi.kz/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
            
            async with aiohttp.ClientSession() as session:
                # Получаем список магазинов
                logger.info("📊 [PLAYWRIGHT] Запрос списка магазинов...")
                async with session.get("https://mc.shop.kaspi.kz/s/m", headers=headers, cookies=cookies_dict) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"📊 [PLAYWRIGHT] Ответ API: {response_data}")
                        
                        # Извлекаем merchant_uid
                        if isinstance(response_data.get('merchants'), list) and len(response_data['merchants']) > 0:
                            merchant_uid = response_data['merchants'][0]['uid']
                            logger.info(f"✅ [PLAYWRIGHT] Найден merchant_uid: {merchant_uid}")
                            
                            # Получаем название через GraphQL
                            store_name = await self._get_store_name_via_graphql(merchant_uid, headers, cookies_dict, session)
                            
                            return {
                                "merchant_id": merchant_uid,
                                "store_name": store_name
                            }
                        else:
                            logger.error("❌ [PLAYWRIGHT] Не удалось извлечь merchant_uid")
                            return {"merchant_id": "error", "store_name": "Ошибка"}
                    else:
                        logger.error(f"❌ [PLAYWRIGHT] API ошибка: {response.status}")
                        return {"merchant_id": "error", "store_name": "Ошибка API"}
                        
        except Exception as e:
            logger.error(f"❌ [PLAYWRIGHT] Ошибка API: {e}")
            return {"merchant_id": "error", "store_name": "Ошибка"}
    
    async def _get_store_name_via_graphql(self, merchant_uid: str, headers: Dict, cookies_dict: Dict, session: aiohttp.ClientSession) -> str:
        """Получение названия магазина через GraphQL"""
        try:
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
            
            url = "https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getMerchant"
            logger.info(f"🌐 [PLAYWRIGHT] GraphQL запрос: {url}")
            
            async with session.post(url, json=payload, headers=headers, cookies=cookies_dict) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"📊 [PLAYWRIGHT] GraphQL ответ: {data}")
                    
                    if 'data' in data and 'merchant' in data['data']:
                        store_name = data['data']['merchant']['name']
                        logger.info(f"✅ [PLAYWRIGHT] Название магазина: {store_name}")
                        return store_name
                
                logger.error(f"❌ [PLAYWRIGHT] GraphQL ошибка: {response.status}")
                return "Ошибка GraphQL"
                
        except Exception as e:
            logger.error(f"❌ [PLAYWRIGHT] Ошибка GraphQL: {e}")
            return "Ошибка"

async def test_playwright_auth():
    """Тест новой авторизации"""
    auth = KaspiPlaywrightAuth()
    
    email = "hvsv1@icloud.com"
    password = "CIoD29g8U1"
    
    result = await auth.login(email, password)
    logger.info(f"🎯 [TEST] Результат: {result}")

if __name__ == "__main__":
    asyncio.run(test_playwright_auth())
