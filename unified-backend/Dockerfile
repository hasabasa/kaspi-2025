FROM python:3.10-slim AS deps
WORKDIR /app

# системные deps (для asyncpg и для playwright --with-deps подтянет остальное)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    libicu-dev \
 && rm -rf /var/lib/apt/lists/*

# ставим питон-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ставим playwright и браузер chromium (одним слоем, чтобы кешировалось)
# если playwright уже в requirements.txt — шаг все равно безопасен
RUN pip install --no-cache-dir playwright \
 && playwright install --with-deps chromium

# ----------------------------------------------------------

FROM deps AS prod
WORKDIR /app
COPY . .

ENV PYTHONUNBUFFERED=1

# если запускаешь браузер как root, пригодится --no-sandbox
# Добавь эти флаги в коде при launch():
# p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])

CMD ["python", "demper_instance.py"]
