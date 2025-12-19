-- Периодическое обслуживание индексов (запускать раз в день через cronjob)
-- Рекомендуется запускать в 3:00 ночи (когда нагрузка минимальна)

-- 1. Переиндексирование для устранения фрагментации
REINDEX INDEX CONCURRENTLY idx_products_bot_active_last_check;
REINDEX INDEX CONCURRENTLY idx_products_shard_check;
REINDEX INDEX CONCURRENTLY idx_products_shard_uuid_check;

-- 2. Обновление статистики для планировщика запросов
ANALYZE products;

-- 3. VACUUM для освобождения места (если используется DELETE)
-- VACUUM ANALYZE products;

-- 4. Опционально: Удаление старых неактивных товаров (старше 90 дней)
-- DELETE FROM products 
-- WHERE bot_active = FALSE
--   AND last_check_time IS NOT NULL
--   AND last_check_time < NOW() - INTERVAL '90 days';

-- 5. Проверка фрагментации индексов
-- Если размер индекса сильно больше размера таблицы → нужен REINDEX
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_indexes
WHERE tablename = 'products'
  AND indexname LIKE '%last_check%'
ORDER BY pg_relation_size(indexname::regclass) DESC;

