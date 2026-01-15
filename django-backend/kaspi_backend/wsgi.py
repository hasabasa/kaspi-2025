"""
WSGI config для Kaspi Backend
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaspi_backend.settings')

application = get_wsgi_application()

