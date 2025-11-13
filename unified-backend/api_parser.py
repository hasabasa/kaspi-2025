# api_parser.py method to parse and extract data from Kaspi API
import json
import os
import random
import re
import uuid
from decimal import Decimal
from collections import defaultdict
from datetime import datetime
from typing import Literal, Any, Optional

import aiohttp
import asyncpg
import pandas as pd
import requests
from aiohttp import ClientSession
from fastapi import HTTPException, status
from httpx import HTTPError
from playwright.async_api import async_playwright, Page, Cookie

from db import create_pool
from error_handlers import ErrorHandler, logger
from proxy_balancer import proxy_balancer
from proxy_config import get_proxy_config
from utils import LoginError, get_product_count


def _proxy_url(proxy_dict: Optional[dict] = None) -> Optional[str]:
    cfg = get_proxy_config(proxy_dict)
    return cfg.get('http') if cfg else None


OUTPUT_DIR = 'preorder_exports'
os.makedirs(OUTPUT_DIR, exist_ok=True)


class SessionManager:
    """Менеджер сессий для работы с cookies и авторизацией"""

    def __init__(self, user_id: str = None, merchant_uid: str = None, shop_uid: str = None):
        self.user_id = user_id
        self.merchant_uid = merchant_uid
        self.session_data = None
        self.last_login = None
        self.shop_uid = shop_uid
        self.pool = None

    async def load(self):
        """Загружает данные сессии из базы данных и проверяет её актуальность"""
        if not self.pool:
            self.pool = await create_pool()  # Создаем пул соединений, если он еще не создан

        if self.shop_uid:
            query = """
                    SELECT guid, merchant_id, last_login
                    FROM kaspi_stores
                    WHERE id = $1 \
                    """
            response = await self.pool.fetch(query, self.shop_uid)
        else:
            query = """
                    SELECT guid, merchant_id, last_login
                    FROM kaspi_stores
                    WHERE user_id = $1
                      AND merchant_id = $2 \
                    """
            response = await self.pool.fetch(query, self.user_id, self.merchant_uid)

        if not response:
            raise Exception("Магазин не найден")

        guid_data = response[0]["guid"]
        self.merchant_uid = response[0].get("merchant_id")

        # Проверяем, что guid является списком cookies или строкой
        if isinstance(guid_data, list):  # Если это список cookies
            self.session_data = guid_data
        elif isinstance(guid_data, str) and guid_data.startswith('{') and guid_data.endswith('}'):
            # Если это строка JSON, распарсим её
            try:
                self.session_data = json.loads(guid_data)
            except json.JSONDecodeError:
                self.session_data = guid_data
        else:
            self.session_data = guid_data

        # Проверяем, актуальна ли сессия
        if not self.is_session_valid():
            # Если сессия невалидна, выполняем повторный логин
            email, password = self.get_email_password()
            if email and password:
                return await self.reauthorize()
            # нет учётки -> пусть верхний уровень решает (демпер пропустит)
            return False
        return True

    def get_cookies(self):
        """Возвращает cookies из сохраненной сессии"""
        if self.session_data:
            return get_formatted_cookies(self.session_data.get("cookies", []))
        return None

    def get_email_password(self):
        """Возвращает email и пароль из сохраненной сессии"""
        if self.session_data:
            if not self.session_data.get("email") or not self.session_data.get("password"):
                return None, None
            return self.session_data.get("email"), self.session_data.get("password")
        return None, None

    async def save(self, cookies, email, password):
        """Сохраняет cookies, email и пароль в сессии и обновляет данные в базе"""
        self.session_data = {
            "cookies": cookies,
            "email": email,
            "password": password
        }
        # Добавляем метку времени последнего входа
        self.last_login = datetime.now()

        if not self.pool:
            self.pool = await create_pool()  # Создаем пул соединений, если он ещё не создан

        # Асинхронно обновляем сессию в базе данных
        async with self.pool.acquire() as connection:
            query = """
                    UPDATE kaspi_stores
                    SET guid       = $1,
                        last_login = $2
                    WHERE merchant_id = $3 \
                    """
            await connection.execute(query, json.dumps(self.session_data), self.last_login, self.merchant_uid)

        return {
            "cookies": cookies,
            "email": email,
            "password": password
        }

    def is_session_expired(self, session_timeout: int = 3600) -> bool:
        """Проверяет, истекла ли сессия"""
        if not self.last_login:
            return True

        last_login_time = datetime.fromisoformat(self.last_login)
        return (datetime.now() - last_login_time).seconds > session_timeout

    def is_session_valid(self) -> bool:
        """Проверяет, действительна ли текущая сессия"""
        cookies = self.get_cookies()

        if not cookies:
            return False

        # Пример запроса для проверки сессии
        try:
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

            response = requests.get("https://mc.shop.kaspi.kz/s/m", headers=headers, cookies=cookies)
            if response.status_code != 200:
                # print(response.status_code)
                # print(response.text)
                return False  # Если 401 Unauthorized, сессия невалидна
            return True  # Если запрос успешен, сессия действительна
        except requests.RequestException as e:
            print(f"Ошибка при проверке сессии: {e}")
            # traceback.print_exc()
            return False  # Если запрос не удался, сессия считается невалидной

    async def reauthorize(self):
        """Повторная авторизация, если сессия невалидна"""
        # Получаем email и пароль из сохраненной сессии
        email, password = self.get_email_password()
        if not email or not password:
            print("Не удалось получить email и пароль из сохраненной сессии")
            return False

        # Выполняем повторный логин
        print("Сессия невалидна, требуется повторный логин")

        # Пример выполнения повторного логина (вам нужно будет передать email и пароль)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Выполняем логин с новыми данными
            success, cookies = await login_to_kaspi(page, email, password)
            await self.save(cookies, email, password)
            await browser.close()
        return True


