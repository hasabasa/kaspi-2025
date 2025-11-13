#!/bin/bash
# Скрипт для периодического обслуживания индексов
# Рекомендуется запускать раз в день в 3:00 ночи через cronjob
# 
# Добавить в crontab:
# 0 3 * * * /path/to/maintenance_cronjob.sh >> /var/log/demper_maintenance.log 2>&1

set -e

# Конфигурация
DB_USER="${DB_USER:-demper_user}"
DB_NAME="${DB_NAME:-demper}"
DB_HOST="${DB_HOST:-95.179.187.42}"
DB_PORT="${DB_PORT:-6432}"
MIGRATIONS_DIR="$(dirname "$0")/../migrations"

echo "🔧 Начало обслуживания индексов: $(date)"

# Переиндексирование
echo "📊 Переиндексирование..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATIONS_DIR/003_maintenance_vacuum.sql"

# Проверка производительности
echo "✅ Проверка производительности индексов..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATIONS_DIR/002_check_index_performance.sql" > /tmp/index_performance_check.log 2>&1

echo "✅ Обслуживание завершено: $(date)"
echo "📝 Результаты проверки производительности:"
cat /tmp/index_performance_check.log

