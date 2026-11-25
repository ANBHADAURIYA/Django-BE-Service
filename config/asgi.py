"""
ASGI entry point for async deployment (WebSockets, HTTP/2).
Included for future-proofing — this project uses WSGI/gunicorn in production.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
