# README.md
# WAHA Интеграция для Kaspi Demper

Автоматическая отправка WhatsApp уведомлений о заказах через WAHA API.

## Описание

Этот модуль интегрирует систему Kaspi Demper с WAHA (WhatsApp API) для автоматической отправки уведомлений покупателям о статусе их заказов.

## Возможности

- ✅ **Автоматическая отправка уведомлений** о новых заказах
- ✅ **Кастомные шаблоны сообщений** с переменными
- ✅ **Подключение через связанные устройства** (без QR-кода)
- ✅ **Webhook для входящих сообщений** и статусов доставки
- ✅ **Логирование всех сообщений** и статистика
- ✅ **REST API** для управления шаблонами и настройками
- ✅ **Масштабируемость** - поддержка множественных магазинов

## Архитектура

```
Kaspi API → api_parser.py → WAHA Module → WAHA Server → WhatsApp → Покупатель
```

## Компоненты

### Основные модули:
- `waha_client.py` - Клиент для работы с WAHA API
- `template_manager.py` - Управление шаблонами сообщений
- `message_sender.py` - Отправка сообщений
- `order_integration.py` - Интеграция с заказами Kaspi
- `database.py` - Работа с базой данных
- `routes.py` - API эндпоинты

### Модели данных:
- `models.py` - Pydantic модели для валидации

## Установка и настройка

### 1. Запуск WAHA сервера

```bash
# Запуск через Docker Compose
cd waha/
docker-compose -f docker-compose.waha.yml up -d

# Или запуск напрямую
docker run -it -p 3000:3000 devlikeapro/waha
```

### 2. Интеграция с основным приложением

Добавьте в `main.py`:

```python
from waha.waha_integration import initialize_waha, get_waha_router, shutdown_waha

# Инициализация WAHA
@app.on_event("startup")
async def startup_event():
    # ... существующий код ...
    
    # Инициализация WAHA
    await initialize_waha(pool, "http://localhost:3000")

# Добавление роутов WAHA
app.include_router(get_waha_router())

# Завершение работы
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
    
    # Обработка заказов для WhatsApp уведомлений
    try:
        waha_manager = get_waha_manager()
        await waha_manager.process_orders_for_store(
            shop_id, 
            result.get('orders', []), 
            session_manager.shop_name or "Магазин"
        )
    except Exception as e:
        logger.error(f"Ошибка обработки заказов WAHA: {e}")
    
    return True, result
```

## Использование

### 1. Настройка магазина

```bash
# Создание настроек WAHA для магазина
POST /waha/settings/{store_id}
{
    "waha_server_url": "http://localhost:3000",
    "waha_session_name": "kaspi-session",
    "is_enabled": true,
    "webhook_url": "http://your-server.com/waha/webhook"
}
```

### 2. Подключение WhatsApp

```bash
# Создание сессии для магазина
POST /waha/sessions/connect/{store_id}
{
    "webhook_url": "http://your-server.com/waha/webhook"
}
```

После создания сессии:
1. Откройте WhatsApp на телефоне
2. Перейдите в Настройки → Связанные устройства
3. Нажмите "Связать устройство"
4. Отсканируйте QR-код или используйте код подключения

### 3. Создание шаблона сообщения

```bash
POST /waha/templates/{store_id}
{
    "template_name": "Уведомление о заказе",
    "template_text": "Здравствуйте, {user_name}!\nВаш заказ Nº {order_num} \"{product_name}\", количество: {item_qty} шт готов к самовывозу.\n* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.\n* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.\nС уважением,\n{shop_name}"
}
```

### 4. Тестирование

```bash
# Отправка тестового сообщения
POST /waha/send-test/{store_id}
{
    "phone_number": "+7XXXXXXXXXX",
    "template_text": "Тестовое сообщение",
    "sample_data": {
        "user_name": "Тест",
        "order_num": "12345",
        "product_name": "Тестовый товар",
        "item_qty": "1",
        "shop_name": "Тестовый магазин"
    }
}
```

## API Эндпоинты

