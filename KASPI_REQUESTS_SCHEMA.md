# 🌐 ПОЛНАЯ СХЕМА ЗАПРОСОВ KASPI ДЕМПЕРА

## 🔐 1. АВТОРИЗАЦИЯ KASPI

### Selenium Авторизация
```
URL: https://idmc.shop.kaspi.kz/login
Метод: Selenium WebDriver (автоматизация браузера)
Процесс:
1. Открыть Chrome в headless режиме
2. Перейти на https://idmc.shop.kaspi.kz/login
3. Ввести email в поле "username"
4. Нажать "Продолжить"
5. Ввести пароль в поле "password"
6. Нажать "Войти"
7. Получить cookies и токены
8. Сохранить в Supabase
```

### Playwright Авторизация
```
URL: https://idmc.shop.kaspi.kz/login
Метод: Playwright (альтернативный браузер)
Процесс: Аналогично Selenium, но через Playwright
```

## 📦 2. ПОЛУЧЕНИЕ ИНФОРМАЦИИ О МАГАЗИНЕ

### Список магазинов
```
URL: https://mc.shop.kaspi.kz/s/m
Метод: GET
Заголовки:
- x-auth-version: 3
- Origin: https://kaspi.kz
- Referer: https://kaspi.kz/
- User-Agent: Mozilla/5.0...
- Cookie: session_id=xxx; merchant_token=yyy
```

### Информация о конкретном магазине
```
URL: https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getMerchant
Метод: POST
Тело: GraphQL запрос с merchant_id
```

## 🛍️ 3. ПАРСИНГ ТОВАРОВ

### Список товаров магазина
```
URL: https://mc.shop.kaspi.kz/bff/offer-view/list?m={merchant_uid}&p={page}&l={page_size}&a=true
Метод: GET
Параметры:
- m: merchant_uid (ID магазина)
- p: page (номер страницы)
- l: page_size (размер страницы)
- a: true (все товары)
```

### Информация о конкретном товаре
```
URL: https://kaspi.kz/yml/offer-view/offers/{sku}
Метод: POST
Тело: JSON с параметрами поиска
Заголовки:
- Content-Type: application/json
- Origin: https://kaspi.kz
- Referer: https://kaspi.kz/shop/p/{sku}
- User-Agent: Mozilla/5.0...
```

## 💰 4. ОБНОВЛЕНИЕ ЦЕН (ДЕМПЕР)

### Загрузка прайс-листа
```
URL: https://mc.shop.kaspi.kz/pricefeed/upload/merchant/upload?merchantUid={merchant_uid}
Метод: POST (multipart/form-data)
Тело: CSV файл с ценами
```

### Обработка прайс-листа
```
URL: https://mc.shop.kaspi.kz/pricefeed/upload/merchant/process
Метод: POST
Тело: JSON с данными о загруженном файле
```

## 📊 5. ПОЛУЧЕНИЕ ЗАКАЗОВ

### Активные заказы (доставка)
```
URL: https://mc.shop.kaspi.kz/mc/api/orderTabs/active?count=100&selectedTabs=DELIVERY&startIndex=0&loadPoints=false&_m={merchant_id}
Метод: GET
```

### Активные заказы (самовывоз)
```
URL: https://mc.shop.kaspi.kz/mc/api/orderTabs/active?count=100&selectedTabs=PICKUP&startIndex=0&loadPoints=false&_m={merchant_id}
Метод: GET
```

## 🗄️ 6. SUPABASE ИНТЕГРАЦИЯ

### База данных
```
URL: https://your-project.supabase.co/rest/v1/
Метод: POST/GET/PUT/DELETE
Таблицы:
- kaspi_stores: магазины
- products: товары  
- sales: продажи
- demper_sessions: сессии демпера
- demper_logs: логи демпера
- proxy_configs: конфигурация прокси
- proxy_logs: логи прокси
```

## 🔄 7. ПРОКСИ СИСТЕМА

### Конфигурация прокси
```
Формат: proxy1:port1:user1:pass1,proxy2:port2:user2:pass2
Использование: Ротация прокси для избежания блокировок
```

## 📋 8. ЛОГИРОВАНИЕ

### Типы логов
- `🔐 [KASPI-AUTH]` - авторизация
- `📦 [SUPABASE]` - операции с БД
- `🔍 [PARSER]` - парсинг товаров
- `💰 [DEMPER]` - демпинг цен
- `🔄 [PROXY]` - использование прокси
- `❌ [ERROR]` - ошибки с traceback

### Где смотреть логи
1. **Консоль backend** - основные логи в реальном времени
2. **Файл logs/app.log** - файловое логирование (если настроено)
3. **Supabase logs** - логи базы данных
4. **Браузер консоль** - логи frontend

## 🚨 9. ЧАСТЫЕ ОШИБКИ

### 401 Unauthorized
- Проблема: Истекла сессия Kaspi
- Решение: Повторная авторизация

### 429 Too Many Requests  
- Проблема: Превышен лимит запросов
- Решение: Использование прокси, задержки

### 500 Internal Server Error
- Проблема: Ошибка в коде
- Решение: Проверить логи с traceback

## 🔧 10. НАСТРОЙКА

### Переменные окружения
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Прокси
PROXY_ENABLED=true
PROXY_LIST=proxy1:port1:user1:pass1

# Демпер
DEMPER_ENABLED=true
DEMPER_INTERVAL=300
DEMPER_MAX_CONCURRENT=10
```
