-- Проверка производительности индексов после миграции
-- Запустите этот файл после применения 001_add_last_check_time.sql
-- для проверки, что индексы работают правильно

-- 1. Проверка основного индекса (rate limiting)
EXPLAIN ANALYZE
SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
FROM products
WHERE bot_active = TRUE
  AND (last_check_time IS NULL 
       OR last_check_time < NOW() - make_interval(secs => 30))
ORDER BY last_check_time ASC NULLS FIRST
LIMIT 500;

-- Ожидаемый результат: "Index Scan using idx_products_bot_active_last_check"
-- Если видите "Seq Scan" → индекс не используется, нужно переделать

-- 2. Проверка индекса для шардирования (INT ID)
EXPLAIN ANALYZE
SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
FROM products
WHERE bot_active = TRUE
  AND ((id::bigint % 5) + 5) % 5 = 0
  AND (last_check_time IS NULL 
       OR last_check_time < NOW() - make_interval(secs => 30))
ORDER BY last_check_time ASC NULLS FIRST
LIMIT 500;

-- Ожидаемый результат: "Index Scan using idx_products_shard_check" или комбинация индексов

-- 3. Проверка индекса для шардирования (UUID)
EXPLAIN ANALYZE
SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
FROM products
WHERE bot_active = TRUE
  AND mod(abs(hashtext(id::text)), 5) = 0
  AND (last_check_time IS NULL 
       OR last_check_time < NOW() - make_interval(secs => 30))
ORDER BY last_check_time ASC NULLS FIRST
LIMIT 500;

-- Ожидаемый результат: "Index Scan using idx_products_shard_uuid_check" или комбинация индексов

-- 4. Статистика по товарам
SELECT 
    COUNT(*) as total_products,
    COUNT(*) FILTER (WHERE bot_active = TRUE) as active_products,
    COUNT(*) FILTER (WHERE bot_active = TRUE AND last_check_time IS NULL) as never_checked,
    COUNT(*) FILTER (WHERE bot_active = TRUE AND last_check_time IS NOT NULL) as checked_at_least_once,
    COUNT(*) FILTER (WHERE bot_active = TRUE 
                     AND last_check_time IS NOT NULL 
                     AND last_check_time < NOW() - make_interval(secs => 30)) as ready_for_check
FROM products;

-- 5. Размер индексов
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_indexes
WHERE tablename = 'products'
  AND indexname LIKE '%last_check%'
ORDER BY pg_relation_size(indexname::regclass) DESC;

