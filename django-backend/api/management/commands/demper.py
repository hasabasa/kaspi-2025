"""
Django management command для демпера цен
Адаптировано из unified-backend/demper.py
"""
import asyncio
import random
import time
import logging
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Product
from api.services.parser_service import parse_product_by_sku, sync_product
from api.services.sync_service import sync_store_api
from kaspi_auth.session_manager import SessionManager

logger = logging.getLogger("demper")


class Command(BaseCommand):
    help = 'Демпер цен - автоматическое снижение цен товаров'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Интервал между циклами в секундах (по умолчанию: 5)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Запустить один раз и выйти',
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']
        
        if run_once:
            self.stdout.write("Запуск демпера (один раз)...")
            asyncio.run(self.check_and_update_prices())
        else:
            self.stdout.write(f"Запуск демпера с интервалом {interval} секунд...")
            while True:
                try:
                    asyncio.run(self.check_and_update_prices())
                    time.sleep(interval)
                except KeyboardInterrupt:
                    self.stdout.write("\nОстановка демпера...")
                    break
                except Exception as e:
                    logger.error(f"Ошибка в цикле демпера: {e}", exc_info=True)
                    time.sleep(interval)
    
    async def process_product(self, product):
        """Обрабатывает один товар"""
        try:
            product_id = str(product.id)
            product_external_id = product.external_kaspi_id
            sku = product.kaspi_sku
            current_price = Decimal(product.price) / 100  # Конвертируем из тиынов
            min_profit = Decimal(product.min_profit) if product.min_profit else Decimal('0.00')
            
            if not product_external_id:
                logger.warning(f"Пропущен товар {sku}: нет external_kaspi_id")
                return
            
            # Парсим конкурентов
            product_data = await parse_product_by_sku(str(product_external_id))
            
            if product_data and len(product_data):
                min_offer_price = min(Decimal(offer["price"]) for offer in product_data)
                
                if current_price > max(min_offer_price, min_profit):
                    new_price = min_offer_price - Decimal('1.00')
                    
                    # Получаем сессию магазина
                    session_manager = SessionManager(shop_uid=str(product.store_id))
                    if not session_manager.load():
                        logger.warning(f"Сессия для магазина {product.store_id} недействительна")
                        return
                    
                    cookies = session_manager.get_cookies()
                    merchant_id = session_manager.merchant_uid
                    
                    # Синхронизируем цену
                    sync_result = await sync_product(
                        product_id,
                        new_price,
                        cookies,
                        merchant_id,
                        product.kaspi_product_id
                    )
                    
                    if sync_result.get('success'):
                        # Обновляем цену в БД
                        product.price = int(new_price * 100)  # Конвертируем в тиыны
                        product.last_check_time = timezone.now()
                        product.save()
                        logger.info(f"Демпер: Успешно - [{sku}] -> {new_price}")
            else:
                logger.warning(f"Конкурентов нет [{sku}]")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке продукта [{product.kaspi_sku}]: {e}")
        
        # Пауза для имитации случайной задержки
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def check_and_update_prices(self):
        """Основная функция демпера"""
        logger.info("Начинаем работу демпера...")
        
        # Получаем активные товары
        products = Product.objects.filter(bot_active=True)
        logger.info(f"Нашли {products.count()} активных продуктов.")
        
        # Обрабатываем товары
        tasks = []
        for product in products:
            task = asyncio.create_task(self.process_product(product))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Синхронизируем магазины
        store_ids = {p.store_id for p in products}
        logger.info(f"Найдено {len(store_ids)} магазинов для синхронизации.")
        
        for store_id in store_ids:
            try:
                result = await sync_store_api(str(store_id))
                logger.info(f"Синхронизирован магазин {store_id}: {result}")
            except Exception as e:
                logger.error(f"Ошибка sync_store_api для {store_id}: {e}", exc_info=True)

