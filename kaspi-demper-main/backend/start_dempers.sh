#!/bin/bash
# start_dempers.sh
# Скрипт для запуска нескольких инстансов демпера с задержкой
# Это распределяет нагрузку и предотвращает блокировки 526

set -e

# Параметры конфигурации
INSTANCE_COUNT=${INSTANCE_COUNT:-5}
MAX_CONCURRENT=${MAX_CONCURRENT_TASKS:-15}
DEMPER_INTERVAL=${DEMPER_INTERVAL:-30}
CHECK_INTERVAL=${CHECK_INTERVAL_SECONDS:-30}
BATCH_SIZE=${BATCH_SIZE:-500}
MIN_DELAY=${MIN_PRODUCT_DELAY:-0.3}
MAX_DELAY=${MAX_PRODUCT_DELAY:-0.8}
STAGGER_DELAY=${STAGGER_DELAY:-2}  # Задержка между запуском инстансов (секунды)

# Создаем директорию для логов, если её нет
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "🚀 Запуск $INSTANCE_COUNT инстансов демпера..."
echo "📋 Параметры:"
echo "   - INSTANCE_COUNT: $INSTANCE_COUNT"
echo "   - MAX_CONCURRENT_TASKS: $MAX_CONCURRENT"
echo "   - DEMPER_INTERVAL: $DEMPER_INTERVAL сек"
echo "   - CHECK_INTERVAL_SECONDS: $CHECK_INTERVAL сек"
echo "   - BATCH_SIZE: $BATCH_SIZE"
echo "   - DELAY: $MIN_DELAY-$MAX_DELAY сек"
echo "   - STAGGER_DELAY: $STAGGER_DELAY сек"
echo ""

# Запускаем каждый инстанс с небольшой задержкой
for i in $(seq 0 $((INSTANCE_COUNT - 1))); do
    echo "▶️  Запуск инстанса $i/$INSTANCE_COUNT..."
    
    INSTANCE_INDEX=$i \
    INSTANCE_COUNT=$INSTANCE_COUNT \
    MAX_CONCURRENT_TASKS=$MAX_CONCURRENT \
    DEMPER_INTERVAL=$DEMPER_INTERVAL \
    CHECK_INTERVAL_SECONDS=$CHECK_INTERVAL \
    BATCH_SIZE=$BATCH_SIZE \
    MIN_PRODUCT_DELAY=$MIN_DELAY \
    MAX_PRODUCT_DELAY=$MAX_DELAY \
    nohup python3 demper_instance.py > "$LOG_DIR/demper_$i.log" 2>&1 &
    
    DEMPER_PID=$!
    echo "   ✅ Инстанс $i запущен (PID: $DEMPER_PID)"
    echo "   📝 Логи: $LOG_DIR/demper_$i.log"
    
    # Задержка перед запуском следующего инстанса
    if [ $i -lt $((INSTANCE_COUNT - 1)) ]; then
        echo "   ⏳ Ожидание ${STAGGER_DELAY} секунд перед запуском следующего инстанса..."
        sleep $STAGGER_DELAY
    fi
    echo ""
done

echo "✅ Все $INSTANCE_COUNT инстансов демпера запущены!"
echo ""
echo "📊 Мониторинг:"
echo "   - Логи всех инстансов: tail -f $LOG_DIR/demper_*.log"
echo "   - Лог конкретного инстанса: tail -f $LOG_DIR/demper_0.log"
echo ""
echo "🛑 Остановка всех инстансов:"
echo "   pkill -f 'python3 demper_instance.py'"
echo ""

# Сохраняем PIDs для удобства остановки
echo $! > "$LOG_DIR/demper_pids.txt"
for pid in $(pgrep -f "python3 demper_instance.py"); do
    echo $pid >> "$LOG_DIR/demper_pids.txt"
done

echo "💾 PIDs сохранены в $LOG_DIR/demper_pids.txt"

