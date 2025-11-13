# Kaspi Demper Backend Database Schema

Этот каталог содержит SQL схемы и миграции для базы данных Supabase, используемой в Kaspi Demper Backend.

## Файлы

### `database_schema.sql`
Основной файл схемы базы данных, содержащий:
- Создание таблиц (`kaspi_stores`, `products`, `preorders`)
- Индексы для оптимизации производительности
- Триггеры для автоматического обновления `updated_at`
- Политики безопасности RLS (Row Level Security)
- Представления для удобного доступа к данным

### `migrations.sql`
Файл с миграциями для обновления существующей базы данных:
- Дополнительные индексы
- Новые колонки и таблицы
- Функции для архивирования и очистки данных
- Мониторинг и аналитика

### `sample_queries.sql`
Примеры SQL запросов для:
- Тестирования функциональности
- Аналитики и отчетности
- Отладки и мониторинга
- Операций CRUD

## Установка

### 1. Создание базы данных в Supabase

1. Войдите в [Supabase Dashboard](https://supabase.com/dashboard)
2. Создайте новый проект или выберите существующий
3. Перейдите в раздел "SQL Editor"

### 2. Выполнение схемы

```sql
-- Выполните содержимое database_schema.sql
-- Это создаст все необходимые таблицы, индексы и политики
```

### 3. Настройка переменных окружения

Добавьте в ваш `.env` файл:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

## Структура таблиц

### kaspi_stores
Хранит информацию о магазинах Kaspi:
- `id` - UUID первичный ключ
- `user_id` - ID пользователя
- `merchant_id` - ID мерчанта в Kaspi
- `name` - Название магазина
- `api_key` - API ключ для Kaspi
- `products_count` - Количество продуктов
- `last_sync` - Время последней синхронизации
- `is_active` - Активность магазина

### products
Каталог продуктов из Kaspi:
- `id` - UUID первичный ключ
- `kaspi_product_id` - ID продукта в Kaspi
- `kaspi_sku` - SKU продукта
- `store_id` - Ссылка на магазин
- `price` - Цена в тиынах (1/100 тенге)
- `name` - Название продукта
- `category` - Категория
- `image_url` - URL изображения
- `bot_active` - Активность бота для продукта

### preorders
Предзаказы от клиентов:
- `id` - UUID первичный ключ
- `product_id` - Ссылка на продукт
- `store_id` - Ссылка на магазин
- `article` - Артикул
- `name` - Название
- `brand` - Бренд
- `status` - Статус (processing, completed, cancelled)
- `price` - Цена
- `warehouses` - JSON с информацией о складах
- `delivery_days` - Дни доставки

## Безопасность

База данных использует Row Level Security (RLS) для обеспечения безопасности:
- Пользователи могут видеть только свои магазины
- Доступ к продуктам и предзаказам ограничен магазинами пользователя
- Все операции требуют аутентификации через Supabase Auth

## Мониторинг

### Представления для мониторинга:
- `store_stats` - Статистика по магазинам
- `product_stats` - Статистика по продуктам
- `system_health` - Общее состояние системы

### Функции:
- `cleanup_old_data()` - Очистка старых данных
- `backup_store_data(store_uuid)` - Резервное копирование данных магазина
- `validate_store_data(store_uuid)` - Валидация данных магазина

## Тестирование

Используйте запросы из `sample_queries.sql` для тестирования:

```sql
-- Создание тестового магазина
INSERT INTO kaspi_stores (user_id, merchant_id, name, api_key)
VALUES ('test-user', 'test-merchant', 'Test Store', 'test-key');

-- Проверка статистики
SELECT * FROM store_stats;
```

## Производительность

### Индексы:
- По `user_id` для быстрого поиска магазинов пользователя
- По `store_id` для быстрого доступа к продуктам
- По `kaspi_product_id` для поиска продуктов
- Составные индексы для сложных запросов

### Рекомендации:
- Регулярно выполняйте `VACUUM` и `ANALYZE`
- Мониторьте размер таблиц и индексов
- Используйте пагинацию для больших результатов

## Резервное копирование

### Автоматическое резервное копирование:
Supabase автоматически создает резервные копии. Дополнительно можно использовать:

```sql
-- Экспорт данных магазина
SELECT backup_store_data('store-uuid-here');
```

### Ручное резервное копирование:
```bash
# Экспорт схемы
pg_dump -h db.your-project.supabase.co -U postgres -d postgres --schema-only > schema_backup.sql

# Экспорт данных
pg_dump -h db.your-project.supabase.co -U postgres -d postgres --data-only > data_backup.sql
```

## Обслуживание

### Еженедельные задачи:
```sql
-- Очистка старых данных
SELECT cleanup_old_data();

-- Обновление статистики
ANALYZE;
```

### Ежемесячные задачи:
```sql
-- Архивирование старых предзаказов
SELECT archive_old_preorders();

-- Проверка целостности данных
SELECT * FROM system_health;
```

## Устранение неполадок

### Частые проблемы:

1. **Ошибка подключения к базе данных**
   - Проверьте переменные окружения
   - Убедитесь, что проект Supabase активен

2. **Медленные запросы**
   - Проверьте наличие индексов
   - Используйте `EXPLAIN ANALYZE` для анализа запросов

3. **Ошибки RLS**
   - Убедитесь, что пользователь аутентифицирован
   - Проверьте политики безопасности

### Логи:
```sql
-- Просмотр активности
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Просмотр медленных запросов
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

## Поддержка

При возникновении проблем:
1. Проверьте логи Supabase Dashboard
2. Используйте запросы из `sample_queries.sql` для диагностики
3. Обратитесь к документации Supabase
4. Проверьте статус сервиса Supabase
