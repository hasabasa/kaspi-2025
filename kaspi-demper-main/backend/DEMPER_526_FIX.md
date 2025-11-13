# Исправление проблемы 526 - Rate Limiting для демпера

## Проблема

При включении бота у нескольких пользователей одновременно возникала блокировка 526 от Kaspi API из-за:
- Обработки всех товаров одновременно (до 30000 товаров)
- Слишком частых циклов (каждые 5 секунд)
- Слишком большого количества параллельных запросов (100 одновременно)
- Отсутствия распределения нагрузки во времени

## Решение

Реализованы следующие изменения:

### 1. SQL Миграция

Добавлено поле `last_check_time` в таблицу `products` для отслеживания времени последней проверки.

**Применить миграцию:**
```bash
psql -U your_user -d your_database -f migrations/001_add_last_check_time.sql
```

Или через psql:
```sql
ALTER TABLE products ADD COLUMN IF NOT EXISTS last_check_time TIMESTAMP WITH TIME ZONE;
CREATE INDEX IF NOT EXISTS idx_products_bot_active_last_check 
ON products (bot_active, last_check_time) WHERE bot_active = TRUE;
```

### 2. Rate Limiting на уровне БД

Теперь запросы выбирают только товары, которые:
- Не проверялись (`last_check_time IS NULL`)
- Или проверялись более `CHECK_INTERVAL_SECONDS` секунд назад
- Ограничены `LIMIT BATCH_SIZE` товаров за цикл

### 3. Настраиваемые параметры

Все параметры теперь настраиваются через переменные окружения:

```bash
# Количество параллельных запросов (по умолчанию 15 вместо 100)
MAX_CONCURRENT_TASKS=15

# Интервал между циклами в секундах (по умолчанию 30 вместо 5)
DEMPER_INTERVAL=30

# Минимальный интервал между проверками товара в секундах
CHECK_INTERVAL_SECONDS=30

# Максимум товаров за цикл на инстанс
BATCH_SIZE=500

# Задержка между обработкой товаров
MIN_PRODUCT_DELAY=0.3
MAX_PRODUCT_DELAY=0.8
```

### 4. Шардирование

Для распределения нагрузки можно запустить несколько инстансов демпера:

```bash
# Запуск 5 инстансов через скрипт
./start_dempers.sh
```

Или вручную:
```bash
INSTANCE_INDEX=0 INSTANCE_COUNT=5 MAX_CONCURRENT_TASKS=15 python3 demper_instance.py &
INSTANCE_INDEX=1 INSTANCE_COUNT=5 MAX_CONCURRENT_TASKS=15 python3 demper_instance.py &
# ... и так далее
```

## ⚠️ КРИТИЧНО: Инициализация после миграции

**ВНИМАНИЕ:** После применения миграции все товары будут иметь `last_check_time = NULL`. 
Если запустить демпер сразу, он попытается проверить ВСЕ товары в первом цикле → блокировка 526!

**Обязательно выполните инициализацию:**

### Способ 1: Автоматическая инициализация (в миграции)
Миграция `001_add_last_check_time.sql` уже включает инициализацию, которая распределяет проверки на весь день.

### Способ 2: Ручная инициализация через Python скрипт
```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend
python3 scripts/initialize_last_check_time.py
```

Этот скрипт:
- Распределяет проверки товаров на весь день
- Предотвращает проверку всех товаров одновременно
- Безопасно работает с большим количеством товаров (батчами)

### Способ 3: Проверка перед запуском
```sql
-- Проверьте, сколько товаров готово к проверке
SELECT COUNT(*) 
FROM products 
WHERE bot_active = TRUE
  AND last_check_time IS NOT NULL
  AND last_check_time < NOW() - make_interval(secs => 30);
```

Если результат > 1000 → выполните инициализацию перед запуском демпера!

## Использование

### Вариант 1: Один инстанс (для небольшой нагрузки)