async def login_to_kaspi(page: Page, email: str, password: str) -> tuple[Literal[True], list[Cookie]]:
    """Вход в кабинет Kaspi и сохранение cookies"""
    error_handler = ErrorHandler(page)

    try:
        logger.info("Переход на страницу входа...")
        await page.goto("https://idmc.shop.kaspi.kz/login")
        await page.wait_for_load_state('domcontentloaded')

        # Шаг 1: Ввод email
        await page.wait_for_selector('#user_email_field', timeout=30000)
        await page.fill('#user_email_field', email)
        await page.click('.button.is-primary')

        # Шаг 2: Ждём появление полей email и пароль
        await page.wait_for_selector('#user_email_field', timeout=30000)
        await page.wait_for_selector('#password_field', timeout=30000)

        # Шаг 3: Ввод email и пароля
        await page.fill('#user_email_field', email)
        await page.fill('#password_field', password)
        await page.click('.button.is-primary')

        # Шаг 4: Ждём загрузки панели навигации
        await page.wait_for_selector('nav.navbar', timeout=30000)

        # Шаг 5: Проверка ошибок входа
        error_element = await page.query_selector('.notification.is-danger')
        if error_element:
            error_text = await error_element.text_content()
            await error_handler.handle_login_error()
            raise LoginError(f"Ошибка при входе: {error_text}")

        # Получение cookies
        cookies = await page.context.cookies()

        return True, cookies

    except Exception as e:
        await error_handler.handle_all_errors(e)
        logger.error(f"❌ Ошибка при входе: {str(e)}")
        raise LoginError(str(e))


def get_formatted_cookies(cookies: list[any]) -> dict[str, str]:
    """Преобразует cookies из списка в словарь для использования в запросах"""
    formatted_cookies = {}

    for cookie in cookies:
        if isinstance(cookie, dict):  # Убедимся, что cookie является словарем
            formatted_cookies[cookie['name']] = cookie['value']
        else:
            logger.warning(f"Невалидный cookie: {cookie}, пропускаем.")

    return formatted_cookies


async def login_and_get_merchant_info(email: str, password: str, user_id: str) -> \
        tuple[list[Cookie], Any, Any, dict[str, Any]]:
    session_manager = SessionManager(user_id)

    try:
        # Выполняем логин и получаем cookies
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            success, cookies = await login_to_kaspi(page, email, password)

            # Преобразуем cookies в словарь для использования в aiohttp
            cookies_dict = get_formatted_cookies(cookies)

            # Сохраняем сессию
            guid = await session_manager.save(cookies, email, password)

            # Извлекаем информацию о магазине (merchant_id и shop_name)
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

            # Получаем список магазинов
            async with aiohttp.ClientSession() as session:
                async with session.get("https://mc.shop.kaspi.kz/s/m", headers=headers,
                                       cookies=cookies_dict) as response:
                    response_merchants = await response.json()

                # Проверьте, что это список, и извлекайте merchant_uid
                if isinstance(response_merchants.get('merchants'), list) and len(response_merchants['merchants']) > 0:
                    merchant_uid = response_merchants['merchants'][0]['uid']
                else:
                    raise LoginError("Не удалось извлечь merchant_uid из ответа Kaspi")

                # Получаем информацию о магазине по merchant_uid
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

                url_shop_info = "https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getMerchant"
                async with session.post(url_shop_info, json=payload, headers=headers,
                                        cookies=cookies_dict) as response_shop_info:
                    shop_info = await response_shop_info.json()
                    shop_name = shop_info['data']['merchant']['name']

            await browser.close()

        return cookies, merchant_uid, shop_name, guid

    except Exception as e:
        raise LoginError(f"Ошибка при авторизации: {str(e)}")


