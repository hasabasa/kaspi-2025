# План миграции на Django + PostgreSQL

## ✅ Что уже сделано

### 1. Структура проекта
- ✅ Создана базовая структура Django проекта
- ✅ Настроены settings.py с PostgreSQL
- ✅ Настроены URL маршруты
- ✅ Создан docker-compose.yml для PostgreSQL

### 2. Модели данных
- ✅ `KaspiStore` - магазины Kaspi
- ✅ `Product` - товары
- ✅ `Preorder` - предзаказы
- ✅ Все модели с правильными связями и индексами

### 3. API Endpoints
- ✅ REST API через Django REST Framework
- ✅ ViewSets для магазинов, товаров, предзаказов
- ✅ Health check endpoints
- ✅ Аутентификация Kaspi через Playwright

### 4. Аутентификация
- ✅ SessionManager адаптирован для Django
- ✅ Playwright логика перенесена
- ✅ Сохранение сессий в БД

## 📋 Что нужно доделать

### Приоритет 1: Критичные функции

#### 1. Синхронизация товаров
**Файл**: `api/services/sync_service.py` (создать)

```python
# Адаптировать из unified-backend/api_parser.py
# - get_products() - получение товаров через API Kaspi
# - insert_product_if_not_exists() - вставка/обновление товаров
# - sync_store_api() - полная синхронизация магазина
```

**Эндпоинт**: `POST /api/v1/kaspi/stores/{id}/sync/` (уже есть, нужно реализовать логику)

#### 2. Парсинг продуктов по SKU
**Файл**: `api/services/parser_service.py` (создать)

```python
# Адаптировать из unified-backend/api_parser.py
# - parse_product_by_sku() - парсинг товара по SKU
# - get_offers_by_product() - получение офферов
```

**Эндпоинт**: `POST /api/v1/kaspi/offers_by_product/` (создать)

#### 3. Обновление цен товаров
**Файл**: `api/services/sync_service.py`

```python
# Адаптировать из unified-backend/api_parser.py
# - sync_product() - обновление цены товара в Kaspi
```

**Эндпоинт**: `POST /api/v1/kaspi/update_product_price/` (создать)

### Приоритет 2: Важные функции

#### 4. Демпер цен (автоматическое снижение)
**Файл**: `api/management/commands/demper.py` (создать Django management command)

```python
# Адаптировать из unified-backend/main.py -> check_and_update_prices()
# Запуск через: python manage.py demper
# Или через Celery (рекомендуется)
```

#### 5. SMS-авторизация
**Файл**: `kaspi_auth/sms_auth_service.py` (создать)

```python
# Адаптировать из unified-backend/api_parser.py
# - sms_login_start() - начало SMS авторизации
# - sms_login_verify() - проверка SMS кода
```

**Эндпоинты**:
- `POST /api/v1/kaspi/auth/sms/start/`
- `POST /api/v1/kaspi/auth/sms/verify/`

#### 6. Предзаказы
**Файл**: `preorders/services.py` (создать)

```python
# Адаптировать из unified-backend/api_parser.py
# - fetch_preorders() - получение предзаказов
# - handle_upload_preorder() - загрузка предзаказов
# - generate_preorder_xlsx() - экспорт в Excel
```

### Приоритет 3: Дополнительные функции

#### 7. Анализ отзывов
**Файл**: `api/services/reviews_service.py` (создать)

```python
# Адаптировать из unified-backend/main.py
# - get_kaspi_reviews_all() - получение всех отзывов
# - analyze_reviews_mapped() - анализ отзывов
```

#### 8. Статистика продаж
**Файл**: `api/services/sales_service.py` (создать)

```python
# Адаптировать из unified-backend/api_parser.py
# - get_sells() - получение статистики продаж
```

#### 9. Proxy балансировка
**Файл**: `api/utils/proxy_balancer.py` (скопировать из unified-backend)

## 🔄 Процесс миграции

### Шаг 1: Настройка окружения

```bash
cd django-backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
playwright install chromium
```

### Шаг 2: Настройка базы данных

```bash
# Создать .env файл
cp .env.example .env

# Запустить PostgreSQL через Docker
docker-compose up -d db

# Или установить PostgreSQL локально и создать БД
createdb kaspi_demper
```

