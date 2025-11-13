# INTEGRATION_CODE_EXAMPLES.py
"""
Конкретные примеры кода для интеграции WAHA с api_parser.py
"""

# ==================== 1. МОДИФИКАЦИЯ API_PARSER.PY ====================

"""
Добавьте эти импорты в начало файла api_parser.py:
"""

# Добавить в начало api_parser.py
import logging
from waha.waha_integration import get_waha_manager
from waha.utils import get_error_handler, get_metrics_collector
from waha.security import get_security_validator

logger = logging.getLogger(__name__)

"""
Замените существующую функцию get_sells() на эту:
"""

async def get_sells(shop_id):
    """
    Получение данных о продажах с интеграцией WAHA уведомлений
    """
    session_manager = SessionManager(shop_uid=shop_id)
    if not await session_manager.load():
        return False, 'Сессия истекла, пожалуйста, войдите заново.'
    
    cookies = session_manager.get_cookies()
    result = get_sells_delivery_request(session_manager.merchant_uid, cookies)
    
    # ========== WAHA ИНТЕГРАЦИЯ ==========
    try:
        waha_manager = get_waha_manager()
        error_handler = get_error_handler()
        metrics_collector = get_metrics_collector()
        security_validator = get_security_validator()
        
        if waha_manager and result.get('orders'):
            logger.info(f"Начинаем обработку {len(result.get('orders', []))} заказов для WAHA уведомлений")
            
            # Обрабатываем заказы для WhatsApp уведомлений
            waha_results = await waha_manager.process_orders_for_store(
                shop_id, 
                result.get('orders', []), 
                session_manager.shop_name or "Магазин"
            )
            
            # Обновляем метрики
            await metrics_collector.increment("orders_processed", len(result.get('orders', [])))
            
            # Логируем результаты WAHA обработки
            successful_notifications = sum(1 for r in waha_results if r.get('success', False))
            logger.info(f"WAHA: успешно отправлено {successful_notifications} из {len(waha_results)} уведомлений")
            
    except Exception as e:
        error_handler.log_error(
            "waha_integration_error",
            f"Ошибка обработки заказов WAHA для магазина {shop_id}: {e}",
            {
                "shop_id": shop_id, 
                "orders_count": len(result.get('orders', [])),
                "error_type": type(e).__name__
            }
        )
        logger.error(f"Ошибка WAHA интеграции для магазина {shop_id}: {e}")
    # ====================================
    
    return True, result

"""
Добавьте эту вспомогательную функцию для проверки WAHA статуса:
"""

