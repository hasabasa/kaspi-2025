FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Копируем код приложения
COPY . .

# Создаем директории для логов
RUN mkdir -p logs staticfiles

# Запускаем миграции и сервер
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8010

