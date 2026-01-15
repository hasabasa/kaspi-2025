"""
Модели Django для Kaspi Backend
"""
import uuid
import json
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class KaspiStore(models.Model):
    """Магазин Kaspi"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    user_id = models.CharField(max_length=255, db_index=True, verbose_name="ID пользователя")
    merchant_id = models.CharField(max_length=255, db_index=True, verbose_name="ID мерчанта")
    name = models.CharField(max_length=255, verbose_name="Название магазина")
    api_key = models.CharField(max_length=255, default='auto_generated_token', verbose_name="API ключ")
    products_count = models.IntegerField(default=0, verbose_name="Количество товаров")
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name="Последняя синхронизация")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активен")
    
    # Дополнительные поля для сессий
    guid = models.JSONField(null=True, blank=True, verbose_name="Cookies и данные сессии")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Последний вход")
    
    class Meta:
        db_table = 'kaspi_stores'
        verbose_name = 'Магазин Kaspi'
        verbose_name_plural = 'Магазины Kaspi'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['merchant_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.merchant_id})"


class Product(models.Model):
    """Товар из магазина Kaspi"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    kaspi_product_id = models.CharField(max_length=255, db_index=True, verbose_name="ID продукта в Kaspi")
    kaspi_sku = models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name="SKU")
    store = models.ForeignKey(
        KaspiStore,
        on_delete=models.CASCADE,
        related_name='products',
        db_index=True,
        verbose_name="Магазин"
    )
    price = models.IntegerField(verbose_name="Цена в тиынах")  # 1/100 тенге
    name = models.CharField(max_length=500, verbose_name="Название товара")
    external_kaspi_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Внешний ID")
    category = models.CharField(max_length=255, null=True, blank=True, verbose_name="Категория")
    image_url = models.URLField(null=True, blank=True, verbose_name="URL изображения")
    bot_active = models.BooleanField(default=True, db_index=True, verbose_name="Бот активен")
    last_check_time = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="Время последней проверки")
    
    # Дополнительные поля для демпера
    min_profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Минимальная прибыль")
    max_profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Максимальная прибыль")
    strategy = models.CharField(max_length=50, null=True, blank=True, verbose_name="Стратегия ценообразования")
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['kaspi_product_id']),
            models.Index(fields=['kaspi_sku']),
            models.Index(fields=['bot_active']),
            models.Index(fields=['bot_active', 'last_check_time']),  # Для оптимизации демпера
        ]
    
    def __str__(self):
        return f"{self.name} ({self.kaspi_product_id})"
    
    @property
    def price_in_tenge(self):
        """Цена в тенге"""
        return self.price / 100


class Preorder(models.Model):
    """Предзаказ"""
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='preorders',
        db_index=True,
        verbose_name="Товар"
    )
    store = models.ForeignKey(
        KaspiStore,
        on_delete=models.CASCADE,
        related_name='preorders',
        db_index=True,
        verbose_name="Магазин"
    )
    article = models.CharField(max_length=255, null=True, blank=True, verbose_name="Артикул")
    name = models.CharField(max_length=500, verbose_name="Название")
    brand = models.CharField(max_length=255, null=True, blank=True, verbose_name="Бренд")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='processing', db_index=True, verbose_name="Статус")
    price = models.IntegerField(null=True, blank=True, verbose_name="Цена в тиынах")
    warehouses = models.JSONField(default=dict, verbose_name="Информация о складах")
    delivery_days = models.IntegerField(default=30, verbose_name="Дни доставки")
    
    class Meta:
        db_table = 'preorders'
        verbose_name = 'Предзаказ'
        verbose_name_plural = 'Предзаказы'
        unique_together = [['product', 'store']]
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['store']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Предзаказ {self.name} ({self.status})"

