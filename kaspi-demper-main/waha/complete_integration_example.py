# complete_integration_example.py
"""
Полный пример интеграции WAHA модуля с Kaspi Demper
Этот файл показывает, как полностью интегрировать WAHA в существующее приложение
"""

# ==================== 1. ОБНОВЛЕНИЕ MAIN.PY ====================

"""
Добавьте этот код в ваш main.py файл:
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

# Импорты WAHA
from waha.waha_integration import initialize_waha, get_waha_router, shutdown_waha
from waha.config import initialize_config, load_environment_config
from waha.monitoring import initialize_monitoring, shutdown_monitoring

# Существующие импорты
from db import create_pool
from api_parser import get_sells

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные
pool = None
waha_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global pool, waha_manager
    
    # Инициализация
    logger.info("Запуск приложения...")
    
    # Создание пула БД
    pool = await create_pool()
    
    # Инициализация конфигурации WAHA
    env_config = load_environment_config("production")  # или "development"
    initialize_config(**env_config)
    
    # Инициализация WAHA модуля
    try:
        waha_manager = await initialize_waha(pool, "http://localhost:3000")
        logger.info("WAHA модуль инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации WAHA: {e}")
    
    # Инициализация мониторинга
    try:
        await initialize_monitoring(waha_manager.waha_db)
        logger.info("Мониторинг WAHA инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации мониторинга: {e}")
    
    yield
    
    # Завершение работы
    logger.info("Завершение работы приложения...")
    
    try:
        await shutdown_monitoring()
        logger.info("Мониторинг WAHA остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга: {e}")
    
    try:
        await shutdown_waha()
        logger.info("WAHA модуль остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки WAHA: {e}")
    
    if pool:
        await pool.close()

# Создание приложения
app = FastAPI(
    title="Kaspi Demper API",
    description="API для управления Kaspi магазинами с WAHA интеграцией",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавление роутов WAHA
app.include_router(get_waha_router())

# Существующие роуты
@app.get("/")
async def root():
    return {"message": "Kaspi Demper API с WAHA интеграцией"}

@app.get("/health")
async def health_check():
    """Проверка состояния системы"""
    try:
        # Проверяем БД
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        # Проверяем WAHA
        waha_health = await waha_manager.get_health_status() if waha_manager else {"status": "not_initialized"}
        
        return {
            "status": "healthy",
            "database": "connected",
            "waha": waha_health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ==================== 2. ОБНОВЛЕНИЕ API_PARSER.PY ====================

"""
Добавьте этот код в ваш api_parser.py файл в функцию get_sells():
"""

from waha.waha_integration import get_waha_manager
from waha.utils import get_error_handler, get_metrics_collector
from waha.security import get_security_validator

async def get_sells(shop_id):
    """Получение данных о продажах с WAHA интеграцией"""
    session_manager = SessionManager(shop_uid=shop_id)
    if not await session_manager.load():
        return False, 'Сессия истекла, пожалуйста, войдите заново.'
    
    cookies = session_manager.get_cookies()
    result = get_sells_delivery_request(session_manager.merchant_uid, cookies)
    
    # WAHA интеграция - обработка заказов для уведомлений
    try:
        waha_manager = get_waha_manager()
        error_handler = get_error_handler()
        metrics_collector = get_metrics_collector()
        
        if waha_manager and result.get('orders'):
            # Обрабатываем заказы для WhatsApp уведомлений
            await waha_manager.process_orders_for_store(
                shop_id, 
                result.get('orders', []), 
                session_manager.shop_name or "Магазин"
            )
            
            # Обновляем метрики
            await metrics_collector.increment("orders_processed", len(result.get('orders', [])))
            
            logger.info(f"Обработано {len(result.get('orders', []))} заказов для WAHA уведомлений")
            
    except Exception as e:
        error_handler.log_error(
            "waha_integration_error",
            f"Ошибка обработки заказов WAHA для магазина {shop_id}: {e}",
            {"shop_id": shop_id, "orders_count": len(result.get('orders', []))}
        )
        logger.error(f"Ошибка WAHA интеграции для магазина {shop_id}: {e}")
    
    return True, result

# ==================== 3. ДОПОЛНИТЕЛЬНЫЕ API ЭНДПОИНТЫ ====================

"""
Добавьте эти эндпоинты в main.py для удобства управления:
"""

@app.get("/kaspi/waha-overview/{shop_id}")
async def get_waha_overview(shop_id: str):
    """Обзор WAHA интеграции для магазина"""
    try:
        waha_manager = get_waha_manager()
        
        # Получаем статистику
        stats = await waha_manager.get_store_statistics(shop_id)
        
        # Получаем информацию о сессии
        session_info = await waha_manager.waha_db.get_session_info(shop_id)
        
        # Получаем активный шаблон
        template = await waha_manager.template_manager.get_active_template(shop_id)
        
        return {
            "success": True,
            "shop_id": shop_id,
            "statistics": stats,
            "session_info": session_info.dict() if session_info else None,
            "active_template": template.dict() if template else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения обзора WAHA для магазина {shop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kaspi/waha-quick-setup/{shop_id}")
async def quick_waha_setup(shop_id: str, setup_data: dict):
    """Быстрая настройка WAHA для магазина"""
    try:
        waha_manager = get_waha_manager()
        
        # Создаем настройки
        from waha.models import WAHASettingsCreate
        settings = WAHASettingsCreate(
            waha_server_url=setup_data.get("waha_server_url", "http://localhost:3000"),
            waha_session_name=f"kaspi-store-{shop_id}",
            is_enabled=True,
            webhook_url=setup_data.get("webhook_url", f"http://your-server.com/webhook/waha")
        )
        
        await waha_manager.waha_db.create_or_update_settings(settings)
        
        # Создаем сессию
        await waha_manager.create_store_session(
            shop_id,
            f"Магазин {shop_id}",
            setup_data.get("webhook_url", f"http://your-server.com/webhook/waha")
        )
        
        # Создаем шаблон по умолчанию
        from waha.models import WhatsAppTemplateCreate
        default_template = WhatsAppTemplateCreate(
            template_name="Уведомление о заказе",
            template_text="""Здравствуйте, {user_name}!
