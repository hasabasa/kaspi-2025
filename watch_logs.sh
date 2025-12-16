#!/bin/bash

echo "🔍 Мониторинг логов unified-backend"
echo "=================================="
echo ""
echo "📊 Backend API: http://localhost:8010/docs"
echo "🌐 Frontend: http://localhost:8080"
echo ""
echo "📋 Логи будут появляться здесь при тестировании Kaspi..."
echo ""

# Проверяем статус backend
echo "🔧 Проверка статуса backend..."
if curl -s http://localhost:8010/docs > /dev/null; then
    echo "✅ Backend работает на порту 8010"
else
    echo "❌ Backend не отвечает"
fi

echo ""
echo "🌐 Проверка статуса frontend..."
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ Frontend работает на порту 8080"
else
    echo "❌ Frontend не отвечает"
fi

echo ""
echo "🚀 Готово! Теперь тестируйте авторизацию Kaspi в браузере:"
echo "   http://localhost:8080"
echo ""
echo "📝 Логи парсинга будут появляться в консоли backend"
echo "   (этот терминал будет показывать логи в реальном времени)"
echo ""
echo "⏹️  Нажмите Ctrl+C для выхода"
echo ""

# Мониторим логи backend
echo "🔍 Начинаем мониторинг логов..."
echo ""

# Проверяем, есть ли файл логов
if [ -f "/Users/hasen/demper-667-45/unified-backend/logs/app.log" ]; then
    echo "📄 Читаем логи из файла..."
    tail -f /Users/hasen/demper-667-45/unified-backend/logs/app.log
else
    echo "⚠️  Файл логов не найден. Логи выводятся в консоль backend."
    echo "   Для просмотра логов откройте отдельный терминал и выполните:"
    echo "   cd /Users/hasen/demper-667-45/unified-backend && python3 main.py"
    echo ""
    echo "🔄 Проверяем API endpoints каждые 5 секунд..."
    
    while true; do
        echo "$(date): Проверка API..."
        curl -s http://localhost:8010/api/v1/admin/health > /dev/null && echo "✅ API отвечает" || echo "❌ API не отвечает"
        sleep 5
    done
fi
