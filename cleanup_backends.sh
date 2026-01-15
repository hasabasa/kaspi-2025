#!/bin/bash
# Скрипт для очистки старых бэкендов

echo "🧹 Очистка старых бэкендов..."

# Создаем папку архива для важных файлов
ARCHIVE_DIR="archive_backends_$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR/unified-backend"

echo "📦 Архивируем важные файлы из unified-backend..."

# Копируем критичные файлы в архив
if [ -d "unified-backend" ]; then
    cp unified-backend/api_parser.py "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp unified-backend/proxy_balancer.py "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp unified-backend/error_handlers.py "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp unified-backend/demper.py "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp unified-backend/demper_instance.py "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp -r unified-backend/routes "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp -r unified-backend/migrations "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    cp unified-backend/utils.py "$ARCHIVE_DIR/unified-backend/" 2>/dev/null
    echo "✅ Важные файлы сохранены в $ARCHIVE_DIR"
fi

echo ""
echo "🗑️  Удаляем старые бэкенды..."
echo ""

# Удаляем старые бэкенды (можно безопасно удалить)
read -p "Удалить backend/ (старый бэкенд)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf backend/
    echo "✅ Удален backend/"
fi

read -p "Удалить newnew/ (дубликат бэкенда)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf newnew/
    echo "✅ Удален newnew/"
fi

read -p "Удалить unified-backend/ (основной FastAPI бэкенд)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf unified-backend/
    echo "✅ Удален unified-backend/"
fi

read -p "Удалить simple_kaspi_backend.py? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f simple_kaspi_backend.py
    echo "✅ Удален simple_kaspi_backend.py"
fi

read -p "Удалить start-unified-backend.sh? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f start-unified-backend.sh
    echo "✅ Удален start-unified-backend.sh"
fi

echo ""
echo "✨ Очистка завершена!"
echo "📦 Архив сохранен в: $ARCHIVE_DIR"
echo ""
echo "⚠️  ВАЖНО: Проверьте, что все функции перенесены в django-backend!"
echo "   См. django-backend/ARCHIVE_NOTES.md для списка функций"