async def sync_store_api(store_id: str):
    """Синхронизация товаров для указанного магазина"""

    # Загружаем сессию магазина по store_id
    session_manager = SessionManager(shop_uid=store_id)
    if not await session_manager.load():
        raise HTTPException(status_code=401,
                            detail="Сессия истекла или отсутствуют учётные данные. Нужен повторный логин.")

    # Извлекаем cookies и merchant_id
    cookies = session_manager.get_cookies()
    if not cookies:
        raise HTTPException(status_code=400, detail="Cookies для сессии не найдены")

    # Получение товаров для магазина
    merchant_id = session_manager.merchant_uid
    products = await get_products(cookies, merchant_id)
    
    current_count = len(products)
    
    pool = await create_pool()
    async with pool.acquire() as conn:
        user_id_result = await conn.fetchrow(
            """
            SELECT user_id
            FROM kaspi_stores
            WHERE id = $1
            """,
            store_id
        )
    
    if not user_id_result:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    user_id = user_id_result["user_id"]
    current_product_count = await get_product_count(store_id)
    
    # Убираем ограничения по подписке - разрешаем неограниченное количество товаров
    max_products = 1000

    current_count = len(products)

    # Получаем пул соединений
    pool = await create_pool()

    # Вставка товаров, если они не существуют в базе данных
    for product in products:
        await insert_product_if_not_exists(product, store_id, pool)

    # Обновление количества товаров и метки времени синхронизации
    update_data = {
        "products_count": current_count + current_product_count,
        "last_sync": datetime.now(),
    }

    try:
        async with pool.acquire() as connection:
            # Обновление данных в таблице kaspi_stores
            await connection.execute(
                """
                UPDATE kaspi_stores
                SET products_count = $1,
                    last_sync      = $2
                WHERE id = $3
                """,
                update_data["products_count"], update_data["last_sync"], store_id
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления данных: {str(e)}")

    return {
        "success": True,
        "products_count": update_data["products_count"],
        "message": "Товары успешно синхронизированы"
    }


async def insert_product_if_not_exists(product: dict, store_id: str, pool=None):
    product["store_id"] = store_id

    # Преобразуем UUID в строку, если они есть в product
    for key, value in product.items():
        if isinstance(value, uuid.UUID):
            product[key] = str(value)

    # Если pool не передан, используем синглтон для получения пула соединений
    if not pool:
        pool = await create_pool()

    try:
        # Проверяем, существует ли продукт с таким kaspi_sku и store_id
        async with pool.acquire() as connection:
            existing = await connection.fetch(
                """
                SELECT id, price, external_kaspi_id, category, image_url
                FROM products
                WHERE kaspi_sku = $1
                  AND store_id = $2
                LIMIT 1
                """,
                product["kaspi_sku"], product["store_id"]
            )

            if existing:
                existing_price = existing[0].get("price")

                if existing_price != product["price"] or product['category'] != existing[0].get('category') or product[
                    'image_url'] != existing[0].get('image_url'):
                    await connection.execute(
                        """
                        UPDATE products
                        SET price     = $1,
                            category  = $2,
                            image_url = $3
                        WHERE id = $4
                        """,
                        product["price"], product['category'], product['image_url'], existing[0]["id"]
                    )
                    print(f"🔄 Цена обновлена для товара: {product['name']} (с {existing_price} на {product['price']})")

                return False

            # Если продукта нет, вставляем новый товар
            await connection.execute(
                """
                INSERT INTO products (kaspi_product_id, kaspi_sku, store_id, price, name, external_kaspi_id, category,
                                      image_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                product["kaspi_product_id"], product["kaspi_sku"], product["store_id"], product["price"],
                product["name"], product.get("external_kaspi_id"), product.get('category'), product.get('image_url')
            )
            print(f"✅ Добавлен товар: {product['name']}")
            return True

    except asyncpg.exceptions.PostgresError as e:
        # Специфическая обработка ошибок базы данных
        print(f"❌ Ошибка вставки товара в базу данных: {e}")
        return False
    except Exception as e:
        # Общая обработка ошибок
        print(f"❌ Ошибка при вставке товара: {e}")
        return False


async def get_products(cookie_jar: dict, merchant_uid: str, page_size: int = 100) -> list[dict]:
    """
    Получает все товары продавца по пагинации асинхронно, с прокси и авторизацией.

    :param cookie_jar: словарь с куки для аутентификации
    :param merchant_uid: уникальный идентификатор продавца
    :param page_size: количество товаров на страницу (максимум 100)
    :return: список всех предложений
    """
    logger.info(f"🔍 [PRODUCTS] Начинаем получение товаров для merchant_uid: {merchant_uid}")
    logger.info(f"📦 [PRODUCTS] Размер страницы: {page_size}")
    
    headers = {
        "x-auth-version": "3",
        "Origin": "https://kaspi.kz",
        "Referer": "https://kaspi.kz/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    logger.info(f"📋 [PRODUCTS] Заголовки запроса: {headers}")

    # Получаем прокси через балансировщик
    proxy_dict = proxy_balancer.get_balanced_proxy(f"merchant_{merchant_uid}")
    proxy_url = _proxy_url(proxy_dict)
    logger.info(f"🔄 [PRODUCTS] Используем прокси: {proxy_url}")

    all_offers = []
    page = 0

    async with ClientSession() as session:
        while True:
            url = (
                f"https://mc.shop.kaspi.kz/bff/offer-view/list"
                f"?m={merchant_uid}&p={page}&l={page_size}&a=true"
            )
            logger.info(f"🌐 [PRODUCTS] Запрос страницы {page}: {url}")

            try:
                # Асинхронный запрос с использованием aiohttp, прокси и авторизации
                async with session.get(url, headers=headers, cookies=cookie_jar, proxy=proxy_url) as response:
                    logger.info(f"📊 [PRODUCTS] Ответ страницы {page}: статус {response.status}")
                    
                    if response.status == 401:
                        logger.error(f"❌ [PRODUCTS] Ошибка авторизации: 401 Unauthorized")
                        raise HTTPError("Ошибка аутентификации: 401 Unauthorized")
                    
                    if response.status == 429:
                        logger.error(f"❌ [PRODUCTS] Превышен лимит запросов: 429 Too Many Requests")
                        rate_limit_error = Exception("Too Many Requests from Kaspi API")
                        rate_limit_error.status_code = 429
                        raise rate_limit_error

                    response.raise_for_status()

                    data = await response.json()
                    offers = data.get('data', [])
                    logger.info(f"📦 [PRODUCTS] Получено сырых офферов на странице {page}: {len(offers)}")

                    # Если на странице нет офферов — выходим из цикла
                    if not offers:
                        logger.info(f"🏁 [PRODUCTS] Страница {page} пустая, завершаем пагинацию")
                        break

                    # Добавляем офферы в общий список
                    processed_count = 0
                    for o in offers:
                        mapped_offer = map_offer(o)
                        all_offers.append(mapped_offer)
                        processed_count += 1
                        logger.info(f"✅ [PRODUCTS] Обработан оффер {processed_count}: SKU={mapped_offer.get('kaspi_sku')}, название={mapped_offer.get('name', 'N/A')[:50]}...")

                    logger.info(f"📊 [PRODUCTS] Получено {len(offers)} офферов на странице {page}")
                    logger.info(f"📈 [PRODUCTS] Всего накоплено офферов: {len(all_offers)}")

                    page += 1

            except HTTPError as http_err:
                logger.error(f"❌ [PRODUCTS] Ошибка авторизации при получении офферов: {http_err}")
                raise
            except aiohttp.ClientError as err:
                logger.error(f"❌ [PRODUCTS] Ошибка при запросе офферов: {err}")
                raise

    logger.info(f"🎉 [PRODUCTS] Всего получено офферов: {len(all_offers)}")
    return all_offers


def map_offer(raw_offer: dict) -> dict:
    # Извлекаем ID товара из URL, используя регулярное выражение
    product_url = raw_offer.get("shopLink", "")
    match = re.search(r'\/p\/.*-(\d+)\/', product_url)

    # Если ID найден, используем его как external_kaspi_id
    external_kaspi_id = match.group(1) if match else None

    return {
        "kaspi_product_id": raw_offer.get("offerId"),  # Оставляем offerId как kaspi_product_id
        "kaspi_sku": raw_offer.get("sku"),  # SKU товара
        "name": raw_offer.get("masterTitle"),
        "category": raw_offer.get("masterCategory"),
        "price": raw_offer.get("minPrice", {}),
        "image_url": f"https://resources.cdn-kaspi.kz/img/m/p/{raw_offer.get('images', [])[0]}",
        "external_kaspi_id": external_kaspi_id,  # Спарсенный ID из URL
        "updated_at": raw_offer.get("updatedAt")
    }


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    # ...добавь ещё пару вариантов
]

ACCEPT_ENCODINGS = [
    "gzip, deflate, br",
    "gzip, deflate, br, zstd",
    "gzip, deflate"
]

ACCEPT_LANGUAGE = [
    "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "ru-RU,ru;q=0.8,en-US;q=0.7,en;q=0.6",
    "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7"
]

X_KS_CITY = [
    "750000000",  # Алматы
    "770000000",  # Астана
    "730000000",  # Шымкент
    # …другие коды, если нужно
]


def get_random_headers(sku: str = None) -> dict:
    return {
        "accept": random.choice([
            "application/json, text/*",
            "application/json, text/html, */*",
        ]),
        "accept-encoding": random.choice(ACCEPT_ENCODINGS),
        "accept-language": random.choice(ACCEPT_LANGUAGE),
        "cache-control": random.choice(["no-cache", "max-age=0"]),
        "connection": random.choice(["keep-alive", "close"]),
        "content-type": "application/json; charset=UTF-8",
        "host": "kaspi.kz",
        "origin": "https://kaspi.kz",
        "pragma": random.choice(["no-cache", ""]),
        "referer": f"https://kaspi.kz/shop/p/{sku}" if sku else "https://kaspi.kz/",
        "user-agent": random.choice(USER_AGENTS),
        "x-ks-city": X_KS_CITY[0],
    }


async def parse_product_by_sku(sku: str) -> list:
    """Парсит данные о товаре по SKU через API Kaspi асинхронно"""
    logger.info(f"🔍 [PARSER] Начинаем парсинг товара SKU: {sku}")
    
    # URL API Kaspi для запроса
    url = f"https://kaspi.kz/yml/offer-view/offers/{sku}"
    logger.info(f"🌐 [PARSER] URL запроса: {url}")

    # Заголовки для запроса
    headers = get_random_headers(sku)
    logger.info(f"📋 [PARSER] Заголовки запроса: {headers}")

    # Тело запроса
    body = {
        "cityId": "750000000",  # Убедитесь, что cityId корректный
        "id": sku,
        "merchantUID": [],
        "limit": 5,
        "page": 0,
        "sortOption": "PRICE",
        "highRating": None,
        "searchText": None,
        "zoneId": ["Magnum_ZONE1"],
        "installationId": "-1"
    }
    logger.info(f"📦 [PARSER] Тело запроса: {body}")

    try:
        # Получаем прокси через балансировщик
        proxy_dict = proxy_balancer.get_balanced_proxy(f"sku_{sku}")
        proxy_url = _proxy_url(proxy_dict)
        logger.info(f"🔄 [PARSER] Используем прокси: {proxy_url}")

        # Создаем сессию для отправки запроса
        async with aiohttp.ClientSession() as session:
            logger.info(f"🚀 [PARSER] Отправляем POST запрос к Kaspi API...")
            
            # Отправляем POST запрос с аутентификацией прокси
            async with session.post(url, json=body, headers=headers, proxy=proxy_url) as response:
                logger.info(f"📊 [PARSER] Получен ответ: статус {response.status}")
                
                # Проверяем, что запрос прошел успешно
                response.raise_for_status()  # В случае ошибки выбросит HTTPError

                # Получаем данные из ответа
                product_data = await response.json()
                logger.info(f"📄 [PARSER] Получены данные товара: {len(str(product_data))} символов")
                
                # Парсим данные о ценах
                parsed_offers = parse_merchant_price_from_offers(product_data)
                logger.info(f"💰 [PARSER] Найдено предложений: {len(parsed_offers)}")
                
                if parsed_offers:
                    prices = [offer.get('price', 0) for offer in parsed_offers]
                    logger.info(f"💵 [PARSER] Цены конкурентов: {prices}")
                    min_price = min(prices) if prices else 0
                    logger.info(f"🏆 [PARSER] Минимальная цена: {min_price}")
                
                return parsed_offers

    except aiohttp.ClientError as e:
        logger.error(f"❌ [PARSER] Ошибка HTTP запроса для SKU {sku}: {e}")
        return []
    except ValueError as ve:
        logger.error(f"❌ [PARSER] Ошибка обработки данных для SKU {sku}: {ve}")
        return []


def parse_merchant_price_from_offers(response_data: dict) -> list:
    """Парсит данные о продавцах и их ценах из ответа API Kaspi"""
    logger.info(f"🔍 [PARSER] Начинаем парсинг предложений из ответа API")
    logger.info(f"📊 [PARSER] Структура ответа: {list(response_data.keys())}")

    # Проверка, есть ли в ответе данные о предложениях
    if 'offers' not in response_data:
        logger.warning(f"⚠️ [PARSER] Ответ не содержит данных о предложениях")
        logger.info(f"📄 [PARSER] Доступные ключи: {list(response_data.keys())}")
        raise ValueError("Ответ не содержит данных о предложениях")

    offers = response_data['offers']
    logger.info(f"📦 [PARSER] Найдено предложений в ответе: {len(offers)}")

    merchant_data = []

    # Извлекаем данные для каждого предложения
    for i, offer in enumerate(offers):
        logger.info(f"🔍 [PARSER] Обрабатываем предложение {i+1}/{len(offers)}")
        
        merchant_id = offer.get('merchantId')
        price = offer.get('price')
        
        logger.info(f"🏪 [PARSER] Merchant ID: {merchant_id}, Цена: {price}")

        # Добавляем данные в список, если они есть
        if merchant_id and price:
            merchant_data.append({
                'merchant_id': merchant_id,
                'price': price
            })
            logger.info(f"✅ [PARSER] Добавлено предложение: merchant_id={merchant_id}, price={price}")
        else:
            logger.warning(f"⚠️ [PARSER] Пропущено предложение: merchant_id={merchant_id}, price={price}")

    logger.info(f"💰 [PARSER] Итого обработано предложений: {len(merchant_data)}")
    return merchant_data


# Метод для отправки запроса с обновлением информации о товаре
async def send_price_update_request(product_data: dict, cookies: dict):
    """Отправляет запрос на обновление цены и наличия товара по SKU асинхронно"""

    # URL API Kaspi для обновления информации о товаре
    url = "https://mc.shop.kaspi.kz/pricefeed/upload/merchant/process"

    # Заголовки для запроса
    headers = {
        "accept": "application/json, text/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "content-type": "application/json; charset=UTF-8",
        "host": "mc.shop.kaspi.kz",
        "origin": "https://kaspi.kz",
        "pragma": "no-cache",
        "referer": "https://kaspi.kz/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
        "x-ks-city": "750000000",  # Убедитесь, что город правильно передан
    }

    # Тело запроса (формируем на основе данных из базы)
    merchant_id = product_data["merchant_id"]
    body = {
        "merchantUid": merchant_id,
        "availabilities": [{"available": "yes", "storeId": f"{merchant_id}_PP1", "stockEnabled": False}],
        "sku": product_data["kaspi_sku"],
        "price": product_data["price"]
    }
    print("body", body)

    try:
        # Получаем прокси через балансировщик
        proxy_dict = proxy_balancer.get_balanced_proxy(f"merchant_{merchant_id}")
        proxy_url = _proxy_url(proxy_dict)

        # Создаем сессию для асинхронного запроса
        async with aiohttp.ClientSession() as session:
            # Отправляем POST запрос с cookies и прокси
            async with session.post(url, json=body, headers=headers, cookies=cookies, proxy=proxy_url) as response:
                # Проверяем, что запрос прошел успешно
                response.raise_for_status()  # В случае ошибки выбросит HTTPError

                # Получаем данные из ответа
                response_data = await response.json()

                # Логируем или обрабатываем ответ
                if 'status' in response_data and response_data['status'] == 'success':
                    print(f"Цена и наличие для товара {product_data['sku']} обновлены успешно.")
                else:
                    print(
                        f"Не удалось обновить цену и наличие для товара {product_data['sku']}. Ответ: {response_data}")

    except aiohttp.ClientError as e:
        print(f"Ошибка при запросе: {e}")
        return {}


# Метод для извлечения данных товара из базы данных (через asyncpg)
async def get_product_data_from_db(product_id):
    pool = await create_pool()

    # ✅ корректно приводим к UUID
    if isinstance(product_id, uuid.UUID):
        pid = product_id
    elif isinstance(product_id, str):
        try:
            pid = uuid.UUID(product_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="product_id должен быть UUID")
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип product_id")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, kaspi_product_id, price, store_id, kaspi_sku
            FROM products
            WHERE id = $1
            """,
            pid  # ← передаём настоящий uuid.UUID
        )

    if not row:
        raise HTTPException(status_code=404, detail="Товар не найден")

    store_id = row["store_id"]
    if not store_id:
        raise HTTPException(status_code=400, detail="Не указан store_id для товара")

    # Подтянем cookies/merchant через SessionManager по store_id
    session_manager = SessionManager(shop_uid=str(store_id))
    if not await session_manager.load():
        # сессия протухла/не найдена
        return None, None

    cookies = session_manager.get_cookies()

    # Сформируем структуру для обновления цены
    product_data = {
        "sku": row["kaspi_product_id"],  # SKU для каспи API (тот, что в pricefeed)
        "kaspi_sku": row["kaspi_sku"],  # наш SKU/артикул
        "price": float(row["price"]),  # текущая цена из БД
        "merchant_id": session_manager.merchant_uid,
        "store_id": str(store_id),
    }

    return product_data, cookies


# Основной метод синхронизации товара по product_id
async def sync_product(product_id: str, price: Decimal):
    """Синхронизация товара для указанного product_id"""

    # Получаем данные товара из базы данных и cookies
    product_data, cookies = await get_product_data_from_db(product_id)

    if not cookies:
        raise HTTPException(status_code=400, detail="Cookies для сессии не найдены")
    product_data['price'] = float(price)
    # Отправляем запрос для обновления товара
    await send_price_update_request(product_data, cookies)

    return {
        "success": True,
        "message": f"Товар {product_id} успешно синхронизирован"
    }


def fetch_orders(url: str, headers: dict, cookies: dict):
    response = requests.get(url, headers=headers, cookies=cookies)
    response.raise_for_status()
    return response.json()


def map_order_data(json_data):
    daily_summary = defaultdict(lambda: {'count': 0, 'amount': 0})

    for tab in json_data:
        for order in tab.get('orders', []):
            date = datetime.fromtimestamp(order['createDate'] / 1000).strftime('%Y-%m-%d')
            daily_summary[date]['count'] += 1
            daily_summary[date]['amount'] += order['totalPrice']

    return [{'date': date, 'count': data['count'], 'amount': data['amount']}
            for date, data in sorted(daily_summary.items())]


def map_top_products(json_data, sort_by="quantity"):
    product_summary = defaultdict(lambda: {'quantity': 0, 'totalAmount': 0, 'name': ""})

    for tab in json_data:
        for order in tab.get('orders', []):
            for entry in order.get('entries', []):
                product_id = int(entry['masterProductCode'])
                product_summary[product_id]['name'] = entry['name']
                product_summary[product_id]['quantity'] += entry['quantity']
                product_summary[product_id]['totalAmount'] += entry['totalPrice']

    top_products = []
    for pid, data in product_summary.items():
        average_price = data['totalAmount'] / data['quantity']
        top_products.append({
            'id': pid,
            'name': data['name'],
            'quantity': data['quantity'],
            'totalAmount': data['totalAmount'],
            'averagePrice': average_price
        })

    if sort_by == "amount":
        top_products.sort(key=lambda x: x['totalAmount'], reverse=True)
    else:
        top_products.sort(key=lambda x: x['quantity'], reverse=True)

    return top_products


def calculate_metrics(json_data):
    total_sales = 0
    total_orders = 0

    for tab in json_data:
        orders = tab.get('orders', [])
        total_orders += len(orders)
        for order in orders:
            total_sales += order['totalPrice']

    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    return {
        'totalSales': total_sales,
        'totalOrders': total_orders,
        'avgOrderValue': avg_order_value
    }


def get_sells_delivery_request(merchant_id: str, cookies: dict):
    headers = {
        "accept": "application/json, text/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "content-type": "application/json; charset=UTF-8",
        "host": "mc.shop.kaspi.kz",
        "origin": "https://kaspi.kz",
        "pragma": "no-cache",
        "referer": "https://kaspi.kz/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
        "x-ks-city": "750000000",
    }

    urls = [
        f"https://mc.shop.kaspi.kz/mc/api/orderTabs/active?count=100&selectedTabs=DELIVERY&startIndex=0&loadPoints=false&_m={merchant_id}",
        f"https://mc.shop.kaspi.kz/mc/api/orderTabs/active?count=100&selectedTabs=PICKUP&startIndex=0&loadPoints=false&_m={merchant_id}"
    ]

    combined_json_data = []

    for url in urls:
        response_data = fetch_orders(url, headers, cookies)
        print(response_data)
        combined_json_data.extend(response_data)

    orders = map_order_data(combined_json_data)
    products = map_top_products(combined_json_data)
    metrics = calculate_metrics(combined_json_data)
    return {
        "orders": orders,
        "top_products": products,
        "metrics": metrics
    }


async def get_sells(shop_id):
    session_manager = SessionManager(shop_uid=shop_id)
    if not await session_manager.load():
        return False, 'Cессия истекла, пожалуйста, войдите заново.'
    cookies = session_manager.get_cookies()
    return True, get_sells_delivery_request(session_manager.merchant_uid, cookies)


# Хранение активных SMS-сессий: session_id → { browser, context, page, user_id }
sms_sessions: dict[str, dict] = {}


async def sms_login_start(user_id: str, phone: str) -> str:
    """
    Открываем Playwright, вводим phone → click send.
    Возвращаем session_id и держим page открытой.
    """
    session_id = str(uuid.uuid4())
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)  # Запускаем браузер в режиме видимости для тестов
    context = await browser.new_context()
    page: Page = await context.new_page()

    logger.info("Переход на страницу входа sms...")
    await page.goto("https://idmc.shop.kaspi.kz/login")  # или реальный URL
    await page.wait_for_load_state('domcontentloaded')
    await page.wait_for_selector('#phone_tab', timeout=30000)
    await page.click("#phone_tab")

    # Шаг 1: Ввод телефона
    await page.wait_for_selector('#user_phone_field', timeout=30000)
    await page.fill("#user_phone_field", phone)

    await page.click('.button.is-primary')

    sms_sessions[session_id] = {
        "playwright": p,
        "browser": browser,
        "context": context,
        "page": page,
        "user_id": user_id
    }
    return session_id