### Шаг 3: Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

### Шаг 4: Миграция данных (если есть)

Если нужно перенести данные из Supabase:

```python
# Создать management command: api/management/commands/migrate_from_supabase.py
# Использовать Supabase клиент для чтения данных
# Записать в Django модели
```

### Шаг 5: Тестирование

```bash
# Запустить сервер
python manage.py runserver

# Проверить health check
curl http://localhost:8010/health/

# Проверить БД
curl http://localhost:8010/health/db/
```

## 🔧 Адаптация async кода

Django использует синхронный код, поэтому async функции из FastAPI нужно оборачивать:

```python
# Было (FastAPI):
async def some_async_function():
    result = await async_operation()
    return result

# Стало (Django):
from kaspi_auth.kaspi_auth_service import run_async

def some_view(request):
    result = run_async(some_async_function())
    return Response(result)
```

Или использовать Django async views (Django 3.1+):

```python
from django.http import JsonResponse
import asyncio

async def some_async_view(request):
    result = await async_operation()
    return JsonResponse(result)
```

## 📦 Рекомендации по улучшению

### 1. Celery для фоновых задач

Для демпера и синхронизации лучше использовать Celery:

```python
# tasks.py
from celery import shared_task

@shared_task
def sync_store_task(store_id):
    # Логика синхронизации
    pass

@shared_task
def demper_task():
    # Логика демпера
    pass
```

### 2. Кэширование (Redis)

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Логирование

Настроено в `settings.py`, логи пишутся в `logs/django.log`

### 4. Production настройки

```python
# settings_production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 🐛 Известные проблемы и решения

### 1. JSONField в старых версиях Django

Если используется Django < 3.1, используйте `django.contrib.postgres.fields.JSONField`:

```python
from django.contrib.postgres.fields import JSONField

class KaspiStore(models.Model):
    guid = JSONField(null=True, blank=True)
```

### 2. UUID в URL

Django REST Framework автоматически обрабатывает UUID в URL, но нужно убедиться:

```python
# urls.py
router.register(r'kaspi/stores', KaspiStoreViewSet, basename='kaspi-stores')
# В ViewSet lookup_field = 'id' уже указан
```

### 3. CORS настройки

Для продакшена ограничьте CORS:

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
CORS_ALLOW_ALL_ORIGINS = False
```

## 📊 Сравнение производительности

| Операция | FastAPI (asyncpg) | Django (ORM) | Примечание |
|----------|------------------|--------------|------------|
| Простые запросы | ⚡⚡⚡ | ⚡⚡ | Django ORM немного медленнее |
| Сложные запросы | ⚡⚡⚡ | ⚡⚡⚡ | Django ORM оптимизирует запросы |
| Миграции | Ручные SQL | ⚡⚡⚡⚡ | Django миграции удобнее |
| Админ-панель | Нет | ⚡⚡⚡⚡⚡ | Встроенная админка Django |

## ✅ Чеклист миграции

- [x] Создать структуру Django проекта
- [x] Создать модели данных
- [x] Настроить PostgreSQL
- [x] Создать базовые API endpoints
- [x] Перенести аутентификацию Kaspi
- [ ] Перенести синхронизацию товаров
- [ ] Перенести парсинг продуктов
- [ ] Перенести демпер цен
- [ ] Перенести SMS-авторизацию
- [ ] Перенести предзаказы
- [ ] Настроить Celery (опционально)
- [ ] Настроить Redis (опционально)
- [ ] Production настройки
- [ ] Тестирование всех функций
- [ ] Документация API

## 🚀 Следующие шаги

1. **Протестировать базовую функциональность**:
   - Аутентификация Kaspi
   - CRUD операции для магазинов
   - Health checks

2. **Перенести критичные функции**:
   - Синхронизация товаров
   - Парсинг продуктов
   - Обновление цен

3. **Настроить фоновые задачи**:
   - Демпер цен (Celery или management command)
   - Периодическая синхронизация

4. **Оптимизация**:
   - Кэширование
   - Индексы БД
   - Оптимизация запросов

5. **Production deployment**:
   - Настройка production settings
   - Настройка Nginx/Gunicorn
   - Мониторинг и логирование

