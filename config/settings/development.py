"""
Development settings.

Activated by default via manage.py:
    DJANGO_SETTINGS_MODULE=config.settings.development (the default)

What's different from production:
  - DEBUG = True  → shows detailed error pages with stack traces
  - SQLite database → no installation needed, creates db.sqlite3 automatically
  - CORS_ALLOW_ALL_ORIGINS = True → allows any frontend to call this API locally
"""
from decouple import Csv, config

from .base import *  # noqa: F401, F403 — imports ALL settings from base.py

# Show full error pages with stack traces (NEVER use in production)
DEBUG = True

# In development, accept requests from localhost and 127.0.0.1
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ─── DATABASE ─────────────────────────────────────────────────────────────────
# SQLite stores everything in a single file (db.sqlite3).
# Perfect for local development — no server needed, Django creates it automatically.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Allow any browser origin to call this API during development.
# This means your React app at localhost:3000 can freely talk to this server.
CORS_ALLOW_ALL_ORIGINS = True
