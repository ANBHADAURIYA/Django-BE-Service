"""
WSGI entry point for production deployment.

Gunicorn uses this file:
    gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000

WSGI = Web Server Gateway Interface — the standard way Python web apps
talk to production web servers.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
