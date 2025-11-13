# error_handlers.py
import asyncio
import logging
import os
from datetime import datetime
from typing import Callable, Any

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class ErrorHandler:
    def __init__(self, page: Page):
        self.page = page
        self.screenshot_dir = "screenshots/errors"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def take_error_screenshot(self, error_name: str) -> str:
        """Создает скриншот с ошибкой"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/{error_name}_{timestamp}.png"
        await self.page.screenshot(path=filename)
        return filename

    async def handle_network_error(self, error: Exception) -> bool:
        """Обработка ошибок сети"""
        screenshot_path = await self.take_error_screenshot("network_error")
        logger.error(f"Ошибка сети: {str(error)}")

        # Пробуем перезагрузить страницу
        try:
            await self.page.reload(wait_until="networkidle")
            return True
        except:
            return False

    async def handle_timeout_error(self, error: Exception) -> bool:
        """Обработка ошибок таймаута"""
        screenshot_path = await self.take_error_screenshot("timeout_error")
        logger.error(f"Таймаут при ожидании элемента: {str(error)}")

        # Упрощенная логика: пробуем перезагрузить страницу
        try:
            logger.info("Попытка перезагрузить страницу из-за таймаута...")
            await self.page.reload(wait_until="networkidle")
            logger.info("Страница перезагружена.")
            return True  # Указываем, что обработали и можно попробовать еще раз
        except Exception as e_reload:
            logger.error(f"Ошибка при попытке перезагрузить страницу: {e_reload}")
            return False  # Не смогли обработать

    async def handle_element_not_found(self, selector: str) -> bool:
        """Обработка ошибок отсутствия элемента"""
        screenshot_path = await self.take_error_screenshot("element_not_found")
        logger.error(f"Элемент не найден: {selector}")

        # Пробуем найти элемент по альтернативному селектору
        try:
            # Проверяем, не изменился ли селектор
            elements = await self.page.query_selector_all('*')
            for element in elements:
                text = await element.text_content()
                if text and selector in text:
                    return True
            return False
        except:
            return False

    async def handle_modal_error(self) -> bool:
        """Обработка ошибок модальных окон"""
        screenshot_path = await self.take_error_screenshot("modal_error")
        logger.error("Ошибка при работе с модальным окном")

        # Пробуем закрыть модальное окно
        try:
            close_buttons = await self.page.query_selector_all('button.is-light, .modal-close')
            for button in close_buttons:
                await button.click()
            return True
        except:
            return False

    async def handle_price_update_error(self) -> bool:
        """Обработка ошибок обновления цены"""
        screenshot_path = await self.take_error_screenshot("price_update_error")
        logger.error("Ошибка при обновлении цены")

        # Пробуем очистить поле цены и ввести заново
        try:
            price_input = await self.page.query_selector('input.input.mb-1')
            if price_input:
                await price_input.fill('')
                return True
            return False
        except:
            return False

    async def handle_login_error(self) -> bool:
        """Обработка ошибок входа"""
        screenshot_path = await self.take_error_screenshot("login_error")
        logger.error("Ошибка при входе в систему")

        # Пробуем очистить поля и ввести заново
        try:
            await self.page.fill('#user_email_field', '')
            await self.page.fill('#password_field', '')
            return True
        except:
            return False

    async def handle_navigation_error(self) -> bool:
        """Обработка ошибок навигации"""
        screenshot_path = await self.take_error_screenshot("navigation_error")
        logger.error("Ошибка при навигации")

        # Пробуем вернуться на предыдущую страницу
        try:
            await self.page.go_back()
            return True
        except:
            return False

    async def handle_retry(self, func: Callable, max_retries: int = 3, delay: int = 2) -> Any:
        """Общая функция для повторных попыток"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                logger.error(f"Попытка {attempt + 1} из {max_retries} не удалась: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise

    async def handle_all_errors(self, error: Exception) -> bool:
        """Обработка всех типов ошибок"""
        error_type = type(error).__name__
        handlers = {
            'TimeoutError': self.handle_timeout_error,
            'ElementNotFoundError': self.handle_element_not_found,
            'NetworkError': self.handle_network_error,
            'LoginError': self.handle_login_error,
            'NavigationError': self.handle_navigation_error
        }

        handler = handlers.get(error_type)
        if handler:
            return await handler(error)
        return False