from playwright.async_api import TimeoutError as PlaywrightTimeoutError


async def sms_login_verify(session_id: str, user_id: str, code: str):
    """
    Берём сохранённую сессию, вводим код, ждём входа, парсим merchant info.
    """
    sess = sms_sessions.get(session_id)
    if not sess:
        raise HTTPException(404, "session_id не найден")

    page = sess["page"]
    context = sess["context"]
    p = sess["playwright"]
    error_handler = ErrorHandler(page)
    # Ввод кода и ожидание
    await page.wait_for_selector('input[name="security-code"]', timeout=30000)
    await page.fill('input[name="security-code"]', code)

    await page.click('.button.is-primary')
    error_element = None
    try:
        # ждём потенциального сообщения об ошибке, но не дольше 3с
        error_element = await page.wait_for_selector('.help.is-danger', timeout=3_000)
    except PlaywrightTimeoutError as e:
        # ошибки нет — нормально залогинились
        pass
    if error_element:
        # Получаем текст, обрезаем лишние пробелы
        error_text = (await error_element.text_content() or "").strip()
        logger.warning(f"Kaspi SMS-login error: {error_text}")
        # Можно вызвать свой обработчик ошибок, если он делает какую-то логику логирования или скриншотов
        raise HTTPException(status_code=401, detail=error_text)
    # Шаг 4: Ждём загрузки панели навигации
    await page.wait_for_selector('nav.navbar', timeout=30000)
    session_manager = SessionManager(user_id)
    # Забираем куки
    cookies = await page.context.cookies()
    # cookies: list[Cookie] = await context.cookies()
    cookies_dict = get_formatted_cookies(cookies)
    guid = await session_manager.save(cookies, None, None)
    # --- ТУТ ДЕЛАЕМ запросы к Kaspi, как в login_and_get_merchant_info ---
    headers = {
        "x-auth-version": "3",
        "Origin": "https://kaspi.kz",
        "Referer": "https://kaspi.kz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    resp = requests.get(
        "https://mc.shop.kaspi.kz/s/m",
        headers=headers,
        cookies=cookies_dict,
        timeout=10
    )
    resp.raise_for_status()
    merchants = resp.json().get("merchants", [])
    if not merchants:
        raise HTTPException(400, "Не удалось получить merchant_uid")
    merchant_uid = merchants[0]["uid"]

    # GraphQL-запрос за именем магазина
    payload = {
        "operationName": "getMerchant",
        "variables": {"id": merchant_uid},
        "query": """
          query getMerchant($id: String!) {
            merchant(id: $id) { id name logo { url } }
          }
        """
    }
    shop_info = requests.post(
        "https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getMerchant",
        json=payload,
        headers=headers,
        cookies=cookies_dict,
        timeout=10
    ).json()
    shop_name = shop_info["data"]["merchant"]["name"]

    # Закрываем браузер
    await sess["browser"].close()
    await p.stop()
    sms_sessions.pop(session_id, None)

    # Возвращаем куки-список, merchant_uid, shop_name
    return cookies, merchant_uid, shop_name, guid


