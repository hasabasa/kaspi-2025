-- Sample Queries for Kaspi Demper Backend
-- Useful SQL queries for testing and debugging

-- 1. Basic Store Operations
-- Create a new store
INSERT INTO kaspi_stores (user_id, merchant_id, name, api_key, products_count, is_active)
VALUES ('test-user-123', 'merchant-456', 'Test Store', 'api-key-789', 0, true);

-- Get all stores for a user
SELECT * FROM kaspi_stores WHERE user_id = 'test-user-123';

-- Update store information
UPDATE kaspi_stores 
SET products_count = 5, last_sync = NOW()::text 
WHERE id = 'store-uuid-here';

-- 2. Product Operations
-- Add a product
INSERT INTO products (kaspi_product_id, kaspi_sku, store_id, price, name, category, image_url)
VALUES (
    'kaspi-product-123', 
    'SKU-456', 
    'store-uuid-here', 
    50000, -- 500.00 KZT in tiyin
    'Test Product', 
    'Electronics', 
    'https://example.com/image.jpg'
);

-- Get all products for a store
SELECT p.*, ks.name as store_name 
FROM products p 
JOIN kaspi_stores ks ON p.store_id = ks.id 
WHERE p.store_id = 'store-uuid-here';

-- Update product price
UPDATE products 
SET price = 45000, updated_at = NOW() 
WHERE kaspi_product_id = 'kaspi-product-123';

-- Get products by price range
SELECT * FROM products 
WHERE price BETWEEN 10000 AND 100000 
ORDER BY price DESC;

-- 3. Preorder Operations
-- Create a preorder
INSERT INTO preorders (product_id, store_id, article, name, brand, status, price, warehouses, delivery_days)
VALUES (
    'product-uuid-here',
    'store-uuid-here',
    'ART-123',
    'Preorder Product',
    'Brand Name',
    'processing',
    75000,
    '["warehouse1", "warehouse2"]'::jsonb,
    15
);

-- Get all preorders for a store
SELECT po.*, p.name as product_name, ks.name as store_name
FROM preorders po
JOIN products p ON po.product_id = p.id
JOIN kaspi_stores ks ON po.store_id = ks.id
WHERE po.store_id = 'store-uuid-here';

-- Update preorder status
UPDATE preorders 
SET status = 'completed', updated_at = NOW() 
WHERE id = 'preorder-uuid-here';

-- 4. Analytics and Statistics
-- Store statistics
SELECT 
    ks.name,
    COUNT(p.id) as total_products,
    COUNT(p.id) FILTER (WHERE p.bot_active = true) as active_products,
    COUNT(po.id) as total_preorders,
    COUNT(po.id) FILTER (WHERE po.status = 'processing') as pending_preorders,
    AVG(p.price) as avg_product_price
FROM kaspi_stores ks
LEFT JOIN products p ON ks.id = p.store_id
LEFT JOIN preorders po ON ks.id = po.store_id
GROUP BY ks.id, ks.name;

-- Top products by preorders
SELECT 
    p.name,
    p.price,
    p.category,
    COUNT(po.id) as preorder_count,
    SUM(po.price) as total_preorder_value
FROM products p
LEFT JOIN preorders po ON p.id = po.product_id
GROUP BY p.id, p.name, p.price, p.category
ORDER BY preorder_count DESC
LIMIT 10;

-- Revenue by store
SELECT 
    ks.name as store_name,
    COUNT(po.id) as total_preorders,
    SUM(po.price) as total_revenue,
    AVG(po.price) as avg_order_value
FROM kaspi_stores ks
LEFT JOIN preorders po ON ks.id = po.store_id
WHERE po.status IN ('completed', 'processing')
GROUP BY ks.id, ks.name
ORDER BY total_revenue DESC;

-- 5. Data Validation Queries
-- Find stores without products
SELECT ks.* FROM kaspi_stores ks
LEFT JOIN products p ON ks.id = p.store_id
WHERE p.id IS NULL AND ks.is_active = true;

-- Find products without valid prices
SELECT * FROM products 
WHERE price <= 0 OR price IS NULL;

-- Find preorders with missing information
SELECT * FROM preorders 
WHERE status IS NULL OR status = '';

-- 6. Performance Monitoring
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE tablename IN ('kaspi_stores', 'products', 'preorders')
ORDER BY tablename, attname;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename IN ('kaspi_stores', 'products', 'preorders')
ORDER BY idx_scan DESC;

-- 7. Data Cleanup Queries
-- Delete old completed preorders
DELETE FROM preorders 
WHERE status = 'completed' 
AND created_at < NOW() - INTERVAL '6 months';

-- Deactivate products without recent updates
UPDATE products 
SET bot_active = false 
WHERE updated_at < NOW() - INTERVAL '3 months' 
AND bot_active = true;

-- 8. Backup and Restore
-- Export store data as JSON
SELECT jsonb_build_object(
    'store', to_jsonb(ks.*),
    'products', (
        SELECT jsonb_agg(to_jsonb(p.*))
        FROM products p 
        WHERE p.store_id = ks.id
    ),
    'preorders', (
        SELECT jsonb_agg(to_jsonb(po.*))
        FROM preorders po 
        WHERE po.store_id = ks.id
    )
) as store_data
FROM kaspi_stores ks
WHERE ks.id = 'store-uuid-here';

-- 9. Search and Filter Operations
-- Search products by name
SELECT * FROM products 
WHERE name ILIKE '%search_term%'
ORDER BY name;

-- Filter products by category
SELECT * FROM products 
WHERE category = 'Electronics'
ORDER BY price DESC;

-- Get recent activity
SELECT 
    'product' as type,
    id,
    name,
    created_at
FROM products
WHERE created_at > NOW() - INTERVAL '7 days'
UNION ALL
SELECT 
    'preorder' as type,
    id::text,
    name,
    created_at
FROM preorders
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- 10. Data Integrity Checks
-- Check for orphaned records
SELECT 'orphaned_products' as issue, COUNT(*) as count
FROM products p
LEFT JOIN kaspi_stores ks ON p.store_id = ks.id
WHERE ks.id IS NULL
UNION ALL
SELECT 'orphaned_preorders' as issue, COUNT(*) as count
FROM preorders po
LEFT JOIN products p ON po.product_id = p.id
WHERE p.id IS NULL;

-- Check for duplicate products
SELECT kaspi_product_id, store_id, COUNT(*) as count
FROM products
GROUP BY kaspi_product_id, store_id
HAVING COUNT(*) > 1;

-- 11. User Activity Analysis
-- User activity summary
SELECT 
    user_id,
    COUNT(DISTINCT ks.id) as store_count,
    COUNT(DISTINCT p.id) as product_count,
    COUNT(DISTINCT po.id) as preorder_count,
    MAX(ks.updated_at) as last_activity
FROM kaspi_stores ks
LEFT JOIN products p ON ks.id = p.store_id
LEFT JOIN preorders po ON ks.id = po.store_id
GROUP BY user_id
ORDER BY last_activity DESC;

-- 12. System Health Check
-- Overall system statistics
SELECT 
    (SELECT COUNT(*) FROM kaspi_stores) as total_stores,
    (SELECT COUNT(*) FROM products) as total_products,
    (SELECT COUNT(*) FROM preorders) as total_preorders,
    (SELECT COUNT(*) FROM kaspi_stores WHERE is_active = true) as active_stores,
    (SELECT COUNT(*) FROM products WHERE bot_active = true) as active_products,
    (SELECT COUNT(*) FROM preorders WHERE status = 'processing') as pending_preorders;
