"""
ViewSets для Django REST Framework
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from .models import KaspiStore, Product, Preorder
from .serializers import KaspiStoreSerializer, ProductSerializer, PreorderSerializer
from api.services.parser_service import run_async, parse_product_by_sku, sync_product
from api.services.sync_service import run_async as run_sync_async
from kaspi_auth.session_manager import SessionManager


class KaspiStoreViewSet(viewsets.ModelViewSet):
    """ViewSet для магазинов Kaspi"""
    queryset = KaspiStore.objects.all()
    serializer_class = KaspiStoreSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Фильтрация по user_id"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def sync(self, request, id=None):
        """Синхронизация магазина"""
        from api.services.sync_service import sync_store_api
        
        store = self.get_object()
        try:
            result = run_sync_async(sync_store_api(str(store.id)))
            return Response(result)
        except Exception as e:
            logger.error(f"Ошибка синхронизации магазина {store.id}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для товаров"""
    queryset = Product.objects.select_related('store').all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    filterset_fields = ['store', 'bot_active', 'category']
    search_fields = ['name', 'kaspi_product_id', 'kaspi_sku']
    ordering_fields = ['created_at', 'price', 'name']
    
    @action(detail=False, methods=['post'])
    def offers_by_product(self, request):
        """Получение офферов по SKU товара"""
        from decimal import Decimal
        
        sku = request.data.get('sku')
        if not sku:
            raise ValidationError('sku обязателен')
        
        try:
            offers = run_async(parse_product_by_sku(sku))
            return Response({
                'success': True,
                'data': offers
            })
        except Exception as e:
            logger.error(f"Ошибка при получении офферов: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_price(self, request):
        """Обновление цены товара"""
        from decimal import Decimal
        
        product_id = request.data.get('product_id')
        price = request.data.get('price')
        
        if not all([product_id, price]):
            raise ValidationError('product_id и price обязательны')
        
        try:
            product = Product.objects.get(id=product_id)
            session_manager = SessionManager(shop_uid=str(product.store_id))
            if not session_manager.load():
                return Response({
                    'success': False,
                    'error': 'Сессия истекла'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            cookies = session_manager.get_cookies()
            merchant_id = session_manager.merchant_uid
            
            result = run_async(sync_product(
                str(product_id),
                Decimal(price),
                cookies,
                merchant_id,
                product.kaspi_product_id
            ))
            
            if result.get('success'):
                product.price = int(Decimal(price) * 100)  # Конвертируем в тиыны
                product.save()
            
            return Response({
                'success': True,
                'data': result
            })
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Товар не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка при обновлении цены: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_enable(self, request):
        """Массовое включение товаров"""
        store_id = request.data.get('store_id')
        product_ids = request.data.get('product_ids', [])
        
        if not store_id or not product_ids:
            raise ValidationError('store_id и product_ids обязательны')
        
        updated = Product.objects.filter(
            store_id=store_id,
            kaspi_product_id__in=product_ids
        ).update(bot_active=True)
        
        return Response({
            'success': True,
            'updated_count': updated,
            'message': f'Включено товаров: {updated}'
        })
    
    @action(detail=False, methods=['post'])
    def batch_disable(self, request):
        """Массовое отключение товаров"""
        store_id = request.data.get('store_id')
        product_ids = request.data.get('product_ids', [])
        
        if not store_id or not product_ids:
            raise ValidationError('store_id и product_ids обязательны')
        
        updated = Product.objects.filter(
            store_id=store_id,
            kaspi_product_id__in=product_ids
        ).update(bot_active=False)
        
        return Response({
            'success': True,
            'updated_count': updated,
            'message': f'Отключено товаров: {updated}'
        })


class PreorderViewSet(viewsets.ModelViewSet):
    """ViewSet для предзаказов"""
    queryset = Preorder.objects.select_related('product', 'store').all()
    serializer_class = PreorderSerializer
    lookup_field = 'id'
    filterset_fields = ['store', 'status']
    search_fields = ['name', 'article', 'brand']
    ordering_fields = ['created_at', 'status']
    
    def get_queryset(self):
        """Фильтрация по store_id"""
        queryset = super().get_queryset()
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def list_by_store(self, request):
        """Список предзаказов по магазину"""
        from preorders.services import fetch_preorders
        
        store_id = request.query_params.get('store_id')
        if not store_id:
            raise ValidationError('store_id обязателен')
        
        try:
            preorders = fetch_preorders(store_id)
            return Response({
                'success': True,
                'preorders': preorders
            })
        except Exception as e:
            logger.error(f"Ошибка при получении предзаказов: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Загрузка предзаказов на Kaspi"""
        from preorders.services import handle_upload_preorder
        
        store_id = request.data.get('store_id')
        if not store_id:
            raise ValidationError('store_id обязателен')
        
        try:
            handle_upload_preorder(store_id)
            return Response({
                'success': True,
                'message': f'Предзаказы для магазина {store_id} успешно загружены'
            })
        except Exception as e:
            logger.error(f"Ошибка при загрузке предзаказов: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_excel(self, request):
        """Генерация Excel файла с предзаказами"""
        from preorders.services import fetch_preorders, process_preorders_for_excel, generate_preorder_xlsx
        
        store_id = request.data.get('store_id')
        if not store_id:
            raise ValidationError('store_id обязателен')
        
        try:
            preorders_data = fetch_preorders(store_id)
            if not preorders_data:
                return Response({
                    'success': False,
                    'error': 'Нет предзаказов для генерации Excel файла'
                })
            
            processed_data = process_preorders_for_excel(preorders_data)
            filepath = generate_preorder_xlsx(processed_data, store_id)
            
            return Response({
                'success': True,
                'filepath': filepath,
                'message': 'Excel файл успешно сгенерирован'
            })
        except Exception as e:
            logger.error(f"Ошибка при генерации Excel: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