async def check_waha_status_for_store(shop_id):
    """
    Проверка статуса WAHA интеграции для конкретного магазина
    """
    try:
        waha_manager = get_waha_manager()
        if not waha_manager:
            return {"status": "not_initialized", "message": "WAHA модуль не инициализирован"}
        
        # Получаем статистику магазина
        stats = await waha_manager.get_store_statistics(shop_id)
        
        # Получаем информацию о сессии
        session_info = await waha_manager.waha_db.get_session_info(shop_id)
        
        # Получаем активный шаблон
        template = await waha_manager.template_manager.get_active_template(shop_id)
        
        return {
            "status": "ok",
            "statistics": stats,
            "session_info": session_info.dict() if session_info else None,
            "has_active_template": template is not None,
            "template_name": template.template_name if template else None
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки WAHA статуса для магазина {shop_id}: {e}")
        return {"status": "error", "message": str(e)}

# ==================== 2. МОДИФИКАЦИЯ MAIN.PY ====================

"""
Добавьте эти импорты в main.py:
"""

from waha.waha_integration import initialize_waha, get_waha_router, shutdown_waha
from waha.config import initialize_config, load_environment_config
from waha.monitoring import initialize_monitoring, shutdown_monitoring

"""
Замените существующие event handlers на эти:
"""

@app.on_event("startup")
async def startup_event():
    """Инициализация приложения с WAHA интеграцией"""
    global pool
    
    logger.info("🚀 Запуск Kaspi Demper с WAHA интеграцией...")
    
    # Создание пула БД (существующий код)
    pool = await create_pool()
    logger.info("✅ База данных подключена")
    
    # Инициализация конфигурации WAHA
    try:
        env_config = load_environment_config("production")  # или "development"
        initialize_config(**env_config)
        logger.info("✅ Конфигурация WAHA загружена")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки конфигурации WAHA: {e}")
    
    # Инициализация WAHA модуля
    try:
        await initialize_waha(pool, "http://localhost:3000")
        logger.info("✅ WAHA модуль инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации WAHA: {e}")
    
    # Инициализация мониторинга
    try:
        waha_manager = get_waha_manager()
        await initialize_monitoring(waha_manager.waha_db)
        logger.info("✅ Мониторинг WAHA инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации мониторинга: {e}")
    
    logger.info("🎉 Приложение успешно запущено!")

@app.on_event("shutdown")
async def shutdown_event():
    """Завершение работы приложения"""
    logger.info("🛑 Завершение работы приложения...")
    
    # Завершение мониторинга
    try:
        await shutdown_monitoring()
        logger.info("✅ Мониторинг WAHA остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка остановки мониторинга: {e}")
    
    # Завершение WAHA модуля
    try:
        await shutdown_waha()
        logger.info("✅ WAHA модуль остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка остановки WAHA: {e}")
    
    # Закрытие пула БД (существующий код)
    if pool:
        await pool.close()
        logger.info("✅ База данных отключена")
    
    logger.info("👋 Приложение завершило работу")

"""
Добавьте роуты WAHA в main.py:
"""

# Добавление роутов WAHA
app.include_router(get_waha_router())

"""
Добавьте эти дополнительные эндпоинты в main.py:
"""

@app.get("/kaspi/waha-status/{shop_id}")
async def get_kaspi_waha_status(shop_id: str):
    """Получение статуса WAHA интеграции для магазина Kaspi"""
    try:
        # Используем функцию из api_parser.py
        from api_parser import check_waha_status_for_store
        status = await check_waha_status_for_store(shop_id)
        
        return {
            "success": True,
            "shop_id": shop_id,
            "waha_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения WAHA статуса для магазина {shop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kaspi/waha-test-notification/{shop_id}")
async def test_waha_notification(shop_id: str, test_data: dict):
    """Тестирование WAHA уведомлений для магазина"""
    try:
        waha_manager = get_waha_manager()
        
        # Создаем тестовые данные заказа
        test_order = {
            "orderId": f"TEST-{int(datetime.now().timestamp())}",
            "customerName": test_data.get("customer_name", "Тестовый клиент"),
            "customerPhone": test_data.get("phone_number", "+7XXXXXXXXXX"),
            "productName": test_data.get("product_name", "Тестовый товар"),
            "quantity": test_data.get("quantity", 1),
            "totalPrice": test_data.get("total_amount", 1000.0),
            "deliveryType": "PICKUP",
            "createDate": int(datetime.now().timestamp() * 1000),
            "status": "NEW"
        }
        
        # Обрабатываем тестовый заказ
        results = await waha_manager.process_orders_for_store(
            shop_id, 
            [test_order], 
            test_data.get("shop_name", "Тестовый магазин")
        )
        
        return {
            "success": True,
            "message": "Тестовое уведомление отправлено",
            "test_order": test_order,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка тестирования WAHA уведомления для магазина {shop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/waha/dashboard")
async def waha_admin_dashboard():
    """Админ панель WAHA интеграции"""
    try:
        waha_manager = get_waha_manager()
        
        # Получаем общую статистику
        enabled_stores = await waha_manager.waha_db.get_enabled_stores()
        
        dashboard_data = {
            "total_stores": len(enabled_stores),
            "waha_server_url": "http://localhost:3000",
            "stores": []
        }
        
        for store_id in enabled_stores:
            try:
                stats = await waha_manager.get_store_statistics(store_id)
                session_info = await waha_manager.waha_db.get_session_info(store_id)
                
                dashboard_data["stores"].append({
                    "store_id": str(store_id),
                    "statistics": stats,
                    "session_status": session_info.status if session_info else "not_configured",
                    "is_connected": session_info.is_connected if session_info else False,
                    "last_activity": session_info.last_activity.isoformat() if session_info and session_info.last_activity else None
                })
            except Exception as e:
                logger.error(f"Ошибка получения данных для магазина {store_id}: {e}")
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения админ панели WAHA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 3. КОНФИГУРАЦИЯ ОКРУЖЕНИЯ ====================

"""
Создайте файл .env в корне проекта:
"""

ENV_CONFIG = """
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/kaspi_demper

# WAHA Configuration
WAHA_SERVER_URL=http://localhost:3000
WAHA_WEBHOOK_BASE_URL=http://your-server.com
WAHA_MAX_MESSAGES_PER_DAY=1000
WAHA_MESSAGE_DELAY_SECONDS=1.0
WAHA_RETRY_ATTEMPTS=3
WAHA_SESSION_TIMEOUT_MINUTES=30

# Security
WAHA_ENABLE_RATE_LIMITING=true
WAHA_RATE_LIMIT_WINDOW_MINUTES=60
WAHA_MAX_MESSAGES_PER_WINDOW=100
WAHA_VALIDATE_PHONE_NUMBERS=true

# Monitoring
WAHA_ENABLE_METRICS=true
WAHA_LOG_LEVEL=INFO
WAHA_ENABLE_ADMIN_NOTIFICATIONS=true
WAHA_ADMIN_NOTIFICATION_THRESHOLD=10

# Development
WAHA_DEBUG_MODE=false
WAHA_MOCK_WAHA_RESPONSES=false
"""

# ==================== 4. ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ API ====================

"""
Примеры вызовов API для настройки и тестирования:
"""

# Пример 1: Быстрая настройка магазина
QUICK_SETUP_EXAMPLE = """
curl -X POST "http://localhost:8000/kaspi/waha-quick-setup/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "waha_server_url": "http://localhost:3000",
    "webhook_url": "http://localhost:8000/webhook/waha"
  }'
"""

# Пример 2: Проверка статуса WAHA
STATUS_CHECK_EXAMPLE = """
curl -X GET "http://localhost:8000/kaspi/waha-status/123e4567-e89b-12d3-a456-426614174000"
"""

# Пример 3: Тестирование уведомления
TEST_NOTIFICATION_EXAMPLE = """
curl -X POST "http://localhost:8000/kaspi/waha-test-notification/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Иван Иванов",
    "phone_number": "+71234567890",
    "product_name": "Тестовый товар",
    "quantity": 2,
    "total_amount": 5000.0,
    "shop_name": "Мой магазин"
  }'
"""

# Пример 4: Получение статистики
STATISTICS_EXAMPLE = """
curl -X GET "http://localhost:8000/waha/statistics/123e4567-e89b-12d3-a456-426614174000?days=7"
"""

# Пример 5: Создание шаблона
TEMPLATE_CREATION_EXAMPLE = """
curl -X POST "http://localhost:8000/waha/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "Уведомление о заказе",
    "template_text": "Здравствуйте, {user_name}! Ваш заказ Nº {order_num} \"{product_name}\", количество: {item_qty} шт готов к самовывозу. С уважением, {shop_name}"
  }'
"""

# ==================== 5. ОБРАБОТКА ОШИБОК ====================

"""
Добавьте эту функцию в api_parser.py для обработки ошибок WAHA:
"""

async def handle_waha_errors(shop_id: str, error: Exception, context: dict = None):
    """
    Централизованная обработка ошибок WAHA
    """
    try:
        error_handler = get_error_handler()
        
        # Логируем ошибку
        error_handler.log_error(
            "waha_error",
            f"Ошибка WAHA для магазина {shop_id}: {str(error)}",
            {
                "shop_id": shop_id,
                "error_type": type(error).__name__,
                "context": context or {}
            }
        )
        
        # В зависимости от типа ошибки принимаем разные действия
        if "connection" in str(error).lower():
            logger.warning(f"Проблема с подключением WAHA для магазина {shop_id}")
        elif "session" in str(error).lower():
            logger.warning(f"Проблема с сессией WAHA для магазина {shop_id}")
        elif "template" in str(error).lower():
            logger.warning(f"Проблема с шаблоном WAHA для магазина {shop_id}")
        else:
            logger.error(f"Неизвестная ошибка WAHA для магазина {shop_id}: {error}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок WAHA: {e}")

# ==================== 6. МОНИТОРИНГ И ЛОГИРОВАНИЕ ====================

"""
Добавьте эту функцию в main.py для периодической проверки WAHA:
"""

async def periodic_waha_health_check():
    """
    Периодическая проверка здоровья WAHA системы
    """
    while True:
        try:
            waha_manager = get_waha_manager()
            if waha_manager:
                # Получаем статус всех магазинов
                enabled_stores = await waha_manager.waha_db.get_enabled_stores()
                
                for store_id in enabled_stores:
                    try:
                        session_info = await waha_manager.waha_db.get_session_info(store_id)
                        if session_info and not session_info.is_connected:
                            logger.warning(f"Сессия WAHA отключена для магазина {store_id}")
                    except Exception as e:
                        logger.error(f"Ошибка проверки сессии для магазина {store_id}: {e}")
            
            # Проверяем каждые 5 минут
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Ошибка периодической проверки WAHA: {e}")
            await asyncio.sleep(60)

# Запуск периодической проверки
@app.on_event("startup")
async def start_periodic_checks():
    asyncio.create_task(periodic_waha_health_check())

# ==================== 7. ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ====================

"""
Создайте файл test_integration.py для тестирования:
"""

TEST_INTEGRATION_CODE = """
import asyncio
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_waha_integration():
    \"\"\"Тест WAHA интеграции\"\"\"
    
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Проверка здоровья системы
        response = await client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "waha" in health_data

@pytest.mark.asyncio
async def test_store_waha_status():
    \"\"\"Тест статуса WAHA для магазина\"\"\"
    
    test_store_id = "test-store-123"
    
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Проверка статуса
        response = await client.get(f"/kaspi/waha-status/{test_store_id}")
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["success"] is True
        assert "waha_status" in status_data

@pytest.mark.asyncio
async def test_waha_notification():
    \"\"\"Тест отправки WAHA уведомления\"\"\"
    
    test_store_id = "test-store-123"
    
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Тестовое уведомление
        response = await client.post(
            f"/kaspi/waha-test-notification/{test_store_id}",
            json={
                "customer_name": "Тестовый клиент",
                "phone_number": "+71234567890",
                "product_name": "Тестовый товар",
                "quantity": 1,
                "total_amount": 1000.0,
                "shop_name": "Тестовый магазин"
            }
        )
        
        assert response.status_code == 200
        result_data = response.json()
        assert result_data["success"] is True
        assert "test_order" in result_data

if __name__ == "__main__":
    asyncio.run(test_waha_integration())
    asyncio.run(test_store_waha_status())
    asyncio.run(test_waha_notification())
    print("✅ Все тесты WAHA интеграции пройдены!")
"""

print("🎯 Примеры кода для интеграции WAHA с api_parser.py готовы!")
print("📝 Скопируйте нужные части кода в соответствующие файлы")
print("🚀 Система готова к интеграции и тестированию!")
