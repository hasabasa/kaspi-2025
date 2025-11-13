# Быстрый старт: Исправление проблемы 526

## Шаг 1: Применить миграцию БД

```bash
# Подключитесь к вашей базе данных PostgreSQL
psql -U your_user -d your_database -f migrations/001_add_last_check_time.sql
```

**⚠️ КРИТИЧНО:** Миграция автоматически инициализирует `last_check_time` для существующих товаров, 
распределяя проверки на весь день. Это предотвращает проверку всех товаров в первом цикле.

### Проверка после миграции:
```sql
-- Проверьте статистику
SELECT 
    COUNT(*) FILTER (WHERE last_check_time IS NULL) as never_checked,
    COUNT(*) FILTER (WHERE last_check_time IS NOT NULL) as initialized
FROM products 
WHERE bot_active = TRUE;
```

Если `never_checked` > 0, выполните дополнительную инициализацию:
```bash
python3 scripts/initialize_last_check_time.py
```

## Шаг 2: Остановить старые инстансы демпера

```bash
# Остановить все запущенные демперы
pkill -f "python3 demper.py"
pkill -f "python3 demper_instance.py"
```

## Шаг 3: Запустить новые инстансы

### Вариант A: Один инстанс (для теста)

```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend

export MAX_CONCURRENT_TASKS=15
export DEMPER_INTERVAL=30
export CHECK_INTERVAL_SECONDS=30
export BATCH_SIZE=500

python3 demper.py
```

### Вариант B: Несколько инстансов (рекомендуется)

```bash
cd /Users/hasa/Downloads/huilo-667-45/kaspi-demper-main/backend

export INSTANCE_COUNT=5
export MAX_CONCURRENT_TASKS=15
export DEMPER_INTERVAL=30

./start_dempers.sh
```

## Шаг 4: Проверить работу

```bash
# Просмотр логов
tail -f logs/demper_*.log

# Проверка процессов
ps aux | grep demper_instance.py

# Поиск ошибок
grep -i error logs/demper_*.log
```

## Что изменилось

✅ **До:** 30000 товаров каждые 5 секунд, 100 параллельных запросов → блокировка 526  
✅ **После:** 500 товаров на инстанс × 5 инстансов, 15 параллельных запросов, цикл 30 секунд → работает стабильно

## Дополнительная настройка

Если все еще есть проблемы, уменьшите нагрузку:

```bash
export MAX_CONCURRENT_TASKS=10
export DEMPER_INTERVAL=60
export BATCH_SIZE=200
```

## Подробная документация

См. `DEMPER_526_FIX.md` для полной документации.

