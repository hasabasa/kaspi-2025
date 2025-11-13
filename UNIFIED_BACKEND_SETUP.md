# Инструкции по настройке unified-backend

## Настройка переменных окружения

### 1. Backend (.env для unified-backend)

Создайте файл `/Users/hasen/demper-667-45/unified-backend/.env` со следующим содержимым:

```bash
# Основные настройки
DEBUG=true
APP_NAME=Unified Kaspi Demper Backend
VERSION=1.0.0

# База данных - используем Supabase
DB_MODE=supabase

# Supabase настройки (заполните реальными данными)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Авторизация
AUTH_METHOD=auto

# Прокси система (отключена для начала)
PROXY_ENABLED=false
PROXY_LIST=

# Демпер система
DEMPER_ENABLED=true
DEMPER_INTERVAL=300
DEMPER_MAX_CONCURRENT=10

# CORS настройки для разработки
CORS_ALLOWED_ORIGINS=^(https:\/\/([a-z0-9-]+\.)?(kaspi-price\.kz|mark-bot\.kz)|http:\/\/localhost(:\d+)?)$

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Kaspi API
KASPI_BASE_URL=https://mc.shop.kaspi.kz
KASPI_LOGIN_URL=https://idmc.shop.kaspi.kz/login

# Безопасность
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Шардинг
INSTANCE_INDEX=0
INSTANCE_COUNT=1
```

### 2. Frontend (.env для фронтенда)

Создайте файл `/Users/hasen/demper-667-45/.env` со следующим содержимым:

```bash
# API URL для unified-backend
VITE_API_URL=http://localhost:8010

# Дополнительные настройки
VITE_BACKEND_URL=http://localhost:8010
VITE_API_VERSION=v1

# Настройки для разработки
VITE_DEBUG=true
VITE_LOG_LEVEL=info
```

## Запуск системы

### 1. Запуск unified-backend

```bash
cd /Users/hasen/demper-667-45/unified-backend
python main.py
```

Backend будет доступен по адресу: http://localhost:8010

### 2. Запуск фронтенда

```bash
cd /Users/hasen/demper-667-45
npm run dev
```

Frontend будет доступен по адресу: http://localhost:5173

## Проверка интеграции

### 1. Health Check

Откройте в браузере: http://localhost:8010/health

Должен вернуться JSON с информацией о состоянии системы.

### 2. API Documentation

Откройте в браузере: http://localhost:8010/docs

Здесь доступна интерактивная документация API.

### 3. Проверка CORS

Убедитесь, что фронтенд может делать запросы к бэкенду без ошибок CORS.

## Основные изменения

1. **Backend**: Работает на порту 8010 с префиксом `/api/v1/`
2. **Frontend**: Обновлены все API вызовы для использования unified-backend
3. **Database**: Используется Supabase из существующей конфигурации
4. **Новые возможности**: Добавлены сервисы для демпера и прокси
5. **CORS**: Настроен в unified-backend для работы с localhost

## Новые API Endpoints

### Kaspi
- `POST /api/v1/kaspi/auth` - Авторизация магазина
- `GET /api/v1/kaspi/stores` - Получение списка магазинов
- `POST /api/v1/kaspi/stores/{id}/sync` - Синхронизация магазина

### Products
- `GET /api/v1/products` - Список товаров
- `POST /api/v1/products/bulk-update` - Массовое обновление
- `GET /api/v1/products/search` - Поиск товаров

### Sales
- `GET /api/v1/sales` - Данные о продажах
- `GET /api/v1/sales/bulk` - Массовая загрузка продаж

### Demper
- `POST /api/v1/demper/start` - Запуск демпера
- `GET /api/v1/demper/status/{storeId}` - Статус демпера
- `GET /api/v1/demper/statistics/{storeId}` - Статистика демпера

### Proxy
- `GET /api/v1/proxy/status` - Статус прокси системы
- `POST /api/v1/proxy/add` - Добавление прокси
- `GET /api/v1/proxy/test/{proxyId}` - Тестирование прокси