### Управление сессиями:
- `POST /waha/sessions/connect/{store_id}` - Подключение сессии
- `GET /waha/sessions/status/{store_id}` - Статус сессии
- `POST /waha/sessions/restart/{store_id}` - Перезапуск сессии
- `POST /waha/sessions/stop/{store_id}` - Остановка сессии

### Управление шаблонами:
- `POST /waha/templates/{store_id}` - Создание шаблона
- `GET /waha/templates/{store_id}` - Список шаблонов
- `GET /waha/templates/template/{template_id}` - Получение шаблона
- `PUT /waha/templates/{template_id}` - Обновление шаблона
- `DELETE /waha/templates/{template_id}` - Удаление шаблона
- `POST /waha/templates/preview` - Предварительный просмотр

### Настройки:
- `POST /waha/settings/{store_id}` - Создание/обновление настроек
- `GET /waha/settings/{store_id}` - Получение настроек

### Отправка сообщений:
- `POST /waha/send-test/{store_id}` - Тестовое сообщение
- `POST /waha/check-phone/{store_id}` - Проверка номера телефона

### Статистика и логи:
- `GET /waha/statistics/{store_id}` - Статистика сообщений
- `GET /waha/logs/{store_id}` - Логи сообщений

### Webhook:
- `POST /waha/webhook` - Обработка webhook событий

### Интеграция с заказами:
- `POST /waha/process-orders/{store_id}` - Обработка заказов

## Переменные шаблонов

Доступные переменные для подстановки в шаблоны:

- `{user_name}` - Имя покупателя
- `{order_num}` - Номер заказа
- `{product_name}` - Название товара
- `{item_qty}` - Количество товара
- `{shop_name}` - Название магазина
- `{delivery_type}` - Тип доставки
- `{order_date}` - Дата заказа
- `{total_amount}` - Общая сумма заказа
- `{customer_phone}` - Телефон покупателя

## База данных

Модуль создает следующие таблицы:

- `whatsapp_templates` - Шаблоны сообщений
- `whatsapp_settings` - Настройки WAHA
- `whatsapp_messages_log` - Логи отправленных сообщений
- `waha_sessions` - Информация о сессиях

## Безопасность

⚠️ **Важные моменты:**

1. **WhatsApp не разрешает ботов** - используйте осторожно
2. **Ограничьте количество сообщений** в день
3. **Получайте согласие** пользователей на получение сообщений
4. **Соблюдайте правила** WhatsApp по спаму
5. **Используйте webhook** для отслеживания статусов доставки

## Мониторинг

### Проверка состояния:
```bash
GET /waha/health
```

### Логи:
- Все отправленные сообщения логируются в БД
- Статусы доставки обновляются через webhook
- Ошибки отправки сохраняются с описанием

### Статистика:
- Количество отправленных сообщений
- Процент успешной доставки
- Статистика по дням
- Топ получателей

## Troubleshooting

### Проблемы с подключением:
1. Проверьте доступность WAHA сервера: `http://localhost:3000`
2. Убедитесь, что сессия подключена: `GET /waha/sessions/status/{store_id}`
3. Проверьте логи WAHA контейнера: `docker logs kaspi-waha`

### Проблемы с отправкой:
1. Проверьте статус сессии
2. Убедитесь, что номер телефона корректный
3. Проверьте логи в таблице `whatsapp_messages_log`

### Проблемы с webhook:
1. Убедитесь, что webhook URL доступен извне
2. Проверьте настройки webhook в WAHA
3. Проверьте логи обработки webhook событий

## Разработка

### Структура проекта:
```
waha/
├── __init__.py
├── waha_client.py
├── template_manager.py
├── message_sender.py
├── order_integration.py
├── database.py
├── models.py
├── routes.py
├── waha_integration.py
├── docker-compose.waha.yml
└── README.md
```

### Тестирование:
```bash
# Запуск тестов
python -m pytest tests/

# Тестирование API
curl -X GET http://localhost:8000/waha/health
```

## Лицензия

Этот модуль является частью проекта Kaspi Demper и распространяется под той же лицензией.

## Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Проверьте статус WAHA сервера
3. Обратитесь к документации WAHA: https://waha.devlike.pro/
4. Создайте issue в репозитории проекта
