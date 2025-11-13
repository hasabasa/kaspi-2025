#!/bin/bash
# start-unified-backend.sh
# Скрипт для запуска unified-backend

echo "🚀 Запуск Unified Backend..."

# Переходим в директорию unified-backend
cd /Users/hasen/demper-667-45/unified-backend

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден"
    echo "📝 Создайте файл .env на основе env.example"
    echo "   cp env.example .env"
    echo "   # Затем отредактируйте .env с вашими настройками"
    exit 1
fi

# Проверяем наличие зависимостей
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден"
    exit 1
fi

# Устанавливаем зависимости (если нужно)
echo "📦 Проверка зависимостей..."
pip3 install -r requirements.txt --quiet

# Запускаем backend
echo "🎯 Запуск backend на http://localhost:8010"
echo "📖 API документация: http://localhost:8010/docs"
echo "🏥 Health check: http://localhost:8010/health"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

python3 main.py
