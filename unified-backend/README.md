# Unified Backend

Полная копия kaspi-demper-main с адаптацией для наших данных.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Скопируйте `env.example` в `.env` и настройте переменные окружения:
```bash
cp env.example .env
```

3. Настройте переменные в `.env`:
```env
# Database Configuration
DB_MODE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Authentication
AUTH_METHOD=playwright

# CORS Configuration
CORS_ALLOWED_ORIGINS=^(http:\/\/localhost(:\d+)?|http:\/\/127\.0\.0\.1(:\d+)?)$
```

## Запуск

```bash
python main.py
```

Или с uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

## API Endpoints

- `/health` - Проверка состояния сервиса
- `/api/v1/kaspi/auth` - Аутентификация в Kaspi
- `/api/v1/kaspi/stores` - Получение списка магазинов
- `/api/v1/kaspi/stores/{store_id}/sync` - Синхронизация магазина
- `/api/v1/products/` - Работа с товарами
- `/api/v1/admin/` - Административные функции

## Особенности

- Использует Playwright для аутентификации в Kaspi
- Поддерживает Supabase и PostgreSQL
- Включает демпер цен, предзаказы, продажи
- SMS авторизация
- CORS настроен для локальной разработки

