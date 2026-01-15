"""
Views для аутентификации Kaspi
"""
import secrets
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from api.models import KaspiStore
from kaspi_auth.kaspi_auth_service import run_async, login_and_get_merchant_info
from kaspi_auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class KaspiAuthViewSet(viewsets.ViewSet):
    """ViewSet для аутентификации в Kaspi"""
    
    @action(detail=False, methods=['post'])
    def authenticate(self, request):
        """
        Аутентификация в Kaspi и привязка магазина
        POST /api/v1/kaspi/auth/authenticate/
        Body: {
            "user_id": "uuid",
            "email": "email@example.com",
            "password": "password"
        }
        """
        user_id = request.data.get('user_id')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([user_id, email, password]):
            raise ValidationError('user_id, email и password обязательны')
        
        try:
            # Аутентификация в Kaspi
            cookies, merchant_uid, shop_name, guid = run_async(
                login_and_get_merchant_info(email, password, user_id)
            )
            
            if not merchant_uid:
                return Response({
                    'success': False,
                    'error': 'Ошибка аутентификации в Kaspi'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Проверяем существующий магазин
            try:
                existing_store = KaspiStore.objects.get(
                    user_id=user_id,
                    merchant_id=merchant_uid
                )
                
                # Обновляем сессию
                existing_store.guid = guid
                existing_store.name = shop_name
                existing_store.last_login = timezone.now()
                existing_store.last_sync = None
                existing_store.save()
                
                return Response({
                    'success': True,
                    'store_id': str(existing_store.id),
                    'name': existing_store.name,
                    'message': 'Сессия магазина успешно обновлена',
                    'api_key': existing_store.api_key,
                    'is_replaced': True
                })
                
            except KaspiStore.DoesNotExist:
                # Создаем новый магазин
                store = KaspiStore.objects.create(
                    user_id=user_id,
                    merchant_id=merchant_uid,
                    name=shop_name,
                    api_key=f"kaspi_{secrets.token_urlsafe(16)}",
                    guid=guid,
                    last_login=timezone.now()
                )
                
                return Response({
                    'success': True,
                    'store_id': str(store.id),
                    'name': store.name,
                    'message': 'Магазин успешно привязан к вашему аккаунту',
                    'api_key': store.api_key,
                    'is_replaced': False
                })
                
        except Exception as e:
            logger.error(f"Ошибка при привязке магазина: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Ошибка при подключении к Kaspi: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def sms_start(self, request):
        """Начало SMS авторизации"""
        from kaspi_auth.sms_auth_service import run_async, sms_login_start
        
        user_id = request.data.get('user_id')
        phone = request.data.get('phone')
        
        if not all([user_id, phone]):
            raise ValidationError('user_id и phone обязательны')
        
        try:
            session_id = run_async(sms_login_start(user_id, phone))
            return Response({'session_id': session_id})
        except Exception as e:
            logger.error(f"Ошибка SMS авторизации (start): {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def sms_verify(self, request):
        """Проверка SMS кода"""
        from kaspi_auth.sms_auth_service import run_async, sms_login_verify
        from api.models import KaspiStore
        import secrets
        
        user_id = request.data.get('user_id')
        session_id = request.data.get('session_id')
        code = request.data.get('code')
        
        if not all([user_id, session_id, code]):
            raise ValidationError('user_id, session_id и code обязательны')
        
        try:
            cookies, merchant_uid, shop_name, guid = run_async(
                sms_login_verify(session_id, user_id, code)
            )
            
            # Проверяем существующий магазин
            try:
                existing_store = KaspiStore.objects.get(
                    user_id=user_id,
                    merchant_id=merchant_uid
                )
                
                existing_store.guid = guid
                existing_store.name = shop_name
                existing_store.last_login = timezone.now()
                existing_store.save()
                
                return Response({
                    'success': True,
                    'store_id': str(existing_store.id),
                    'message': 'Сессия магазина успешно обновлена через SMS',
                    'is_replaced': True
                })
            except KaspiStore.DoesNotExist:
                # Создаем новый магазин
                store = KaspiStore.objects.create(
                    user_id=user_id,
                    merchant_id=merchant_uid,
                    name=shop_name,
                    api_key=f"kaspi_{secrets.token_urlsafe(16)}",
                    guid=guid,
                    last_login=timezone.now()
                )
                
                return Response({
                    'success': True,
                    'store_id': str(store.id),
                    'message': 'Магазин успешно привязан через SMS',
                    'is_replaced': False
                })
                
        except Exception as e:
            logger.error(f"Ошибка SMS авторизации (verify): {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

