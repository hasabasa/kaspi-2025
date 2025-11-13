# demper.py
# nohup python3 demper.py > demper.log 2>&1 &
import asyncio
import logging
import os
import random
import time
from decimal import Decimal, ROUND_DOWN

from supabase import create_client, Client

from api_parser import parse_product_by_sku, sync_product, sync_store_api  # ваши функции
from db import create_pool

logging.getLogger("postgrest").setLevel(logging.WARNING)

# Если используются httpx / urllib3 — тоже понизить им уровень
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
for lib in ("supabase", "httpx", "httpcore", "urllib3", "postgrest", "gotrue"):
    lg = logging.getLogger(lib)
    lg.setLevel(logging.WARNING)
    lg.propagate = False

# ── Настраиваемые параметры через переменные окружения ──────────────────────────
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "15"))  # По умолчанию 15 вместо 100
DEMPER_INTERVAL = int(os.getenv("DEMPER_INTERVAL", "30"))  # Интервал цикла в секундах (30 вместо 5)
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))  # Минимальный интервал между проверками товара
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))  # Максимум товаров за один цикл
MIN_PRODUCT_DELAY = float(os.getenv("MIN_PRODUCT_DELAY", "0.3"))  # Минимальная задержка между товарами
MAX_PRODUCT_DELAY = float(os.getenv("MAX_PRODUCT_DELAY", "0.8"))  # Максимальная задержка между товарами

semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


class NoHttpRequestFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # пропускаем всё, кроме сообщений, начинающихся с "HTTP Request"
        return not record.getMessage().startswith("HTTP Request:")


