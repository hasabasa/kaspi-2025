# demper_instance.py
import asyncio
import logging
import os
import random
import time
from decimal import Decimal, ROUND_DOWN

from api_parser import parse_product_by_sku, sync_product, sync_store_api  # твои функции
from db import create_pool  # должен возвращать asyncpg-пул

# ── Параметры шардирования ────────────────────────────────────────────────────
INSTANCE_INDEX = int(os.getenv("INSTANCE_INDEX", "0"))  # 0..N-1
INSTANCE_COUNT = int(os.getenv("INSTANCE_COUNT", "1"))  # N
ID_IS_UUID = os.getenv("ID_IS_UUID", "false").lower() in ("1", "true", "yes")
SYNC_STORES_MODE = os.getenv("SYNC_STORES_MODE", "leader")  # "leader" | "shard"

# ── Настраиваемые параметры для rate limiting ─────────────────────────────────
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))  # Минимальный интервал между проверками
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))  # Максимум товаров за цикл на инстанс
MIN_PRODUCT_DELAY = float(os.getenv("MIN_PRODUCT_DELAY", "0.3"))  # Минимальная задержка
MAX_PRODUCT_DELAY = float(os.getenv("MAX_PRODUCT_DELAY", "0.8"))  # Максимальная задержка
DEMPER_INTERVAL = int(os.getenv("DEMPER_INTERVAL", "30"))  # Интервал цикла в секундах


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
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "15"))  # По умолчанию 15 вместо 100
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


# ── Логика обработки товара ───────────────────────────────────────────────────
async def process_product(product, clogger, pool):
    """
    Обрабатывает данные о продукте и обновляет цену в БД.
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
            clogger.error(f"❌ Ошибка при обработке продукта [{sku}]: {e}", exc_info=False)
        
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
            clogger.error(f"❌ Ошибка обновления БД для [{sku}]: {e}", exc_info=False)
        
        # Распределение нагрузки во времени
        await asyncio.sleep(random.uniform(MIN_PRODUCT_DELAY, MAX_PRODUCT_DELAY))

    elapsed_time = time.time() - start_time
    clogger.info(f"⏱️ Время обработки [{sku}]: {elapsed_time:.2f} сек")


# ── Выборка шардов ────────────────────────────────────────────────────────────
async def fetch_products(pool):
    """
    Извлекаем только свой шард с rate limiting:
      - если id UUID:    mod(abs(hashtext(id::text)), INSTANCE_COUNT) = INSTANCE_INDEX
      - если id INT:     (id::bigint % INSTANCE_COUNT) = INSTANCE_INDEX
    Добавлен фильтр по last_check_time для распределения нагрузки во времени.
    """
    async with pool.acquire() as connection:
        if ID_IS_UUID:
            # Для UUID используем hashtext
            query = """
                    SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
                    FROM products
                    WHERE bot_active = TRUE
                      AND mod(abs(hashtext(id::text)), $1) = $2
                      AND (last_check_time IS NULL 
                           OR last_check_time < NOW() - make_interval(secs => $3))
                    ORDER BY last_check_time ASC NULLS FIRST
                    LIMIT $4
                    """
            return await connection.fetch(
                query,
                INSTANCE_COUNT,
                INSTANCE_INDEX,
                CHECK_INTERVAL_SECONDS,
                BATCH_SIZE
            )
        else:
            # Для INT используем модуль с правильной обработкой отрицательных значений
            # Формула ((id % N) + N) % N гарантирует неотрицательный результат
            query = """
                    SELECT id, store_id, kaspi_sku, external_kaspi_id, price, min_profit
                    FROM products
                    WHERE bot_active = TRUE
                      AND ((id::bigint % $1) + $1) % $1 = $2
                      AND (last_check_time IS NULL 
                           OR last_check_time < NOW() - make_interval(secs => $3))
                    ORDER BY last_check_time ASC NULLS FIRST
                    LIMIT $4
                    """
            return await connection.fetch(
                query,
                INSTANCE_COUNT,
                INSTANCE_INDEX,
                CHECK_INTERVAL_SECONDS,
                BATCH_SIZE
            )


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
    
    clogger.info(f"🚀 Демпер-инстанс [{INSTANCE_INDEX}/{INSTANCE_COUNT}] запущен с параметрами:")
    clogger.info(f"   - MAX_CONCURRENT_TASKS: {MAX_CONCURRENT_TASKS}")
    clogger.info(f"   - DEMPER_INTERVAL: {DEMPER_INTERVAL} сек")
    clogger.info(f"   - CHECK_INTERVAL_SECONDS: {CHECK_INTERVAL_SECONDS} сек")
    clogger.info(f"   - BATCH_SIZE: {BATCH_SIZE}")
    clogger.info(f"   - DELAY: {MIN_PRODUCT_DELAY}-{MAX_PRODUCT_DELAY} сек")
    clogger.info(f"   - SYNC_STORES_MODE: {SYNC_STORES_MODE}")
    clogger.info(f"   - ID_IS_UUID: {ID_IS_UUID}")

    while True:
        try:
            clogger.info("=" * 60)
            clogger.info(f"🔄 [Shard {INSTANCE_INDEX}/{INSTANCE_COUNT}] Старт цикла демпера...")
            products = await fetch_products(pool)
            clogger.info(f"📦 [Shard {INSTANCE_INDEX}/{INSTANCE_COUNT}] Найдено {len(products)} товаров для проверки (из {BATCH_SIZE} возможных)")

            if not products:
                clogger.info(f"✅ [Shard {INSTANCE_INDEX}/{INSTANCE_COUNT}] Нет товаров, требующих проверки.")
            else:
                # обработка товаров
                tasks = [asyncio.create_task(process_product(p, clogger, pool)) for p in products]
                if tasks:
                    await asyncio.gather(*tasks)
                clogger.info(f"✅ [Shard {INSTANCE_INDEX}/{INSTANCE_COUNT}] Обработано {len(products)} товаров")

                # синхронизация магазинов
                store_ids = {p["store_id"] for p in products}
                if store_ids:
                    if SYNC_STORES_MODE == "leader" and INSTANCE_INDEX == 0:
                        clogger.info(f"🏪 [leader] Синхронизируем {len(store_ids)} магазинов.")
                        for sid in store_ids:
                            await sync_store(sid, clogger)
                    elif SYNC_STORES_MODE == "shard":
                        my_store_ids = [sid for sid in store_ids if _should_sync_stores_for_sid(sid)]
                        clogger.info(f"🏪 [shard] Моих магазинов: {len(my_store_ids)}")
                        for sid in my_store_ids:
                            await sync_store(sid, clogger)

        except Exception as e:
            clogger.error(f"❌ [Shard {INSTANCE_INDEX}/{INSTANCE_COUNT}] Ошибка во время цикла: {e}", exc_info=False)

        clogger.info(f"⏳ [Shard {INSTANCE_INDEX}/{INSTANCE_COUNT}] Ожидание {DEMPER_INTERVAL} секунд до следующего цикла...")
        await asyncio.sleep(DEMPER_INTERVAL)


if __name__ == "__main__":
    asyncio.run(check_and_update_prices())
