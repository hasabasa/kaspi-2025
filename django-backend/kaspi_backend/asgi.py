"""
ASGI config для Kaspi Backend
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaspi_backend.settings')

application = get_asgi_application()