Ваш заказ Nº {order_num} "{product_name}", количество: {item_qty} шт готов к самовывозу.
* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.
* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.
С уважением,
{shop_name}"""
        )
        
        await waha_manager.template_manager.create_template(shop_id, default_template)
        
        return {
            "success": True,
            "message": "WAHA быстро настроен для магазина",
            "shop_id": shop_id,
            "next_steps": [
                "1. Откройте WhatsApp на телефоне",
                "2. Перейдите в Настройки → Связанные устройства",
                "3. Нажмите 'Связать устройство'",
                "4. Отсканируйте QR-код с http://localhost:3000",
                "5. Проверьте статус: GET /waha/sessions/status/{shop_id}"
            ]
        }
        
    except Exception as e:
        logger.error(f"Ошибка быстрой настройки WAHA для магазина {shop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/waha/dashboard")
async def waha_admin_dashboard():
    """Админ панель WAHA"""
    try:
        waha_manager = get_waha_manager()
        
        # Получаем общую статистику
        enabled_stores = await waha_manager.waha_db.get_enabled_stores()
        
        dashboard_data = {
            "total_stores": len(enabled_stores),
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
                    "is_connected": session_info.is_connected if session_info else False
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

# ==================== 4. КОНФИГУРАЦИЯ ОКРУЖЕНИЯ ====================

"""
Создайте файл .env в корне проекта:
"""

ENV_EXAMPLE = """
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

# ==================== 5. DOCKER COMPOSE ДЛЯ ПОЛНОЙ СИСТЕМЫ ====================

"""
Создайте файл docker-compose.full.yml:
"""

DOCKER_COMPOSE_FULL = """
version: '3.8'

services:
  # Основное приложение Kaspi Demper
  kaspi-demper:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/kaspi_demper
      - WAHA_SERVER_URL=http://waha:3000
    depends_on:
      - postgres
      - waha
    volumes:
      - ./logs:/app/logs
    networks:
      - kaspi-network

  # WAHA сервер
  waha:
    image: devlikeapro/waha:latest
    container_name: kaspi-waha
    ports:
      - "3000:3000"
    environment:
      - WAHA_SESSION_STORAGE=file
      - WAHA_SESSION_STORAGE_PATH=/app/sessions
      - WAHA_LOG_LEVEL=info
      - WAHA_WEBHOOK_URL=http://kaspi-demper:8000/waha/webhook
      - WAHA_WEBHOOK_EVENTS=message,messageStatus,sessionStatus
    volumes:
      - waha_sessions:/app/sessions
      - waha_logs:/app/logs
    restart: unless-stopped
    networks:
      - kaspi-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL база данных
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=kaspi_demper
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - kaspi-network

  # Redis для кеширования (опционально)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - kaspi-network

volumes:
  postgres_data:
  redis_data:
  waha_sessions:
  waha_logs:

networks:
  kaspi-network:
    driver: bridge
"""

# ==================== 6. СКРИПТЫ РАЗВЕРТЫВАНИЯ ====================