async def fetch_preorders(store_id: str,
                          *,
                          pool: Optional[asyncpg.pool.Pool] = None,
                          limit: Optional[int] = None,
                          offset: int = 0) -> list[dict]:
    """
    Получает предзаказы по store_id через пул соединений.
    Если pool не передан — создаёт временный пул и корректно закрывает его.
    """

    pool = await create_pool()

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
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
                """,
                store_id, offset, limit
            )
        
        result = []
        for row in rows:
            item = dict(row)
            
            if isinstance(item.get('warehouses'), str):
                try:
                    import json
                    item['warehouses'] = json.loads(item['warehouses'])
                except (json.JSONDecodeError, TypeError):
                    item['warehouses'] = []
            elif item.get('warehouses') is None:
                item['warehouses'] = []
            result.append(item)
        
        return result
    except asyncpg.PostgresError as e:
        # можно завести свой класс ошибки, если нужно
        raise RuntimeError(f"DB error while fetching preorders: {e}") from e


def generate_preorder_xlsx(preorders: list, store_id: str) -> str:
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
    print(f"✅ Excel сохранён: {filepath}")
    return filepath


def process_preorders_for_excel(rows: list) -> list:
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


def upload_preorder_to_kaspi(filepath: str, merchant_uid: str, cookies: dict):
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
    with open(filepath, 'rb') as f:
        files = {'file': (
            os.path.basename(filepath), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        resp = requests.post(url, headers=headers, cookies=cookies, files=files, timeout=60)
    resp.raise_for_status()
    print(f"📤 Успешно загружено на Kaspi, статус {resp.status_code}")


async def handle_upload_preorder(store_id: str):
    try:
        rows = await fetch_preorders(store_id)
        if not rows:
            print(f"Нет предзаказов для магазина {store_id}")
            return

        # 2) Формируем список для Excel
        preorders_list = process_preorders_for_excel(rows)

        # 3) Генерируем и сохраняем файл с уникальным именем
        filepath = generate_preorder_xlsx(preorders_list, store_id)

        # 4) Загружаем на Kaspi, получая куки через SessionManager
        session_manager = SessionManager(shop_uid=store_id)
        if not await session_manager.load():
            raise HTTPException(status_code=400, detail="Сессия истекла, пожалуйста, войдите заново.")
        cookies = session_manager.get_cookies()
        merchant_id = session_manager.merchant_uid
        
        # 5) Загружаем файл на Kaspi
        upload_preorder_to_kaspi(filepath, merchant_id, cookies)
        
        print(f"✅ Предзаказы для магазина {store_id} успешно загружены на Kaspi")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке предзаказов для магазина {store_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке предзаказов: {str(e)}")


async def create_preorder_from_product(
        product: dict,
        store_id: str,
        *,
        pool: Optional[asyncpg.pool.Pool] = None
) -> dict:
    """
    Создаёт предзаказ на основе товара по product_id для указанного магазина (через asyncpg).
    Возвращает статусы: success | already_preordered | not_found | db_error
    """
    # --- валидация входных данных ---
    if not product or "product_id" not in product:
        return {"success": False, "status": "not_found", "product_id": None}

    product_id_raw = product["product_id"]

    # приведение product_id к UUID (если колонка в БД UUID)
    try:
        product_id = uuid.UUID(str(product_id_raw))
    except (ValueError, TypeError):
        return {"success": False, "status": "not_found", "product_id": product_id_raw}

    own_pool = False
    if pool is None:
        pool = await create_pool()
        own_pool = True

    try:
        async with pool.acquire() as conn:
            # изоляция от гонок: SELECT + INSERT под транзакцией
            async with conn.transaction():
                # 1) Проверяем существующий предзаказ
                row_exists = await conn.fetchval(
                    """
                    SELECT 1
                    FROM preorders
                    WHERE product_id = $1
                      AND store_id = $2
                    """,
                    product_id, store_id
                )
                if row_exists:
                    return {"success": False, "status": "already_preordered", "product_id": str(product_id)}

                # 2) Получаем данные о товаре
                prod = await conn.fetchrow(
                    """
                    SELECT id, kaspi_sku, name, category, price
                    FROM products
                    WHERE id = $1
                    """,
                    product_id
                )
                if not prod:
                    return {"success": False, "status": "not_found", "product_id": str(product_id)}

                # 3) Готовим данные предзаказа
                warehouses = product.get("warehouses", [])
                delivery_days = int(product.get("delivery_days", 30))
                created_at = datetime.now()  # или datetime.utcnow()

                # 4) Вставляем (с ON CONFLICT на случай гонки)
                inserted_id = await conn.fetchval(
                    """
                    INSERT INTO preorders (product_id, store_id, article, name, brand, status,
                                           price, warehouses, delivery_days, created_at)
                    VALUES ($1, $2, $3, $4, $5, 'processing', $6, $7, $8, $9)
                    ON CONFLICT (product_id, store_id) DO NOTHING
                    RETURNING id
                    """,
                    product_id,
                    store_id,
                    prod["kaspi_sku"] or "",
                    prod["name"] or "",
                    prod["category"] or "",
                    int(float(prod["price"] or 0)),
                    warehouses,  # asyncpg сам преобразует dict/list -> jsonb
                    delivery_days,
                    created_at,
                )

                if inserted_id is None:
                    # Конфликт уникальности — уже есть заявка
                    return {"success": False, "status": "already_preordered", "product_id": str(product_id)}

                return {"success": True, "status": "success", "product_id": str(product_id)}

    except asyncpg.PostgresError as e:
        return {"success": False, "status": "db_error", "product_id": str(product_id), "error": str(e)}
    finally:
        if own_pool:
            await pool.close()