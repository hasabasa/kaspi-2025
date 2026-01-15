"""
Сервис для аутентификации в Kaspi через Playwright
Адаптировано из unified-backend/api_parser.py
"""
import asyncio
import aiohttp
import json
import logging
from typing import Tuple, Optional
from playwright.async_api import async_playwright, Page, Cookie
from django.conf import settings

logger = logging.getLogger(__name__)


async def login_to_kaspi(page: Page, email: str, password: str) -> Tuple[bool, list]:
    """Вход в кабинет Kaspi и сохранение cookies"""
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
            raise Exception(f"Ошибка при входе: {error_text}")

        # Получение cookies
        cookies = await page.context.cookies()
        return True, cookies

    except Exception as e:
        logger.error(f"❌ Ошибка при входе: {str(e)}")
        raise


def get_formatted_cookies(cookies: list) -> dict:
    """Преобразует cookies из списка в словарь"""
    formatted_cookies = {}
    for cookie in cookies:
        if isinstance(cookie, dict):
            formatted_cookies[cookie.get('name', '')] = cookie.get('value', '')
    return formatted_cookies


async def login_and_get_merchant_info(email: str, password: str, user_id: str) -> Tuple[list, str, str, dict]:
    """
    Выполняет логин в Kaspi и получает информацию о магазине
    Возвращает: (cookies, merchant_uid, shop_name, guid)
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            success, cookies = await login_to_kaspi(page, email, password)
            cookies_dict = get_formatted_cookies(cookies)

            # Получаем информацию о магазине
            headers = {
                "x-auth-version": "3",
                "Origin": "https://kaspi.kz",
                "Referer": "https://kaspi.kz/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
            }

            async with aiohttp.ClientSession() as session:
                # Получаем список магазинов
                async with session.get(
                    "https://mc.shop.kaspi.kz/s/m",
                    headers=headers,
                    cookies=cookies_dict
                ) as response:
                    response_merchants = await response.json()

                # Извлекаем merchant_uid
                if isinstance(response_merchants.get('merchants'), list) and len(response_merchants['merchants']) > 0:
                    merchant_uid = response_merchants['merchants'][0]['uid']
                else:
                    raise Exception("Не удалось извлечь merchant_uid из ответа Kaspi")

                # Получаем информацию о магазине
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
                async with session.post(
                    url_shop_info,
                    json=payload,
                    headers=headers,
                    cookies=cookies_dict
                ) as response_shop_info:
                    shop_info = await response_shop_info.json()
                    shop_name = shop_info['data']['merchant']['name']

            await browser.close()

            # Формируем guid для сохранения
            guid = {
                "cookies": cookies,
                "email": email,
                "password": password
            }

            return cookies, merchant_uid, shop_name, guid

    except Exception as e:
        logger.error(f"Ошибка при авторизации: {str(e)}")
        raise


def run_async(coro):
    """Запускает async функцию синхронно"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

