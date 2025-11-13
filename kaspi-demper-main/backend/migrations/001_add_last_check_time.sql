-- Миграция: Добавление поля last_check_time для rate limiting
-- Дата: 2025-01-21
-- Описание: Добавляет поле для отслеживания времени последней проверки товара
--           + индексы для эффективного шардирования и rate limiting
--           КРИТИЧНО: После миграции инициализирует last_check_time для существующих товаров,
--           чтобы избежать проверки всех товаров в первом цикле (526 блокировка)

-- 1. Добавляем колонку last_check_time
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS last_check_time TIMESTAMP WITH TIME ZONE;

-- 2. Создаем основной индекс (last_check_time первым для оптимальной сортировки)
CREATE INDEX IF NOT EXISTS idx_products_bot_active_last_check 
ON products (last_check_time, bot_active) 
WHERE bot_active = TRUE;

-- 3. Создаем индекс для шардирования по ID (для INT ID)
-- Этот индекс ускорит запросы с условием ((id % INSTANCE_COUNT) + INSTANCE_COUNT) % INSTANCE_COUNT = INSTANCE_INDEX
-- Используется в demper_instance.py для распределения нагрузки между инстансами
-- ПРИМЕЧАНИЕ: Функциональный индекс с модулем может не работать на всех версиях PostgreSQL
-- Если получаете ошибку, можно создать обычный индекс на id и полагаться на основной индекс
-- CREATE INDEX IF NOT EXISTS idx_products_shard_check
-- ON products USING btree ((id::bigint % 5), last_check_time)
-- WHERE bot_active = TRUE;

-- 4. Создаем индекс для шардирования по UUID (если используется UUID)
-- Этот индекс использует hashtext для UUID, как в demper_instance.py
-- ПРИМЕЧАНИЕ: Функциональный индекс может быть проблематичным, используйте только если нужно
-- CREATE INDEX IF NOT EXISTS idx_products_shard_uuid_check
-- ON products USING btree ((hashtext(id::text)), last_check_time)
-- WHERE bot_active = TRUE;

-- Альтернатива: Создаем простой индекс на id для ускорения фильтрации
-- PostgreSQL может использовать его в комбинации с основным индексом
CREATE INDEX IF NOT EXISTS idx_products_id_bot_active
ON products (id)
WHERE bot_active = TRUE;

-- 5. Комментарий к колонке
COMMENT ON COLUMN products.last_check_time IS 
'Время последней проверки цены конкурентов. Используется для rate limiting и распределения нагрузки. NULL означает, что товар никогда не проверялся.';

-- 6. КРИТИЧНО: Инициализация last_check_time для существующих товаров
-- Распределяем проверки равномерно на период времени
-- Это предотвращает проверку всех 30000 товаров в первом цикле → избегаем 526 блокировки
-- 
-- Стратегия: Распределяем товары так, чтобы в каждый момент времени было готово к проверке
-- примерно BATCH_SIZE товаров, распределенных равномерно во времени
UPDATE products
SET last_check_time = NOW() - INTERVAL '1 day' + (
    row_number() OVER (ORDER BY id) * INTERVAL '10 seconds'
)
WHERE last_check_time IS NULL AND bot_active = TRUE;

-- 7. Анализируем таблицу для оптимизации запросов планировщика
ANALYZE products;

-- 8. Примечание: После применения миграции рекомендуется проверить производительность:
-- EXPLAIN ANALYZE
-- SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
-- FROM products
-- WHERE bot_active = TRUE
--   AND (last_check_time IS NULL 
--        OR last_check_time < NOW() - make_interval(secs => 30))
-- ORDER BY last_check_time ASC NULLS FIRST
-- LIMIT 500;
-- 
-- Результат должен показывать "Index Scan using idx_products_bot_active_last_check"
-- Если показывает "Seq Scan" → индекс не используется, нужно переделать.

