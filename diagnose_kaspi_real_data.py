#!/usr/bin/env python3
"""
Диагностический скрипт для проверки реальных данных Kaspi
"""

import asyncio
import sys
import os
sys.path.append('/Users/hasen/demper-667-45/unified-backend')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def test_kaspi_real_data():
    """Тест получения реальных данных Kaspi"""
    
    email = "hvsv1@icloud.com"
    password = "CIoD29g8U1"
    
    logger.info(f"🔍 [DIAGNOSTIC] Начинаем диагностику Kaspi")
    logger.info(f"📧 [DIAGNOSTIC] Email: {email}")
    
    # Настройка Chrome БЕЗ headless режима для диагностики
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Отключаем headless для диагностики
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        logger.info(f"🌐 [DIAGNOSTIC] Открываем Kaspi...")
        driver.get("https://idmc.shop.kaspi.kz/login")
        time.sleep(3)
        
        logger.info(f"📄 [DIAGNOSTIC] Заголовок страницы: {driver.title}")
        logger.info(f"🌐 [DIAGNOSTIC] Текущий URL: {driver.current_url}")
        
        # Шаг 1: Ввод email
        logger.info(f"📧 [DIAGNOSTIC] Вводим email...")
        email_input = driver.find_element(By.NAME, "username")
        email_input.clear()
        email_input.send_keys(email)
        
        # Нажимаем "Продолжить"
        continue_button = driver.find_element(By.CSS_SELECTOR, "button.button.is-primary")
        continue_button.click()
        logger.info(f"✅ [DIAGNOSTIC] Нажали 'Продолжить'")
        
        time.sleep(2)
        
        # Шаг 2: Ввод пароля
        logger.info(f"🔑 [DIAGNOSTIC] Вводим пароль...")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.clear()
        password_input.send_keys(password)
        
        # Нажимаем "Войти"
        login_button = driver.find_element(By.CSS_SELECTOR, "button.button.is-primary")
        login_button.click()
        logger.info(f"✅ [DIAGNOSTIC] Нажали 'Войти'")
        
        # Ждем перехода
        time.sleep(5)
        
        logger.info(f"🌐 [DIAGNOSTIC] URL после входа: {driver.current_url}")
        logger.info(f"📄 [DIAGNOSTIC] Заголовок после входа: {driver.title}")
        
        # Переходим на страницу магазина
        logger.info(f"🏪 [DIAGNOSTIC] Переходим на страницу магазина...")
        driver.get("https://mc.shop.kaspi.kz/s/m")
        time.sleep(3)
        
        logger.info(f"🌐 [DIAGNOSTIC] URL магазина: {driver.current_url}")
        logger.info(f"📄 [DIAGNOSTIC] Заголовок магазина: {driver.title}")
        
        # Ищем информацию о магазине
        logger.info(f"🔍 [DIAGNOSTIC] Ищем название магазина...")
        
        # Проверяем различные селекторы
        selectors = [
            "h1", "h2", "h3",
            ".title", ".name", ".shop-name", ".merchant-name",
            "[class*='name']", "[class*='title']", "[class*='shop']",
            "[data-testid*='name']", "[data-testid*='title']",
            ".header", ".navbar", ".breadcrumb"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 3:
                        logger.info(f"📝 [DIAGNOSTIC] Найдено в '{selector}': {text}")
            except:
                continue
        
        # Проверяем cookies
        logger.info(f"🍪 [DIAGNOSTIC] Проверяем cookies...")
        cookies = driver.get_cookies()
        for cookie in cookies:
            logger.info(f"🍪 [DIAGNOSTIC] Cookie: {cookie['name']} = {cookie['value'][:30]}...")
        
        # Проверяем JavaScript переменные
        logger.info(f"🔧 [DIAGNOSTIC] Проверяем JS переменные...")
        try:
            js_vars = driver.execute_script("""
                return {
                    merchantId: window.merchantId,
                    shopId: window.shopId,
                    userId: window.userId,
                    storeName: window.storeName,
                    shopName: window.shopName
                };
            """)
            logger.info(f"🔧 [DIAGNOSTIC] JS переменные: {js_vars}")
        except Exception as e:
            logger.error(f"❌ [DIAGNOSTIC] Ошибка JS: {e}")
        
        # Ждем для ручной проверки
        logger.info(f"⏳ [DIAGNOSTIC] Ожидаем 10 секунд для ручной проверки...")
        time.sleep(10)
        
    except Exception as e:
        logger.error(f"❌ [DIAGNOSTIC] Ошибка: {e}")
        import traceback
        logger.error(f"🔍 [DIAGNOSTIC] Traceback: {traceback.format_exc()}")
    
    finally:
        driver.quit()
        logger.info(f"🔚 [DIAGNOSTIC] Диагностика завершена")

if __name__ == "__main__":
    test_kaspi_real_data()