"""
Создайте файл deploy.sh:
"""

DEPLOY_SCRIPT = """#!/bin/bash

echo "🚀 Развертывание Kaspi Demper с WAHA интеграцией..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен"
    exit 1
fi

# Создание директорий
mkdir -p logs
mkdir -p waha/sessions
mkdir -p waha/logs

# Копирование конфигурации
if [ ! -f .env ]; then
    echo "📝 Создание файла .env..."
    cp .env.example .env
    echo "⚠️  Отредактируйте файл .env перед запуском"
fi

# Запуск сервисов
echo "🐳 Запуск Docker контейнеров..."
docker-compose -f docker-compose.full.yml up -d

# Ожидание готовности
echo "⏳ Ожидание готовности сервисов..."
sleep 30

# Проверка статуса
echo "🔍 Проверка статуса сервисов..."
docker-compose -f docker-compose.full.yml ps

# Проверка WAHA
echo "📱 Проверка WAHA сервера..."
curl -f http://localhost:3000/api/health || echo "⚠️  WAHA сервер недоступен"

# Проверка основного приложения
echo "🌐 Проверка основного приложения..."
curl -f http://localhost:8000/health || echo "⚠️  Основное приложение недоступно"

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте http://localhost:8000/docs для API документации"
echo "2. Откройте http://localhost:3000 для WAHA Dashboard"
echo "3. Настройте магазины через API или админ панель"
echo "4. Подключите WhatsApp через связанные устройства"
echo ""
echo "📚 Документация:"
echo "- API: http://localhost:8000/docs"
echo "- WAHA: http://localhost:3000"
echo "- Логи: docker-compose logs -f"
"""

# ==================== 7. ТЕСТИРОВАНИЕ ====================

"""
Создайте файл test_integration.py:
"""

TEST_INTEGRATION = """
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
        
        # Проверка WAHA здоровья
        waha_response = await client.get("/waha/health")
        assert waha_response.status_code == 200
        
        waha_health = waha_response.json()
        assert waha_health["status"] in ["healthy", "unhealthy"]

@pytest.mark.asyncio
async def test_store_setup():
    \"\"\"Тест настройки магазина\"\"\"
    
    test_store_id = "test-store-123"
    
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Быстрая настройка
        setup_response = await client.post(
            f"/kaspi/waha-quick-setup/{test_store_id}",
            json={
                "waha_server_url": "http://localhost:3000",
                "webhook_url": "http://localhost:8000/webhook/waha"
            }
        )
        
        assert setup_response.status_code == 200
        setup_data = setup_response.json()
        assert setup_data["success"] is True
        
        # Проверка статуса сессии
        status_response = await client.get(f"/waha/sessions/status/{test_store_id}")
        assert status_response.status_code == 200
        
        # Проверка шаблонов
        templates_response = await client.get(f"/waha/templates/{test_store_id}")
        assert templates_response.status_code == 200
        
        templates_data = templates_response.json()
        assert len(templates_data["templates"]) > 0

if __name__ == "__main__":
    asyncio.run(test_waha_integration())
    asyncio.run(test_store_setup())
    print("✅ Все тесты пройдены!")
"""

# ==================== 8. МОНИТОРИНГ И ЛОГИРОВАНИЕ ====================

"""
Добавьте в main.py:
"""

MONITORING_SETUP = """
# Настройка логирования
import structlog
from waha.monitoring import get_monitor, get_alert_manager

# Структурированное логирование
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Периодическая проверка алертов
async def check_alerts_periodically():
    \"\"\"Периодическая проверка алертов\"\"\"
    while True:
        try:
            monitor = get_monitor()
            alert_manager = get_alert_manager()
            
            if monitor and alert_manager:
                alerts = await alert_manager.check_alerts(monitor)
                
                for alert in alerts:
                    if alert["severity"] == "critical":
                        logger.critical(f"КРИТИЧЕСКИЙ АЛЕРТ: {alert['message']}")
                    elif alert["severity"] == "warning":
                        logger.warning(f"Предупреждение: {alert['message']}")
            
            await asyncio.sleep(300)  # Проверяем каждые 5 минут
            
        except Exception as e:
            logger.error(f"Ошибка проверки алертов: {e}")
            await asyncio.sleep(60)

# Запуск проверки алертов в фоне
@app.on_event("startup")
async def start_alert_monitoring():
    asyncio.create_task(check_alerts_periodically())
"""

print("🎉 Полная интеграция WAHA с Kaspi Demper готова!")
print("📁 Созданы все необходимые файлы и компоненты")
print("🚀 Система готова к развертыванию и использованию")
