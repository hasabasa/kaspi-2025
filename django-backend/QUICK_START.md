# 🚀 Быстрый старт Django Backend

## Установка и запуск

### Вариант 1: С Docker Compose (рекомендуется)

```bash
cd django-backend

# Создать .env файл
cp .env.example .env
# Отредактировать .env при необходимости

# Запустить все сервисы
docker-compose up -d

# Проверить логи
docker-compose logs -f django

# Остановить
docker-compose down
```

### Вариант 2: Локальная установка

```bash
cd django-backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Установить Playwright браузер
playwright install chromium

# Настроить .env
cp .env.example .env
# Отредактировать .env:
# - POSTGRES_HOST=localhost
# - POSTGRES_PASSWORD=your_password

# Создать базу данных PostgreSQL
createdb kaspi_demper  # или через pgAdmin

# Выполнить миграции
python manage.py migrate

# Создать суперпользователя (опционально)
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

## Проверка работы

```bash
# Health check
curl http://localhost:8010/health/

# Проверка БД
curl http://localhost:8010/health/db/

# Список магазинов (требует user_id)
curl "http://localhost:8010/api/v1/kaspi/stores/?user_id=your-user-id"
```

## Админ-панель

Откройте в браузере: http://localhost:8010/admin/

Войдите с учетными данными суперпользователя.

## Основные команды

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Django shell
python manage.py shell

# Собрать статику
python manage.py collectstatic

# Проверить настройки
python manage.py check
```

## Структура API

### Аутентификация Kaspi
```
POST /api/v1/kaspi/auth/authenticate/
Body: {
    "user_id": "uuid",
    "email": "email@example.com",
    "password": "password"
}
```

### Магазины
```
GET    /api/v1/kaspi/stores/?user_id=<uuid>
POST   /api/v1/kaspi/stores/
GET    /api/v1/kaspi/stores/{id}/
POST   /api/v1/kaspi/stores/{id}/sync/
DELETE /api/v1/kaspi/stores/{id}/
```

### Товары
```
GET    /api/v1/products/
POST   /api/v1/products/
GET    /api/v1/products/{id}/
POST   /api/v1/products/batch_enable/
POST   /api/v1/products/batch_disable/
```

### Предзаказы
```
GET    /api/v1/preorders/?store_id=<uuid>
POST   /api/v1/preorders/
GET    /api/v1/preorders/{id}/
```

## Troubleshooting

### Ошибка подключения к БД
```bash
# Проверить, что PostgreSQL запущен
pg_isready

# Проверить настройки в .env
# POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
```

### Ошибка Playwright
```bash
# Переустановить браузер
playwright install chromium
playwright install-deps chromium
```

### Ошибки миграций
```bash
# Сбросить миграции (ОСТОРОЖНО: удалит данные!)
python manage.py migrate api zero
python manage.py migrate
```

## Следующие шаги

1. Протестировать аутентификацию Kaspi
2. Перенести логику синхронизации товаров
3. Настроить фоновые задачи (Celery)
4. Настроить production окружение

См. подробный план в `docs/django_migration_plan.md`

