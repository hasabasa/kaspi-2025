"""
URL configuration для Kaspi Backend
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Импортируем ViewSets (создадим позже)
from api.views import KaspiStoreViewSet, ProductViewSet, PreorderViewSet
from kaspi_auth.views import KaspiAuthViewSet

# Создаем роутер для API
router = DefaultRouter()
router.register(r'kaspi/stores', KaspiStoreViewSet, basename='kaspi-stores')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'preorders', PreorderViewSet, basename='preorders')
router.register(r'kaspi/auth', KaspiAuthViewSet, basename='kaspi-auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('health/', include('api.health_urls')),
]

