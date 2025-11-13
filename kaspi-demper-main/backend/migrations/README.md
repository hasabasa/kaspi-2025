# Миграции базы данных

## Порядок применения миграций

### 1. Основная миграция (обязательно)
```bash
psql -U your_user -d your_database -f migrations/001_add_last_check_time.sql
```

**Что делает:**
- Добавляет колонку `last_check_time` для rate limiting
- Создает индексы для оптимизации запросов
- **КРИТИЧНО:** Инициализирует `last_check_time` для существующих товаров, распределяя проверки во времени

**⚠️ ВАЖНО:** После применения миграции НЕ запускайте демпер сразу! 
Сначала убедитесь, что инициализация прошла успешно:

```sql
-- Проверка инициализации
SELECT 
    COUNT(*) FILTER (WHERE last_check_time IS NULL) as never_checked,
    COUNT(*) FILTER (WHERE last_check_time IS NOT NULL) as initialized
FROM products 
WHERE bot_active = TRUE;
```

Если `never_checked` > 0, выполните дополнительную инициализацию через Python скрипт.

### 2. Проверка производительности (рекомендуется)
```bash
psql -U your_user -d your_database -f migrations/002_check_index_performance.sql
```

**Что делает:**
- Проверяет, используются ли индексы правильно
- Показывает статистику по товарам
- Отображает размер индексов

**Ожидаемый результат:**
- `EXPLAIN ANALYZE` должен показывать "Index Scan using idx_products_bot_active_last_check"
- Если показывает "Seq Scan" → индекс не используется, нужно переделать

### 3. Обслуживание индексов (рекомендуется ежедневно через cronjob)
```bash
# Вручную:
psql -U your_user -d your_database -f migrations/003_maintenance_vacuum.sql

# Или через скрипт:
./scripts/maintenance_cronjob.sh
```

**Что делает:**
- Переиндексирует таблицы для устранения фрагментации
- Обновляет статистику для планировщика запросов
- Проверяет размер индексов

**Настройка cronjob:**
```bash
# Добавить в crontab (каждый день в 3:00)
0 3 * * * /path/to/scripts/maintenance_cronjob.sh >> /var/log/demper_maintenance.log 2>&1
```

## Дополнительная инициализация

Если после миграции остались товары с `last_check_time = NULL`, используйте Python скрипт:

```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend
python3 scripts/initialize_last_check_time.py
```

**Что делает:**
- Распределяет проверки товаров на весь день (батчами)
- Безопасно работает с большим количеством товаров
- Показывает прогресс инициализации

## Устранение неполадок

### Проблема: Индекс не используется (Seq Scan)

**Решение:**
1. Проверьте, что индекс создан:
   ```sql
   SELECT indexname FROM pg_indexes WHERE tablename = 'products' AND indexname LIKE '%last_check%';
   ```

2. Обновите статистику:
   ```sql
   ANALYZE products;
   ```

3. Переиндексируйте:
   ```sql
   REINDEX INDEX idx_products_bot_active_last_check;
   ```

### Проблема: Слишком много товаров с NULL last_check_time

**Решение:**
1. Выполните дополнительную инициализацию через Python скрипт
2. Или вручную через SQL (для больших объемов):
   ```sql
   UPDATE products
   SET last_check_time = NOW() - INTERVAL '1 day' + (row_number() OVER (ORDER BY id) * INTERVAL '10 seconds')
   WHERE last_check_time IS NULL AND bot_active = TRUE
   LIMIT 10000;  -- Батчами по 10000
   ```

### Проблема: Ошибка при создании функционального индекса

**Решение:**
Некоторые версии PostgreSQL могут не поддерживать функциональные индексы с модулем.
В этом случае используйте альтернативный индекс (уже включен в миграцию):
```sql
CREATE INDEX IF NOT EXISTS idx_products_id_bot_active
ON products (id)
WHERE bot_active = TRUE;
```

PostgreSQL сможет использовать его в комбинации с основным индексом.

## Откат миграции (если нужно)

```sql
-- Удалить индексы
DROP INDEX IF EXISTS idx_products_bot_active_last_check;
DROP INDEX IF EXISTS idx_products_id_bot_active;

-- Удалить колонку
ALTER TABLE products DROP COLUMN IF EXISTS last_check_time;
```

**⚠️ ВНИМАНИЕ:** Откат удалит все данные о времени последней проверки!

