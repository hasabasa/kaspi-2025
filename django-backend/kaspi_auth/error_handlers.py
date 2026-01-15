"""
Обработка ошибок Playwright
Адаптировано из unified-backend/error_handlers.py
"""
import os
import logging
import asyncio
from datetime import datetime
from typing import Callable, Any
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Обработчик ошибок для Playwright"""
    
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
        await self.take_error_screenshot("network_error")
        logger.error(f"Ошибка сети: {str(error)}")
        
        try:
            await self.page.reload(wait_until="networkidle")
            return True
        except:
            return False
    
    async def handle_timeout_error(self, error: Exception) -> bool:
        """Обработка ошибок таймаута"""
        await self.take_error_screenshot("timeout_error")
        logger.error(f"Таймаут при ожидании элемента: {str(error)}")
        
        try:
            logger.info("Попытка перезагрузить страницу из-за таймаута...")
            await self.page.reload(wait_until="networkidle")
            logger.info("Страница перезагружена.")
            return True
        except Exception as e_reload:
            logger.error(f"Ошибка при попытке перезагрузить страницу: {e_reload}")
            return False
    
    async def handle_login_error(self) -> bool:
        """Обработка ошибок входа"""
        await self.take_error_screenshot("login_error")
        logger.error("Ошибка при входе в систему")
        
        try:
            await self.page.fill('#user_email_field', '')
            await self.page.fill('#password_field', '')
            return True
        except:
            return False
    
    async def handle_all_errors(self, error: Exception) -> bool:
        """Обработка всех типов ошибок"""
        error_type = type(error).__name__
        handlers = {
            'TimeoutError': self.handle_timeout_error,
            'NetworkError': self.handle_network_error,
            'LoginError': self.handle_login_error,
        }
        
        handler = handlers.get(error_type)
        if handler:
            return await handler(error)
        return False

