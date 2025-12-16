#!/usr/bin/env python3
"""
Скрипт для инициализации last_check_time для существующих товаров
Запускать после применения миграции 001_add_last_check_time.sql
для безопасного распределения нагрузки при первом запуске демпера
"""

import asyncio
import logging
from db import create_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_last_check_time():
    """
    Инициализирует last_check_time для всех товаров с bot_active = TRUE
    Распределяет проверки на весь день, чтобы избежать 526 блокировки при первом запуске
    """
    pool = await create_pool()
    
    try:
        async with pool.acquire() as conn:
            # Проверяем, сколько товаров нужно инициализировать
            count = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM products 
                WHERE last_check_time IS NULL 
                  AND bot_active = TRUE
            """)
            
            if count == 0:
                logger.info("✅ Все товары уже инициализированы")
                return
            
            logger.info(f"📦 Найдено {count} товаров для инициализации")
            
            # Распределяем проверки на весь день (каждый товар через 10 секунд)
            # Можно изменить интервал в зависимости от количества товаров
            interval_seconds = 10
            total_seconds = count * interval_seconds
            
            if total_seconds > 86400:  # Больше суток
                # Если товаров слишком много, распределяем на несколько дней
                days_needed = (total_seconds // 86400) + 1
                logger.warning(f"⚠️ Товаров слишком много ({count}). Распределение займет {days_needed} дней")
            
            # Инициализируем товары одним запросом (PostgreSQL справится даже с большим количеством)
            # Используем простой подход: распределяем на весь день равномерно
            logger.info("🔄 Начинаем инициализацию...")
            
            result = await conn.execute("""
                UPDATE products
                SET last_check_time = NOW() - INTERVAL '1 day' + (
                    row_number() OVER (ORDER BY id) * INTERVAL '10 seconds'
                )
                WHERE last_check_time IS NULL 
                  AND bot_active = TRUE
            """)
            
            # Проверяем, сколько строк обновлено
            rows_affected = int(result.split()[-1]) if result else 0
            logger.info(f"✅ Инициализировано {rows_affected} товаров")
            
            # Обновляем статистику для планировщика
            await conn.execute("ANALYZE products")
            logger.info("✅ Статистика обновлена")
            
            # Проверяем результат
            ready_for_check = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM products 
                WHERE bot_active = TRUE
                  AND last_check_time IS NOT NULL
                  AND last_check_time < NOW() - make_interval(secs => 30)
            """)
            
            logger.info(f"📊 Готово к проверке: {ready_for_check} товаров")
            logger.info(f"📊 Ожидают проверки: {count - ready_for_check} товаров")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации: {e}", exc_info=True)
        raise
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(initialize_last_check_time())

