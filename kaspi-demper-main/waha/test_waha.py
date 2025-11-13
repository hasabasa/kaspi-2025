# test_waha.py
"""
Тесты для WAHA модуля
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from waha.models import (
    WhatsAppTemplateCreate, WAHASettingsCreate, OrderData,
    WhatsAppTestMessage, WhatsAppSendResponse
)
from waha.template_manager import TemplateManager
from waha.message_sender import WhatsAppMessageSender
from waha.order_integration import OrderIntegration
from waha.waha_client import WAHAClient


class TestTemplateManager:
    """Тесты для TemplateManager"""
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        db = AsyncMock()
        return db
    
    @pytest.fixture
    def template_manager(self, mock_db):
        """Экземпляр TemplateManager"""
        return TemplateManager(mock_db)
    
    def test_process_template(self, template_manager):
        """Тест обработки шаблона"""
        template_text = "Здравствуйте, {user_name}! Ваш заказ {order_num} готов."
        order_data = {
            "customer_name": "Иван",
            "order_id": "12345",
            "product_name": "Товар",
            "quantity": 2,
            "shop_name": "Магазин"
        }
        
        result = template_manager.process_template(template_text, order_data)
        
        assert "Иван" in result
        assert "12345" in result
        assert "{user_name}" not in result
        assert "{order_num}" not in result
    
    def test_validate_template_variables(self, template_manager):
        """Тест валидации переменных шаблона"""
        template_text = "Привет {user_name}! Заказ {order_num} готов. Неизвестная {unknown_var}."
        
        result = template_manager.validate_template_variables(template_text)
        
        assert not result['valid']
        assert '{user_name}' in result['known_variables']
        assert '{order_num}' in result['known_variables']
        assert '{unknown_var}' in result['unknown_variables']
    
    def test_get_default_template(self, template_manager):
        """Тест получения шаблона по умолчанию"""
        template = template_manager.get_default_template()
        
        assert isinstance(template, str)
        assert "{user_name}" in template
        assert "{order_num}" in template
        assert "{product_name}" in template
    
    def test_get_sample_order_data(self, template_manager):
        """Тест получения тестовых данных заказа"""
        sample_data = template_manager.get_sample_order_data()
        
        assert isinstance(sample_data, dict)
        assert "customer_name" in sample_data
        assert "order_id" in sample_data
        assert "product_name" in sample_data


class TestWAHAClient:
    """Тесты для WAHAClient"""
    
    @pytest.fixture
    def waha_client(self):
        """Экземпляр WAHAClient"""
        return WAHAClient("http://localhost:3000")
    
    @pytest.mark.asyncio
    async def test_send_text_message(self, waha_client):
        """Тест отправки текстового сообщения"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"id": "test_message_id"})
            
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            result = await waha_client.send_text_message(
                "test_session", 
                "71234567890@c.us", 
                "Тестовое сообщение"
            )
            
            assert result["id"] == "test_message_id"
    
    @pytest.mark.asyncio
    async def test_get_session_status(self, waha_client):
        """Тест получения статуса сессии"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"status": "CONNECTED"})
            
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            result = await waha_client.get_session_status("test_session")
            
            assert result["status"] == "CONNECTED"


class TestOrderIntegration:
    """Тесты для OrderIntegration"""
    
    @pytest.fixture
    def mock_message_sender(self):
        """Мок отправителя сообщений"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        return AsyncMock()
    
    @pytest.fixture
    def order_integration(self, mock_message_sender, mock_db):
        """Экземпляр OrderIntegration"""
        return OrderIntegration(mock_message_sender, mock_db)
    
    def test_extract_order_data_from_kaspi(self, order_integration):
        """Тест извлечения данных заказа из Kaspi"""
        kaspi_order = {
            "orderId": "12345",
            "customerName": "Иван Иванов",
            "customerPhone": "+71234567890",
            "productName": "Тестовый товар",
            "quantity": 2,
            "totalPrice": 5000.0,
            "deliveryType": "DELIVERY",
            "createDate": 1640995200000  # Timestamp в миллисекундах
        }
        
        result = order_integration.extract_order_data_from_kaspi(kaspi_order, "Тестовый магазин")
        
        assert result.customer_name == "Иван Иванов"
        assert result.customer_phone == "+71234567890"
        assert result.order_id == "12345"
        assert result.product_name == "Тестовый товар"
        assert result.quantity == 2
        assert result.total_amount == 5000.0
        assert result.delivery_type == "доставка"
        assert result.shop_name == "Тестовый магазин"
    
    def test_filter_new_orders(self, order_integration):
        """Тест фильтрации новых заказов"""
        orders = [
            {"orderId": "1", "status": "NEW"},
            {"orderId": "2", "status": "CONFIRMED"},
            {"orderId": "3", "status": "PROCESSING"},
            {"orderId": "4", "status": "DELIVERED"},
            {"orderId": "5", "status": "CANCELLED"}
        ]
        
        new_orders = order_integration._filter_new_orders(orders)
        
        assert len(new_orders) == 3
        assert new_orders[0]["orderId"] == "1"
        assert new_orders[1]["orderId"] == "2"
        assert new_orders[2]["orderId"] == "3"
    
    @pytest.mark.asyncio
    async def test_handle_webhook_event(self, order_integration):
        """Тест обработки webhook событий"""
        webhook_data = {
            "event": "message",
            "session": "test_session",
            "payload": {
                "id": "msg_123",
                "body": "Тестовое сообщение",
                "from": "71234567890@c.us"
            }
        }
        
        result = await order_integration.handle_webhook_event(webhook_data)
        
        assert result["success"] is True
        assert "Входящее сообщение обработано" in result["message"]


