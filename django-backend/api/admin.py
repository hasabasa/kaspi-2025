from django.contrib import admin
from .models import KaspiStore, Product, Preorder


@admin.register(KaspiStore)
class KaspiStoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'merchant_id', 'user_id', 'products_count', 'is_active', 'last_sync']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'merchant_id', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'kaspi_product_id', 'store', 'price', 'bot_active', 'last_check_time']
    list_filter = ['bot_active', 'category', 'store']
    search_fields = ['name', 'kaspi_product_id', 'kaspi_sku']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Preorder)
class PreorderAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'store', 'status', 'price', 'delivery_days']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'article', 'brand']
    readonly_fields = ['id', 'created_at', 'updated_at']

