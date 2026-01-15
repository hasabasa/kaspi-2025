"""
Health check views
"""
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone


def health_check(request):
    """Проверка состояния сервиса"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'cors_enabled': True,
    })


def health_db(request):
    """Проверка подключения к БД"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        from .models import KaspiStore
        stores_count = KaspiStore.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'mode': 'postgresql',
            'stores_count': stores_count,
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)

