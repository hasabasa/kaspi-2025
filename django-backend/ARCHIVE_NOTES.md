# Архив важных файлов из unified-backend

Перед удалением unified-backend, убедитесь что эти функции перенесены:

## Критичные функции (нужно перенести):

1. **api_parser.py** - содержит:
   - `get_products()` - получение товаров через API Kaspi
   - `sync_store_api()` - синхронизация магазина
   - `parse_product_by_sku()` - парсинг товара по SKU
   - `sync_product()` - обновление цены товара
   - `get_sells()` - статистика продаж
   - `fetch_preorders()` - получение предзаказов
   - `handle_upload_preorder()` - загрузка предзаказов
   - `generate_preorder_xlsx()` - экспорт в Excel
   - `sms_login_start()` - SMS авторизация (начало)
   - `sms_login_verify()` - SMS авторизация (проверка)

2. **proxy_balancer.py** - балансировка прокси (если используется)

3. **error_handlers.py** - обработка ошибок Playwright

4. **demper.py** / **demper_instance.py** - логика демпера цен

5. **routes/** - дополнительные эндпоинты:
   - `routes/products.py` - расширенные функции товаров
   - `routes/kaspi.py` - дополнительные функции Kaspi
   - `routes/admin.py` - админ функции

6. **migrations/** - SQL миграции (если нужны для справки)

## Можно удалить после переноса:

- `backend/` - старый бэкенд (Selenium)
- `newnew/` - дубликат старого бэкенда
- `unified-backend/` - после переноса всех функций

## Файлы для сохранения:

- `unified-backend/api_parser.py` - основная логика
- `unified-backend/proxy_balancer.py` - если используете прокси
- `unified-backend/error_handlers.py` - обработка ошибок
- `unified-backend/demper.py` - логика демпера

