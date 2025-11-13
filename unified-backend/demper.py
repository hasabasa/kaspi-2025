# demper.py
# nohup python3 demper.py > demper.log 2>&1 &
import asyncio
import logging
import random
import time
from decimal import Decimal

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

MAX_CONCURRENT_TASKS = 100
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
    """Обрабатывает данные о продукте и обновляет цену в базе данных Supabase"""
    start_time = time.time()
    # clogger.info(f"Начинаем обработку продукта [{product['kaspi_sku']}]")

    async with semaphore:
        product_id = product["id"]
        product_external_id = product["external_kaspi_id"]
        sku = product["kaspi_sku"]
        current_price = Decimal(product["price"])
        min_profit = Decimal(product['min_profit']) if product['min_profit'] else Decimal('0.00')
        try:
            product_data = await parse_product_by_sku(str(product_external_id))
            if product_data and len(product_data):
                min_offer_price = min(Decimal(offer["price"]) for offer in product_data)

                if current_price > max(min_offer_price, min_profit):
                    new_price = min_offer_price - Decimal('1.00')

                    # Синхронизация с базой данных
                    sync_result = await sync_product(product_id, new_price)

                    if sync_result.get('success'):
                        # Получаем соединение с базой данных
                        async with pool.acquire() as connection:
                            # Обновляем цену продукта в Supabase
                            await connection.execute(
                                """
                                UPDATE products
                                SET price = $1
                                WHERE id = $2
                                """,
                                int(new_price), product_id
                            )
                        clogger.info(f"Демпер: Успешно - [{sku}] -> {new_price}")
            else:
                clogger.warning(f"Конкурентов нет [{sku}]")
        except Exception as e:
            clogger.error(f"Ошибка при обработке продукта [{sku}]: {e}")
            # traceback.print_exc()
        # Пауза для имитации случайной задержки между запросами
        await asyncio.sleep(random.uniform(0.1, 0.3))

    elapsed_time = time.time() - start_time
    clogger.info(f"Время обработки продукта [{product['kaspi_sku']}]: {elapsed_time:.2f} секунд")


async def fetch_products(pool):
    """Асинхронно извлекает список продуктов из базы данных Supabase через пул соединений"""
    async with pool.acquire() as connection:
        query = """
        SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
        FROM products
        WHERE bot_active = TRUE
        """
        products = await connection.fetch(query)
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

    while True:
        try:
            clogger.info("Начинаем работу демпера...")
            products = await fetch_products(pool)
            clogger.info(f"Нашли {len(products)} активных продуктов.")

            # Список задач для обработки продуктов
            tasks = []
            for product in products:
                task = asyncio.create_task(process_product(product, clogger, pool))
                tasks.append(task)

            # Ограничиваем количество одновременно выполняемых задач
            await asyncio.gather(*tasks)

            # Список задач для синхронизации магазинов
            store_ids = {p["store_id"] for p in products}
            clogger.info(f"Найдено {len(store_ids)} магазинов для синхронизации.")

            # Обрабатываем каждый магазин по очереди
            for sid in store_ids:
                await sync_store(sid, clogger)  # Синхронизируем магазин последовательно

        except Exception as e:
            clogger.error(f"Error during price check/update: {e}", exc_info=True)

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(check_and_update_prices())
