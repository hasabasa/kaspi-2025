"""
Сериализаторы Django REST Framework
"""
from rest_framework import serializers
from .models import KaspiStore, Product, Preorder


class KaspiStoreSerializer(serializers.ModelSerializer):
    """Сериализатор для магазина Kaspi"""
    products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = KaspiStore
        fields = [
            'id', 'created_at', 'updated_at', 'user_id', 'merchant_id',
            'name', 'api_key', 'products_count', 'last_sync', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'api_key']


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товара"""
    store_id = serializers.UUIDField(write_only=True, required=False)
    price_in_tenge = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'kaspi_product_id', 'kaspi_sku', 'store', 'store_id',
            'price', 'price_in_tenge', 'name', 'external_kaspi_id',
            'category', 'image_url', 'bot_active', 'last_check_time',
            'min_profit', 'max_profit', 'strategy', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        store_id = validated_data.pop('store_id', None)
        if store_id:
            validated_data['store'] = KaspiStore.objects.get(id=store_id)
        return super().create(validated_data)


class PreorderSerializer(serializers.ModelSerializer):
    """Сериализатор для предзаказа"""
    product_id = serializers.UUIDField(write_only=True, required=False)
    store_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Preorder
        fields = [
            'id', 'product', 'product_id', 'store', 'store_id',
            'article', 'name', 'brand', 'status', 'price',
            'warehouses', 'delivery_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id', None)
        store_id = validated_data.pop('store_id', None)
        if product_id:
            validated_data['product'] = Product.objects.get(id=product_id)
        if store_id:
            validated_data['store'] = KaspiStore.objects.get(id=store_id)
        return super().create(validated_data)