logging.getLogger().addFilter(NoHttpRequestFilter())
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("price_worker.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger("price_worker")


# добавляем фильтр на уровень корневого логгера


async def process_product(product, clogger, pool):
    """
    Обрабатывает данные о продукте и обновляет цену в базе данных.
    ВАЖНО: Kaspi API принимает только целые числа (без копеек).
    Все цены округляются ВНИЗ до целого числа для гарантии конкурентоспособности.
    """
    start_time = time.time()
    product_id = product["id"]
    product_external_id = product["external_kaspi_id"]
    sku = product["kaspi_sku"]
    new_price = None  # Будет установлено, если нужно обновить цену
    
    async with semaphore:
        # Текущая цена из БД (может быть Decimal с копейками от старого API)
        current_price = Decimal(str(product["price"]))
        # Округляем текущую цену до целого числа (для сравнения)
        current_price_int = int(current_price.quantize(Decimal('1'), rounding=ROUND_DOWN))
        
        min_profit = Decimal(str(product['min_profit'])) if product['min_profit'] else Decimal('0')
        min_profit_int = int(min_profit.quantize(Decimal('1'), rounding=ROUND_DOWN))
        
        try:
            product_data = await parse_product_by_sku(str(product_external_id))
            if product_data and len(product_data):
                # Получаем цены от конкурентов (могут быть с копейками от API)
                competitor_prices = [Decimal(str(offer["price"])) for offer in product_data]
                min_offer_price = min(competitor_prices)
                
                # Kaspi требует целые числа! Округляем конкурентскую цену ВНИЗ до целого
                min_offer_price_int = int(min_offer_price.quantize(Decimal('1'), rounding=ROUND_DOWN))
                
                # Проверяем, нужно ли менять цену
                if current_price_int > max(min_offer_price_int, min_profit_int):
                    # Устанавливаем цену на 1тг ниже конкурента (гарантированно целое число)
                    new_price = min_offer_price_int - 1
                    
                    # Проверяем минимальную прибыль
                    if new_price >= min_profit_int:
                        # Отправляем в Kaspi (целое число гарантировано)
                        sync_result = await sync_product(product_id, Decimal(str(new_price)))
                        
                        if sync_result.get('success'):
                            clogger.info(f"✅ Демпер: OK [{sku}] конкурент {min_offer_price_int}тг → мы {new_price}тг")
                        else:
                            clogger.warning(f"⚠️ Kaspi отклонил цену {new_price}тг для [{sku}]: {sync_result.get('message', 'Unknown error')}")
                            # Если Kaspi отклонил, не обновляем цену в БД
                            new_price = None
                    else:
                        clogger.warning(f"⚠️ Цена {new_price}тг ниже минимальной прибыли {min_profit_int}тг [{sku}]")
                        new_price = None
                else:
                    clogger.info(f"ℹ️ Демпер: цена конкурента {min_offer_price_int}тг ≥ нашей {current_price_int}тг [{sku}], не меняем")
            else:
                clogger.warning(f"ℹ️ Конкурентов нет [{sku}]")
        except Exception as e:
            clogger.error(f"❌ Ошибка при обработке продукта [{sku}]: {e}")
        
        # ОДИН UPDATE в конце: обновляем и цену (если изменилась), и last_check_time
        try:
            async with pool.acquire() as connection:
                if new_price is not None:
                    # Обновляем цену (целое число) и last_check_time
                    await connection.execute(
                        """
                        UPDATE products
                        SET price = $1, last_check_time = NOW()
                        WHERE id = $2
                        """,
                        new_price,  # ✅ Гарантированно целое число для Kaspi
                        product_id
                    )
                else:
                    # Обновляем только last_check_time
                    await connection.execute(
                        """
                        UPDATE products
                        SET last_check_time = NOW()
                        WHERE id = $1
                        """,
                        product_id
                    )
        except Exception as e:
            clogger.error(f"❌ Ошибка обновления БД для [{sku}]: {e}")
        
        # Пауза для распределения нагрузки во времени
        await asyncio.sleep(random.uniform(MIN_PRODUCT_DELAY, MAX_PRODUCT_DELAY))

    elapsed_time = time.time() - start_time
    clogger.info(f"⏱️ Время обработки [{sku}]: {elapsed_time:.2f} сек")


async def fetch_products(pool):
    """
    Асинхронно извлекает список продуктов из базы данных с rate limiting.
    Берет только товары, которые не проверялись более CHECK_INTERVAL_SECONDS секунд,
    ограничивая количество товаров за цикл для распределения нагрузки.
    """
    async with pool.acquire() as connection:
        # Используем параметризованный запрос для безопасности
        # make_interval работает на всех версиях PostgreSQL
        query = """
        SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
        FROM products
        WHERE bot_active = TRUE
          AND (last_check_time IS NULL 
               OR last_check_time < NOW() - make_interval(secs => $1))
        ORDER BY last_check_time ASC NULLS FIRST
        LIMIT $2
        """
        products = await connection.fetch(query, CHECK_INTERVAL_SECONDS, BATCH_SIZE)
        return products


async def sync_store(sid, clogger):
    """Синхронизация магазина"""
    async with semaphore:
        try:
            result = await sync_store_api(sid)
            clogger.info(f"Синхронизирован магазин {sid}: {result}")
        except Exception as e:
            clogger.error(f"Ошибка sync_store_api для {sid}: {e}", exc_info=True)


async def check_and_update_prices():
    clogger = logging.getLogger("price_checker")
    clogger.setLevel(logging.INFO)
    pool = await create_pool()
    
    clogger.info(f"🚀 Демпер запущен с параметрами:")
    clogger.info(f"   - MAX_CONCURRENT_TASKS: {MAX_CONCURRENT_TASKS}")
    clogger.info(f"   - DEMPER_INTERVAL: {DEMPER_INTERVAL} сек")
    clogger.info(f"   - CHECK_INTERVAL_SECONDS: {CHECK_INTERVAL_SECONDS} сек")
    clogger.info(f"   - BATCH_SIZE: {BATCH_SIZE}")
    clogger.info(f"   - DELAY: {MIN_PRODUCT_DELAY}-{MAX_PRODUCT_DELAY} сек")

    while True:
        try:
            clogger.info("=" * 60)
            clogger.info("🔄 Начинаем цикл демпера...")
            products = await fetch_products(pool)
            clogger.info(f"📦 Найдено {len(products)} товаров для проверки (из {BATCH_SIZE} возможных)")

            if not products:
                clogger.info("✅ Нет товаров, требующих проверки. Ожидание следующего цикла...")
            else:
                # Список задач для обработки продуктов
                tasks = []
                for product in products:
                    task = asyncio.create_task(process_product(product, clogger, pool))
                    tasks.append(task)

                # Обрабатываем товары с ограничением параллелизма
                await asyncio.gather(*tasks)
                clogger.info(f"✅ Обработано {len(products)} товаров")

                # Синхронизация магазинов (только если есть товары)
                store_ids = {p["store_id"] for p in products}
                if store_ids:
                    clogger.info(f"🏪 Синхронизация {len(store_ids)} магазинов...")
                    for sid in store_ids:
                        await sync_store(sid, clogger)

        except Exception as e:
            clogger.error(f"❌ Ошибка во время цикла демпера: {e}", exc_info=True)

        clogger.info(f"⏳ Ожидание {DEMPER_INTERVAL} секунд до следующего цикла...")
        await asyncio.sleep(DEMPER_INTERVAL)


if __name__ == "__main__":
    asyncio.run(check_and_update_prices())
