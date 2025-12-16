#!/bin/bash
# Скрипт для быстрого запуска WAHA сервера

echo "🚀 Запуск WAHA сервера для WhatsApp интеграции"
echo "=============================================="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "📥 Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "📥 Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Переход в папку WAHA
cd "$(dirname "$0")"

# Проверка файла docker-compose
if [ ! -f "docker-compose.waha.yml" ]; then
    echo "❌ Файл docker-compose.waha.yml не найден!"
    exit 1
fi

echo "✅ Файл конфигурации найден"

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose -f docker-compose.waha.yml down

# Запуск WAHA сервера
echo "🚀 Запуск WAHA сервера..."
docker-compose -f docker-compose.waha.yml up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервера..."
sleep 10

# Проверка статуса
echo "🔍 Проверка статуса сервера..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ WAHA сервер запущен успешно!"
    echo ""
    echo "📱 Следующие шаги:"
    echo "1. Получите QR код: curl http://localhost:3000/api/sessions/kaspi_demper_session/qr"
    echo "2. Отсканируйте QR код в WhatsApp"
    echo "3. Проверьте статус: curl http://localhost:3000/api/sessions/kaspi_demper_session/status"
    echo ""
    echo "🌐 WAHA сервер доступен по адресу: http://localhost:3000"
    echo "📊 Веб-интерфейс: http://localhost:3000/api/docs"
else
    echo "❌ WAHA сервер не запустился!"
    echo "📋 Проверьте логи: docker-compose -f docker-compose.waha.yml logs"
    exit 1
fi

echo ""
echo "🎉 Готово! WAHA сервер работает!"
