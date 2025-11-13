# integration_example.py
"""
Пример интеграции WAHA модуля с основным приложением Kaspi Demper
"""

# Добавьте этот код в main.py для интеграции WAHA

from waha.waha_integration import initialize_waha, get_waha_router, shutdown_waha, get_waha_manager

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

@app.on_event("startup")
async def startup_event():
    """Инициализация приложения"""
    # ... существующий код инициализации ...
    
    # Инициализация WAHA модуля
    try:
        await initialize_waha(pool, "http://localhost:3000")
        logger.info("WAHA модуль инициализирован успешно")
    except Exception as e:
        logger.error(f"Ошибка инициализации WAHA модуля: {e}")

# Добавление роутов WAHA
app.include_router(get_waha_router())

@app.on_event("shutdown")
async def shutdown_event():
    """Завершение работы приложения"""
    # ... существующий код завершения ...
    
    # Завершение работы WAHA модуля
    try:
        await shutdown_waha()
        logger.info("WAHA модуль завершил работу")
    except Exception as e:
        logger.error(f"Ошибка завершения работы WAHA модуля: {e}")


# ==================== МОДИФИКАЦИЯ API_PARSER.PY ====================

# Добавьте этот код в api_parser.py в функцию get_sells()

async def get_sells(shop_id):
    """Получение данных о продажах с интеграцией WAHA"""
    session_manager = SessionManager(shop_uid=shop_id)
    if not await session_manager.load():
        return False, 'Сессия истекла, пожалуйста, войдите заново.'
    
    cookies = session_manager.get_cookies()
    result = get_sells_delivery_request(session_manager.merchant_uid, cookies)
    
    # Обработка заказов для WhatsApp уведомлений
    try:
        waha_manager = get_waha_manager()
        await waha_manager.process_orders_for_store(
            shop_id, 
            result.get('orders', []), 
            session_manager.shop_name or "Магазин"
        )
        logger.info(f"Обработано {len(result.get('orders', []))} заказов для WAHA уведомлений")
    except Exception as e:
        logger.error(f"Ошибка обработки заказов WAHA для магазина {shop_id}: {e}")
    
    return True, result


# ==================== ДОПОЛНИТЕЛЬНЫЕ ЭНДПОИНТЫ ====================

# Добавьте эти эндпоинты в main.py для удобства управления

