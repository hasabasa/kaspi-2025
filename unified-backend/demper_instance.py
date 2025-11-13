# demper_instance.py
import asyncio
import logging
import os
import random
import time
from decimal import Decimal

from api_parser import parse_product_by_sku, sync_product, sync_store_api  # твои функции
from db import create_pool  # должен возвращать asyncpg-пул

# ── Параметры шардирования ────────────────────────────────────────────────────
INSTANCE_INDEX = int(os.getenv("INSTANCE_INDEX", "0"))  # 0..N-1
INSTANCE_COUNT = int(os.getenv("INSTANCE_COUNT", "1"))  # N
ID_IS_UUID = os.getenv("ID_IS_UUID", "false").lower() in ("1", "true", "yes")
SYNC_STORES_MODE = os.getenv("SYNC_STORES_MODE", "leader")  # "leader" | "shard"


# ── Логи ──────────────────────────────────────────────────────────────────────
class NoHttpRequestFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # пропускаем всё, кроме сообщений, начинающихся с "HTTP Request"
        return not record.getMessage().startswith("HTTP Request:")


logging.getLogger().addFilter(NoHttpRequestFilter())
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [shard %(shard_idx)s/%(shard_cnt)s] %(message)s",
    handlers=[logging.FileHandler("price_worker.log", encoding="utf-8"), logging.StreamHandler()]
)


# добавим значения шардов во все записи логов
class ShardContext(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.shard_idx = INSTANCE_INDEX
        record.shard_cnt = INSTANCE_COUNT
        return True


logger = logging.getLogger("price_worker")
logger.addFilter(ShardContext())

# ── Параллелизм внутри инстанса ───────────────────────────────────────────────
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "100"))
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


# ── Логика обработки товара ───────────────────────────────────────────────────
async def process_product(product, clogger, pool):
    """Обрабатывает данные о продукте и обновляет цену в БД"""
    start_time = time.time()

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

                    # Синхронизация с внешней системой (если требуется)
                    sync_result = await sync_product(product_id, new_price)

                    if sync_result.get('success'):
                        # Обновляем цену продукта в нашей БД
                        async with pool.acquire() as connection:
                            await connection.execute(
                                """
                                UPDATE products
                                SET price = $1
                                WHERE id = $2
                                """,
                                int(new_price), product_id
                            )
                        clogger.info(f"Демпер: OK [{sku}] -> {new_price}")
            else:
                clogger.warning(f"Конкурентов нет [{sku}]")
        except Exception as e:
            clogger.error(f"Ошибка при обработке продукта [{sku}]: {e}", exc_info=False)

        # легкая рандомная задержка, чтобы не долбить API синхронно
        await asyncio.sleep(random.uniform(0.1, 0.3))

    elapsed_time = time.time() - start_time
    clogger.info(f"Время обработки [{sku}]: {elapsed_time:.2f} сек")


# ── Выборка шардов ────────────────────────────────────────────────────────────
async def fetch_products(pool):
    """
    Извлекаем только свой шард:
      - если id INT:     (id % INSTANCE_COUNT) = INSTANCE_INDEX
      - если id UUID:    mod(abs(hashtext(id::text)), INSTANCE_COUNT) = INSTANCE_INDEX
    """
    async with pool.acquire() as connection:
        if ID_IS_UUID:
            query = """
                    SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
                    FROM products
                    WHERE bot_active = TRUE
                      AND mod(abs(hashtext(id::text)), $1) = $2 \
                    """
        else:
            query = """
                    SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
                    FROM products
                    WHERE bot_active = TRUE
                      AND mod(abs(hashtext(id::text)), $1) = $2 \
                    """
        return await connection.fetch(query, INSTANCE_COUNT, INSTANCE_INDEX)


# ── Синхронизация магазинов ───────────────────────────────────────────────────
async def sync_store(sid, clogger):
    async with semaphore:
        try:
            result = await sync_store_api(sid)
            clogger.info(f"Синхронизирован магазин {sid}: {result}")
        except Exception as e:
            clogger.error(f"Ошибка sync_store_api для {sid}: {e}", exc_info=False)


def _should_sync_stores_for_sid(sid: int) -> bool:
    """Если распределяем синхронизацию по шардам (SYNC_STORES_MODE=shard)"""
    if SYNC_STORES_MODE != "shard":
        return INSTANCE_INDEX == 0  # лидер
    # распределяем по модулю store_id
    try:
        return (int(sid) % INSTANCE_COUNT) == INSTANCE_INDEX
    except Exception:
        # на случай если sid не int — на всякий случай по хэшу строки
        return (abs(hash(str(sid))) % INSTANCE_COUNT) == INSTANCE_INDEX


# ── Главный цикл ──────────────────────────────────────────────────────────────
async def check_and_update_prices():
    clogger = logging.getLogger("price_checker")
    clogger.addFilter(ShardContext())
    clogger.setLevel(logging.INFO)

    pool = await create_pool()

    while True:
        try:
            clogger.info("Старт цикла демпера...")
            products = await fetch_products(pool)
            clogger.info(f"Найдено {len(products)} активных продуктов в моём шарде.")

            # обработка товаров
            tasks = [asyncio.create_task(process_product(p, clogger, pool)) for p in products]
            if tasks:
                await asyncio.gather(*tasks)

            # синхронизация магазинов
            store_ids = {p["store_id"] for p in products}
            if store_ids:
                if SYNC_STORES_MODE == "leader" and INSTANCE_INDEX == 0:
                    clogger.info(f"[leader] Синхронизируем {len(store_ids)} магазинов.")
                    for sid in store_ids:
                        await sync_store(sid, clogger)
                elif SYNC_STORES_MODE == "shard":
                    my_store_ids = [sid for sid in store_ids if _should_sync_stores_for_sid(sid)]
                    clogger.info(f"[shard] Моих магазинов: {len(my_store_ids)}")
                    for sid in my_store_ids:
                        await sync_store(sid, clogger)

        except Exception as e:
            clogger.error(f"Error during price check/update: {e}", exc_info=False)

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(check_and_update_prices())