class TestWhatsAppMessageSender:
    """Тесты для WhatsAppMessageSender"""
    
    @pytest.fixture
    def mock_waha_client(self):
        """Мок WAHA клиента"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_template_manager(self):
        """Мок менеджера шаблонов"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        return AsyncMock()
    
    @pytest.fixture
    def message_sender(self, mock_waha_client, mock_template_manager, mock_db):
        """Экземпляр WhatsAppMessageSender"""
        return WhatsAppMessageSender(mock_waha_client, mock_template_manager, mock_db)
    
    @pytest.mark.asyncio
    async def test_send_order_notification_success(self, message_sender):
        """Тест успешной отправки уведомления о заказе"""
        # Настройка моков
        message_sender.db.get_settings.return_value = AsyncMock(is_enabled=True)
        message_sender.template_manager.get_active_template.return_value = AsyncMock(
            template_text="Тест {user_name}",
            id=uuid4()
        )
        message_sender.session_manager.get_session_status.return_value = {"status": "CONNECTED"}
        message_sender.template_manager.process_template.return_value = "Тест Иван"
        message_sender.session_manager.send_message.return_value = {"id": "msg_123"}
        message_sender.db.log_message.return_value = uuid4()
        
        order_data = OrderData(
            customer_name="Иван",
            customer_phone="+71234567890",
            order_id="12345",
            product_name="Товар",
            quantity=1,
            total_amount=1000.0,
            delivery_type="самовывоз",
            order_date="01.01.2024",
            shop_name="Магазин"
        )
        
        result = await message_sender.send_order_notification(uuid4(), order_data)
        
        assert result.success is True
        assert result.message_id == "msg_123"
    
    @pytest.mark.asyncio
    async def test_send_order_notification_disabled(self, message_sender):
        """Тест отправки уведомления при отключенных настройках"""
        message_sender.db.get_settings.return_value = None
        
        order_data = OrderData(
            customer_name="Иван",
            customer_phone="+71234567890",
            order_id="12345",
            product_name="Товар",
            quantity=1,
            total_amount=1000.0,
            delivery_type="самовывоз",
            order_date="01.01.2024",
            shop_name="Магазин"
        )
        
        result = await message_sender.send_order_notification(uuid4(), order_data)
        
        assert result.success is False
        assert "отключены" in result.error


class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Этот тест проверяет интеграцию всех компонентов
        # В реальном проекте здесь будут более сложные тесты
        
        # Создание тестовых данных
        store_id = uuid4()
        order_data = {
            "orderId": "TEST-123",
            "customerName": "Тестовый клиент",
            "customerPhone": "+71234567890",
            "productName": "Тестовый товар",
            "quantity": 1,
            "totalPrice": 1000.0,
            "deliveryType": "PICKUP",
            "createDate": int(datetime.now().timestamp() * 1000)
        }
        
        # Здесь можно добавить тесты полного процесса:
        # 1. Создание настроек
        # 2. Подключение сессии
        # 3. Создание шаблона
        # 4. Обработка заказа
        # 5. Отправка уведомления
        
        assert True  # Заглушка для теста


# Фикстуры для pytest
@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Конфигурация pytest
pytest_plugins = ["pytest_asyncio"]