@app.get("/kaspi/waha-status/{shop_id}")
async def get_kaspi_waha_status(shop_id: str):
    """Получение статуса WAHA для магазина Kaspi"""
    try:
        waha_manager = get_waha_manager()
        stats = await waha_manager.get_store_statistics(shop_id)
        
        return {
            "success": True,
            "shop_id": shop_id,
            "waha_statistics": stats
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса WAHA для магазина {shop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kaspi/waha-test/{shop_id}")
async def test_waha_integration(shop_id: str, test_data: dict):
    """Тестирование WAHA интеграции для магазина"""
    try:
        waha_manager = get_waha_manager()
        
        # Создаем тестовые данные заказа
        test_order = {
            "orderId": "TEST-12345",
            "customerName": test_data.get("customer_name", "Тестовый клиент"),
            "customerPhone": test_data.get("phone_number", "+7XXXXXXXXXX"),
            "productName": "Тестовый товар",
            "quantity": 1,
            "totalPrice": 1000.0,
            "deliveryType": "PICKUP",
            "createDate": int(datetime.now().timestamp() * 1000)
        }
        
        # Обрабатываем тестовый заказ
        results = await waha_manager.process_orders_for_store(
            shop_id, 
            [test_order], 
            "Тестовый магазин"
        )
        
        return {
            "success": True,
            "message": "Тестовое уведомление отправлено",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка тестирования WAHA для магазина {shop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBHOOK ОБРАБОТКА ====================

@app.post("/webhook/waha")
async def waha_webhook_handler(request: Request):
    """Обработка webhook событий от WAHA"""
    try:
        webhook_data = await request.json()
        
        # Получаем менеджер WAHA
        waha_manager = get_waha_manager()
        
        # Обрабатываем webhook событие
        result = await waha_manager.order_integration.handle_webhook_event(webhook_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка обработки WAHA webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== АДМИН ПАНЕЛЬ ====================

@app.get("/admin/waha/overview")
async def waha_admin_overview():
    """Обзор WAHA интеграции для администратора"""
    try:
        waha_manager = get_waha_manager()
        
        # Получаем статистику по всем магазинам
        enabled_stores = await waha_manager.waha_db.get_enabled_stores()
        
        overview_data = {
            "total_stores": len(enabled_stores),
            "waha_server_url": waha_manager.waha_server_url,
            "stores": []
        }
        
        for store_id in enabled_stores:
            try:
                stats = await waha_manager.get_store_statistics(store_id)
                session_info = await waha_manager.waha_db.get_session_info(store_id)
                
                overview_data["stores"].append({
                    "store_id": str(store_id),
                    "statistics": stats,
                    "session_info": session_info.dict() if session_info else None
                })
            except Exception as e:
                logger.error(f"Ошибка получения данных для магазина {store_id}: {e}")
        
        return {
            "success": True,
            "overview": overview_data
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения обзора WAHA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== КОНФИГУРАЦИЯ ====================

# Добавьте эти переменные в config.py или .env

WAHA_CONFIG = {
    "server_url": "http://localhost:3000",
    "webhook_url": "http://your-server.com/webhook/waha",
    "max_messages_per_day": 1000,
    "message_delay_seconds": 1,
    "retry_attempts": 3,
    "session_timeout_minutes": 30
}

# ==================== МОНИТОРИНГ ====================

@app.get("/health/waha")
async def waha_health_check():
    """Проверка состояния WAHA интеграции"""
    try:
        waha_manager = get_waha_manager()
        
        # Проверяем доступность WAHA сервера
        async with waha_manager.waha_client:
            sessions = await waha_manager.waha_client.get_sessions()
        
        # Получаем статистику активных сессий
        active_sessions = len(session_manager.active_sessions)
        
        return {
            "status": "healthy",
            "waha_server": "available",
            "active_sessions": active_sessions,
            "total_sessions": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"WAHA health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ==================== ЛОГИРОВАНИЕ ====================

# Добавьте в logging configuration

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "waha_file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "logs/waha.log",
        },
    },
    "loggers": {
        "waha": {
            "level": "INFO",
            "handlers": ["default", "waha_file"],
            "propagate": False,
        },
    },
}

# ==================== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ====================

"""
Примеры использования WAHA интеграции:

1. Создание настроек для магазина:
curl -X POST "http://localhost:8000/waha/settings/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "waha_server_url": "http://localhost:3000",
    "waha_session_name": "kaspi-session",
    "is_enabled": true,
    "webhook_url": "http://localhost:8000/webhook/waha"
  }'

2. Подключение WhatsApp сессии:
curl -X POST "http://localhost:8000/waha/sessions/connect/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "http://localhost:8000/webhook/waha"}'

3. Создание шаблона сообщения:
curl -X POST "http://localhost:8000/waha/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "Уведомление о заказе",
    "template_text": "Здравствуйте, {user_name}! Ваш заказ Nº {order_num} готов к самовывозу."
  }'

4. Отправка тестового сообщения:
curl -X POST "http://localhost:8000/waha/send-test/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+7XXXXXXXXXX",
    "template_text": "Тестовое сообщение для {user_name}",
    "sample_data": {"user_name": "Тест"}
  }'

5. Проверка статуса:
curl -X GET "http://localhost:8000/waha/sessions/status/123e4567-e89b-12d3-a456-426614174000"

6. Получение статистики:
curl -X GET "http://localhost:8000/waha/statistics/123e4567-e89b-12d3-a456-426614174000?days=30"
"""
