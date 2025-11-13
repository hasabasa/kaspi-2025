# DEPLOYMENT.md
# Инструкция по развертыванию WAHA интеграции

## Быстрый старт

### 1. Запуск WAHA сервера

```bash
# Перейдите в директорию waha
cd /Users/hasen/demper-667-45/kaspi-demper-main/waha/

# Запустите WAHA сервер
docker-compose -f docker-compose.waha.yml up -d

# Проверьте статус
docker ps | grep waha
```

### 2. Интеграция с основным приложением

Добавьте в `main.py`:

```python
# Импорты
from waha.waha_integration import initialize_waha, get_waha_router, shutdown_waha

# Инициализация
@app.on_event("startup")
async def startup_event():
    # ... существующий код ...
    await initialize_waha(pool, "http://localhost:3000")

# Роуты
app.include_router(get_waha_router())

# Завершение
@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_waha()
```

### 3. Модификация api_parser.py

Добавьте в функцию `get_sells()`:

```python
from waha.waha_integration import get_waha_manager

async def get_sells(shop_id):
    # ... существующий код ...
    
    # WAHA интеграция
    try:
        waha_manager = get_waha_manager()
        await waha_manager.process_orders_for_store(
            shop_id, 
            result.get('orders', []), 
            session_manager.shop_name or "Магазин"
        )
    except Exception as e:
        logger.error(f"WAHA error: {e}")
    
    return True, result
```

## Пошаговая настройка

### Шаг 1: Настройка магазина

```bash
# Создайте настройки WAHA для магазина
curl -X POST "http://localhost:8000/waha/settings/YOUR_STORE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "waha_server_url": "http://localhost:3000",
    "waha_session_name": "kaspi-session",
    "is_enabled": true,
    "webhook_url": "http://your-server.com/webhook/waha"
  }'
```

### Шаг 2: Подключение WhatsApp

```bash
# Создайте сессию
curl -X POST "http://localhost:8000/waha/sessions/connect/YOUR_STORE_ID" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "http://your-server.com/webhook/waha"}'
```

**Затем:**
1. Откройте WhatsApp на телефоне
2. Настройки → Связанные устройства
3. Связать устройство
4. Отсканируйте QR-код

### Шаг 3: Создание шаблона

```bash
# Создайте шаблон сообщения
curl -X POST "http://localhost:8000/waha/templates/YOUR_STORE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "Уведомление о заказе",
    "template_text": "Здравствуйте, {user_name}! Ваш заказ Nº {order_num} \"{product_name}\", количество: {item_qty} шт готов к самовывозу. С уважением, {shop_name}"
  }'
```

### Шаг 4: Тестирование

```bash
# Отправьте тестовое сообщение
curl -X POST "http://localhost:8000/waha/send-test/YOUR_STORE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+7XXXXXXXXXX",
    "template_text": "Тест для {user_name}",
    "sample_data": {"user_name": "Тест"}
  }'
```

## Проверка работы

### Статус WAHA сервера
```bash
curl http://localhost:3000/api/health
```

### Статус интеграции
```bash
curl http://localhost:8000/waha/health
```

### Статус сессии магазина
```bash
curl http://localhost:8000/waha/sessions/status/YOUR_STORE_ID
```

## Мониторинг

### Логи WAHA
```bash
docker logs kaspi-waha -f
```

### Логи приложения
```bash
tail -f logs/waha.log
```

### Статистика сообщений
```bash
curl http://localhost:8000/waha/statistics/YOUR_STORE_ID?days=7
```

## Troubleshooting

### Проблема: WAHA сервер недоступен
```bash
# Проверьте статус контейнера
docker ps | grep waha

# Перезапустите если нужно
docker-compose -f docker-compose.waha.yml restart
```

### Проблема: Сессия не подключается
1. Проверьте QR-код в браузере: `http://localhost:3000`
2. Убедитесь, что телефон подключен к интернету
3. Попробуйте перезапустить сессию

### Проблема: Сообщения не отправляются
1. Проверьте статус сессии
2. Убедитесь, что номер телефона корректный
3. Проверьте логи в БД: таблица `whatsapp_messages_log`

### Проблема: Webhook не работает
1. Убедитесь, что URL доступен извне
2. Проверьте настройки webhook в WAHA
3. Проверьте логи обработки webhook

## Безопасность

⚠️ **Важно:**
- Ограничьте количество сообщений в день
- Получайте согласие пользователей
- Соблюдайте правила WhatsApp
- Используйте HTTPS для webhook

## Масштабирование

### Множественные магазины
Каждый магазин может иметь свою сессию WAHA:
- `kaspi-store-{store_id}`
- Отдельные настройки и шаблоны
- Независимая статистика

### Горизонтальное масштабирование
- Несколько экземпляров WAHA сервера
- Балансировка нагрузки
- Общая база данных сессий

## Резервное копирование

### Важные данные
- Настройки магазинов (`whatsapp_settings`)
- Шаблоны сообщений (`whatsapp_templates`)
- Сессии WAHA (`waha_sessions`)
- Логи сообщений (`whatsapp_messages_log`)

### Автоматическое резервное копирование
```bash
# Создайте скрипт резервного копирования
pg_dump -h localhost -U postgres -d kaspi_demper \
  --table=whatsapp_* --table=waha_sessions \
  > waha_backup_$(date +%Y%m%d).sql
```

## Обновление

### Обновление WAHA
```bash
# Остановите текущий контейнер
docker-compose -f docker-compose.waha.yml down

# Обновите образ
docker pull devlikeapro/waha:latest

# Запустите обновленную версию
docker-compose -f docker-compose.waha.yml up -d
```

### Обновление модуля
```bash
# Обновите код модуля
git pull origin main

# Перезапустите приложение
# (зависит от вашего процесса развертывания)
```

## Поддержка

При возникновении проблем:
1. Проверьте логи
2. Обратитесь к документации WAHA: https://waha.devlike.pro/
3. Создайте issue в репозитории проекта
4. Обратитесь к команде разработки