```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend

# Настройка параметров через переменные окружения
export MAX_CONCURRENT_TASKS=15
export DEMPER_INTERVAL=30
export CHECK_INTERVAL_SECONDS=30
export BATCH_SIZE=500

# Запуск
python3 demper.py
```

### Вариант 2: Несколько инстансов (рекомендуется для большой нагрузки)

```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend

# Настройка параметров
export INSTANCE_COUNT=5
export MAX_CONCURRENT_TASKS=15
export DEMPER_INTERVAL=30
export CHECK_INTERVAL_SECONDS=30
export BATCH_SIZE=500

# Запуск всех инстансов
./start_dempers.sh
```

### Вариант 3: Docker Compose

```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend

# Настройка в docker-compose.yml
# Запуск
docker-compose up -d
```

## Мониторинг

### Просмотр логов

```bash
# Все инстансы
tail -f logs/demper_*.log

# Конкретный инстанс
tail -f logs/demper_0.log

# Поиск ошибок
grep -i error logs/demper_*.log
```

### Проверка статуса

```bash
# Проверка запущенных процессов
ps aux | grep demper_instance.py

# Остановка всех инстансов
pkill -f "python3 demper_instance.py"
```

## Ожидаемые результаты

### До исправления:
- 30000 товаров каждые 5 секунд
- 100 параллельных запросов
- 6000 запросов/сек → блокировка 526

### После исправления:
- 500 товаров на инстанс × 5 инстансов = 2500 товаров за цикл
- 15 параллельных запросов × 5 инстансов = ~75 запросов/сек
- Интервал 30 секунд → равномерное распределение нагрузки
- ✅ Никаких блокировок

## Настройка под нагрузку

### Маленькая нагрузка (< 1000 товаров):
```bash
INSTANCE_COUNT=1
MAX_CONCURRENT_TASKS=10
BATCH_SIZE=200
DEMPER_INTERVAL=30
```

### Средняя нагрузка (1000-10000 товаров):
```bash
INSTANCE_COUNT=3
MAX_CONCURRENT_TASKS=15
BATCH_SIZE=500
DEMPER_INTERVAL=30
```

### Большая нагрузка (> 10000 товаров):
```bash
INSTANCE_COUNT=5
MAX_CONCURRENT_TASKS=15
BATCH_SIZE=500
DEMPER_INTERVAL=30
```

При необходимости можно увеличить `INSTANCE_COUNT` до 10 и более.

## Важные замечания

1. **Всегда обновляется `last_check_time`** - даже при ошибке, чтобы не перепроверять товар в ближайший цикл
2. **Товары сортируются по `last_check_time ASC NULLS FIRST`** - сначала проверяются те, которые давно не проверялись
3. **Ограничение `LIMIT BATCH_SIZE`** - предотвращает обработку всех товаров сразу
4. **Задержки между товарами** - распределяют нагрузку во времени

## Troubleshooting

### Проблема: Все еще получаю ошибку 526

**Решение:**
1. Уменьшите `MAX_CONCURRENT_TASKS` до 10
2. Увеличьте `DEMPER_INTERVAL` до 60 секунд
3. Увеличьте `MIN_PRODUCT_DELAY` и `MAX_PRODUCT_DELAY` до 0.5-1.0
4. Уменьшите `BATCH_SIZE` до 200

### Проблема: Товары проверяются слишком медленно

**Решение:**
1. Увеличьте `INSTANCE_COUNT` до 10
2. Увеличьте `MAX_CONCURRENT_TASKS` до 20 (осторожно!)
3. Уменьшите `DEMPER_INTERVAL` до 20 секунд

### Проблема: Миграция не применяется

**Решение:**
Проверьте права доступа к БД и что колонка `last_check_time` действительно создана:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'products' AND column_name = 'last_check_time';
```

## Дополнительная информация

- См. `demper.py` и `demper_instance.py` для деталей реализации
- См. `migrations/001_add_last_check_time.sql` для SQL миграции
- См. `start_dempers.sh` для скрипта запуска

