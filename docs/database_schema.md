# Структура базы данных проекта

## 📊 Обзор

Проект использует **Supabase** (PostgreSQL) для хранения данных. База данных состоит из нескольких групп таблиц:

1. **Основные таблицы Kaspi** (kaspi_stores, products, preorders)
2. **Таблицы WhatsApp** (whatsapp_sessions, whatsapp_messages, whatsapp_contacts)
3. **Таблицы пользователей и подписок** (subscriptions, user_roles)
4. **Таблицы реферальной системы** (referral_links, referral_clicks, referral_conversions)
5. **Таблицы партнеров и промокодов** (partners, promo_codes)

---

## 🏪 Основные таблицы Kaspi

### 1. `kaspi_stores`
Хранит информацию о магазинах Kaspi, подключенных пользователями.

```sql
CREATE TABLE kaspi_stores (
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
```

**Поля:**
- `id` - UUID первичный ключ
- `user_id` - ID пользователя (связь с auth.users)
- `merchant_id` - ID мерчанта в Kaspi
- `name` - Название магазина
- `api_key` - API ключ для Kaspi
- `products_count` - Количество товаров
- `last_sync` - Время последней синхронизации
- `is_active` - Активность магазина

**Индексы:**
- `idx_kaspi_stores_user_id` - по user_id
- `idx_kaspi_stores_merchant_id` - по merchant_id
- `idx_kaspi_stores_is_active` - по is_active

---

### 2. `products`
Каталог товаров из магазинов Kaspi.

```sql
CREATE TABLE products (
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
    last_check_time TIMESTAMP WITH TIME ZONE, -- Для rate limiting
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Поля:**
- `id` - UUID первичный ключ
- `kaspi_product_id` - ID продукта в Kaspi
- `kaspi_sku` - SKU продукта
- `store_id` - Ссылка на магазин (FK)
- `price` - Цена в тиынах (1/100 тенге)
- `name` - Название товара
- `external_kaspi_id` - Внешний ID в Kaspi
- `category` - Категория товара
- `image_url` - URL изображения
- `bot_active` - Активность бота для товара
- `last_check_time` - Время последней проверки цены (для rate limiting)

**Индексы:**
- `idx_products_store_id` - по store_id
- `idx_products_kaspi_product_id` - по kaspi_product_id
- `idx_products_kaspi_sku` - по kaspi_sku
- `idx_products_bot_active` - по bot_active
- `idx_products_bot_active_last_check` - композитный (last_check_time, bot_active) для оптимизации демпера

---

### 3. `preorders`
Предзаказы от клиентов.

```sql
CREATE TABLE preorders (
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
    UNIQUE(product_id, store_id)
);
```

**Поля:**
- `id` - UUID первичный ключ
- `product_id` - Ссылка на товар (FK)
- `store_id` - Ссылка на магазин (FK)
- `article` - Артикул
- `name` - Название
- `brand` - Бренд
- `status` - Статус (processing, completed, cancelled)
- `price` - Цена
- `warehouses` - JSONB с информацией о складах
- `delivery_days` - Дни доставки

**Индексы:**
- `idx_preorders_product_id` - по product_id
- `idx_preorders_store_id` - по store_id
- `idx_preorders_status` - по status
- `idx_preorders_created_at` - по created_at

---

## 📱 Таблицы WhatsApp

### 4. `whatsapp_sessions`
Сессии WhatsApp для пользователей.

```sql
CREATE TABLE whatsapp_sessions (
    id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL,
    session_name TEXT NOT NULL,
    qr_code TEXT,
    is_connected BOOLEAN NOT NULL DEFAULT false,
    last_activity TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Поля:**
- `id` - UUID первичный ключ
- `user_id` - Ссылка на пользователя (FK)
- `session_name` - Название сессии
- `qr_code` - QR код для подключения
- `is_connected` - Статус подключения
- `last_activity` - Время последней активности

---

### 5. `whatsapp_messages`
Сообщения WhatsApp.

```sql
CREATE TABLE whatsapp_messages (
    id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES whatsapp_sessions NOT NULL,
    contact_phone TEXT NOT NULL,
    contact_name TEXT,
    message_text TEXT,
    message_type TEXT NOT NULL DEFAULT 'text',
    is_outgoing BOOLEAN NOT NULL DEFAULT false,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    delivery_status TEXT DEFAULT 'sent',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Поля:**
- `id` - UUID первичный ключ
- `session_id` - Ссылка на сессию (FK)
- `contact_phone` - Номер телефона контакта
- `contact_name` - Имя контакта
- `message_text` - Текст сообщения
- `message_type` - Тип сообщения (text, image, etc.)
- `is_outgoing` - Исходящее/входящее
- `timestamp` - Время сообщения
- `delivery_status` - Статус доставки

---

### 6. `whatsapp_contacts`
Контакты WhatsApp.

```sql
CREATE TABLE whatsapp_contacts (
    id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES whatsapp_sessions NOT NULL,
    phone TEXT NOT NULL,
    name TEXT,
    profile_pic_url TEXT,
    last_seen TIMESTAMP WITH TIME ZONE,
    is_blocked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE(session_id, phone)
);
```

---

## 👤 Таблицы пользователей и подписок

### 7. `subscriptions`
Подписки пользователей.

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL,
    plan_type TEXT NOT NULL, -- 'free', 'basic', 'premium', 'enterprise'
    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'cancelled', 'expired'
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Поля:**
- `id` - UUID первичный ключ
- `user_id` - Ссылка на пользователя (FK)
- `plan_type` - Тип плана (free, basic, premium, enterprise)
- `status` - Статус подписки (active, cancelled, expired)
- `start_date` - Дата начала
- `end_date` - Дата окончания

---

### 8. `user_roles`
Роли пользователей.

```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user', -- 'user', 'admin', 'moderator'
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

---

## 🎁 Таблицы реферальной системы

### 9. `referral_links`
Реферальные ссылки.

```sql
CREATE TABLE referral_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL,
    referral_code TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

---

### 10. `referral_clicks`
Клики по реферальным ссылкам.

```sql
CREATE TABLE referral_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_link_id UUID REFERENCES referral_links NOT NULL,
    clicked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    ip_address TEXT,
    user_agent TEXT
);
```

---

### 11. `referral_conversions`
Конверсии рефералов (регистрации).

```sql
CREATE TABLE referral_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_link_id UUID REFERENCES referral_links NOT NULL,
    new_user_id UUID REFERENCES auth.users NOT NULL,
    conversion_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    reward_given BOOLEAN DEFAULT false
);
```

---

## 🤝 Таблицы партнеров

### 12. `partners`
Партнеры системы.

```sql
CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    contact_email TEXT,
    partnership_type TEXT, -- 'affiliate', 'reseller', 'integration'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

