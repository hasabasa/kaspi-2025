"""
SMS авторизация Kaspi
Адаптировано из unified-backend/api_parser.py
"""
import uuid
import asyncio
import logging
import requests
from typing import Dict, Tuple
from playwright.async_api import async_playwright, Page
from kaspi_auth.error_handlers import ErrorHandler
from kaspi_auth.kaspi_auth_service import get_formatted_cookies
from kaspi_auth.session_manager import SessionManager

logger = logging.getLogger(__name__)

# Хранилище SMS сессий (в продакшене использовать Redis)
sms_sessions = {}


def run_async(coro):
    """Запускает async функцию синхронно"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def sms_login_start(user_id: str, phone: str) -> str:
    """
    Начало SMS авторизации
    Открываем Playwright, вводим phone → click send.
    Возвращаем session_id и держим page открытой.
    """
    session_id = str(uuid.uuid4())
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context()
    page: Page = await context.new_page()
    
    logger.info("Переход на страницу входа sms...")
    await page.goto("https://idmc.shop.kaspi.kz/login")
    await page.wait_for_load_state('domcontentloaded')
    await page.wait_for_selector('#phone_tab', timeout=30000)
    await page.click("#phone_tab")
    
    # Ввод телефона
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


async def sms_login_verify(session_id: str, user_id: str, code: str) -> Tuple[list, str, str, dict]:
    """
    Проверка SMS кода
    Берём сохранённую сессию, вводим код, ждём входа, парсим merchant info.
    """
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    
    sess = sms_sessions.get(session_id)
    if not sess:
        raise Exception("session_id не найден")
    
    page = sess["page"]
    context = sess["context"]
    p = sess["playwright"]
    error_handler = ErrorHandler(page)
    
    # Ввод кода
    await page.wait_for_selector('input[name="security-code"]', timeout=30000)
    await page.fill('input[name="security-code"]', code)
    await page.click('.button.is-primary')
    
    # Проверка ошибки
    error_element = None
    try:
        error_element = await page.wait_for_selector('.help.is-danger', timeout=3_000)
    except PlaywrightTimeoutError:
        pass
    
    if error_element:
        error_text = (await error_element.text_content() or "").strip()
        logger.warning(f"Kaspi SMS-login error: {error_text}")
        raise Exception(f"Ошибка авторизации: {error_text}")
    
    # Ждём загрузки панели навигации
    await page.wait_for_selector('nav.navbar', timeout=30000)
    
    # Забираем куки
    cookies = await page.context.cookies()
    cookies_dict = get_formatted_cookies(cookies)
    
    # Получаем информацию о магазине
    headers = {
        "x-auth-version": "3",
        "Origin": "https://kaspi.kz",
        "Referer": "https://kaspi.kz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
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
        raise Exception("Не удалось получить merchant_uid")
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
    
    # Сохраняем сессию
    session_manager = SessionManager(user_id=user_id)
    guid = session_manager.save(cookies, None, None)
    
    # Закрываем браузер
    await sess["browser"].close()
    await p.stop()
    sms_sessions.pop(session_id, None)
    
    return cookies, merchant_uid, shop_name, guid

