-- SQL Schema for Kaspi Demper Backend
-- Supabase Database Tables

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: kaspi_stores
-- Stores information about Kaspi stores/marketplaces
CREATE TABLE IF NOT EXISTS kaspi_stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id TEXT NOT NULL,
    merchant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    api_key TEXT DEFAULT 'auto_generated_token',
    products_count INTEGER DEFAULT 0,
    last_sync TEXT,
    is_active BOOLEAN DEFAULT true
);

-- Table: products
-- Stores product information from Kaspi
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kaspi_product_id TEXT NOT NULL,
    kaspi_sku TEXT,
    store_id UUID NOT NULL REFERENCES kaspi_stores(id) ON DELETE CASCADE,
    price INTEGER NOT NULL, -- Price in tiyin (1/100 of tenge)
    name TEXT NOT NULL,
    external_kaspi_id TEXT,
    category TEXT,
    image_url TEXT,
    bot_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: preorders
-- Stores preorder requests from customers
CREATE TABLE IF NOT EXISTS preorders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES kaspi_stores(id) ON DELETE CASCADE,
    article TEXT,
    name TEXT,
    brand TEXT,
    status TEXT DEFAULT 'processing',
    price INTEGER,
    warehouses JSONB, -- JSON array of warehouse information
    delivery_days INTEGER DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate preorders
    UNIQUE(product_id, store_id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_kaspi_stores_user_id ON kaspi_stores(user_id);
CREATE INDEX IF NOT EXISTS idx_kaspi_stores_merchant_id ON kaspi_stores(merchant_id);
CREATE INDEX IF NOT EXISTS idx_kaspi_stores_is_active ON kaspi_stores(is_active);

CREATE INDEX IF NOT EXISTS idx_products_store_id ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_kaspi_product_id ON products(kaspi_product_id);
CREATE INDEX IF NOT EXISTS idx_products_kaspi_sku ON products(kaspi_sku);
CREATE INDEX IF NOT EXISTS idx_products_bot_active ON products(bot_active);

CREATE INDEX IF NOT EXISTS idx_preorders_product_id ON preorders(product_id);
CREATE INDEX IF NOT EXISTS idx_preorders_store_id ON preorders(store_id);
CREATE INDEX IF NOT EXISTS idx_preorders_status ON preorders(status);
CREATE INDEX IF NOT EXISTS idx_preorders_created_at ON preorders(created_at);

-- Functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_kaspi_stores_updated_at 
    BEFORE UPDATE ON kaspi_stores 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_preorders_updated_at 
    BEFORE UPDATE ON preorders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) policies
ALTER TABLE kaspi_stores ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE preorders ENABLE ROW LEVEL SECURITY;

-- Policy for kaspi_stores - users can only access their own stores
CREATE POLICY "Users can access their own stores" ON kaspi_stores
    FOR ALL USING (auth.uid()::text = user_id);

-- Policy for products - users can only access products from their stores
CREATE POLICY "Users can access products from their stores" ON products
    FOR ALL USING (
        store_id IN (
            SELECT id FROM kaspi_stores WHERE user_id = auth.uid()::text
        )
    );

-- Policy for preorders - users can only access preorders from their stores
CREATE POLICY "Users can access preorders from their stores" ON preorders
    FOR ALL USING (
        store_id IN (
            SELECT id FROM kaspi_stores WHERE user_id = auth.uid()::text
        )
    );

-- Views for easier data access
CREATE OR REPLACE VIEW store_stats AS
SELECT 
    ks.id as store_id,
    ks.name as store_name,
    ks.user_id,
    ks.products_count,
    ks.last_sync,
    ks.is_active,
    COUNT(p.id) as actual_products_count,
    COUNT(po.id) as preorders_count
FROM kaspi_stores ks
LEFT JOIN products p ON ks.id = p.store_id
LEFT JOIN preorders po ON ks.id = po.store_id
GROUP BY ks.id, ks.name, ks.user_id, ks.products_count, ks.last_sync, ks.is_active;

-- View for product statistics
CREATE OR REPLACE VIEW product_stats AS
SELECT 
    p.id,
    p.name,
    p.price,
    p.category,
    p.bot_active,
    ks.name as store_name,
    ks.user_id,
    COUNT(po.id) as preorders_count
FROM products p
JOIN kaspi_stores ks ON p.store_id = ks.id
LEFT JOIN preorders po ON p.id = po.product_id
GROUP BY p.id, p.name, p.price, p.category, p.bot_active, ks.name, ks.user_id;

-- Sample data (optional - remove in production)
-- INSERT INTO kaspi_stores (user_id, merchant_id, name, api_key) 
-- VALUES ('sample-user-id', 'sample-merchant-id', 'Sample Store', 'sample-api-key');

-- Comments for documentation
COMMENT ON TABLE kaspi_stores IS 'Stores information about Kaspi stores/marketplaces connected by users';
COMMENT ON TABLE products IS 'Product catalog from Kaspi stores with pricing and metadata';
COMMENT ON TABLE preorders IS 'Customer preorder requests for products';

COMMENT ON COLUMN products.price IS 'Price in tiyin (1/100 of tenge) - multiply by 100 for display';
COMMENT ON COLUMN preorders.warehouses IS 'JSON array containing warehouse information and stock levels';
COMMENT ON COLUMN kaspi_stores.api_key IS 'API key for Kaspi marketplace integration';
COMMENT ON COLUMN kaspi_stores.merchant_id IS 'Kaspi merchant ID for API requests';
