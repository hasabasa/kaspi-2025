"""
Health check URLs
"""
from django.urls import path
from .health_views import health_check, health_db

urlpatterns = [
    path('', health_check, name='health'),
    path('db/', health_db, name='health_db'),
]