---

### 13. `promo_codes`
Промокоды.

```sql
CREATE TABLE promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    discount_percent INTEGER,
    discount_amount INTEGER,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE,
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

---

## 🔒 Безопасность (RLS - Row Level Security)

Все таблицы используют **Row Level Security (RLS)** для обеспечения безопасности:

- Пользователи могут видеть только свои данные
- Доступ к магазинам ограничен по `user_id`
- Доступ к товарам и предзаказам ограничен магазинами пользователя
- WhatsApp сессии доступны только владельцу

---

## 📈 Представления (Views)

### `store_stats`
Статистика по магазинам:
- Количество товаров
- Количество предзаказов
- Статус активности

### `product_stats`
Статистика по товарам:
- Количество предзаказов на товар
- Информация о магазине

---

## 🔧 Функции и триггеры

### Триггеры автоматического обновления `updated_at`:
- `update_kaspi_stores_updated_at`
- `update_products_updated_at`
- `update_preorders_updated_at`

### Функция обновления времени:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

---

## 📝 Миграции

### Основные миграции:
1. `001_add_last_check_time.sql` - Добавление поля `last_check_time` для rate limiting
2. `002_check_index_performance.sql` - Проверка производительности индексов
3. `003_maintenance_vacuum.sql` - Обслуживание БД

### Supabase миграции:
- 32 миграции в папке `supabase/migrations/`
- Создание таблиц WhatsApp, подписок, рефералов, партнеров

---

## 📊 Статистика таблиц

| Таблица | Назначение | Связи |
|---------|-----------|-------|
| `kaspi_stores` | Магазины Kaspi | → `products`, `preorders` |
| `products` | Товары | → `kaspi_stores`, `preorders` |
| `preorders` | Предзаказы | → `products`, `kaspi_stores` |
| `whatsapp_sessions` | Сессии WhatsApp | → `whatsapp_messages`, `whatsapp_contacts` |
| `whatsapp_messages` | Сообщения | → `whatsapp_sessions` |
| `whatsapp_contacts` | Контакты | → `whatsapp_sessions` |
| `subscriptions` | Подписки | → `auth.users` |
| `user_roles` | Роли | → `auth.users` |
| `referral_links` | Реферальные ссылки | → `auth.users`, `referral_clicks`, `referral_conversions` |
| `referral_clicks` | Клики | → `referral_links` |
| `referral_conversions` | Конверсии | → `referral_links`, `auth.users` |
| `partners` | Партнеры | - |
| `promo_codes` | Промокоды | - |

---

**Дата создания:** 2025-12-09
**Версия БД:** 1.0


