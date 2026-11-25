"""
Production settings.

Activated by setting on your server:
    export DJANGO_SETTINGS_MODULE=config.settings.production

What's different from development:
  - DEBUG = False  → no stack traces exposed to users
  - PostgreSQL instead of SQLite (more robust, supports multiple server processes)
  - Strict CORS — only whitelisted origins allowed
  - Security headers enforced (HTTPS, XSS protection, etc.)
"""
from decouple import Csv, config

from .base import *  # noqa: F401, F403

# NEVER True in production — exposes internal errors to attackers
DEBUG = False

# Only requests to these exact domains are accepted
# Example: ALLOWED_HOSTS=api.myapp.com,www.myapp.com
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# ─── DATABASE ─────────────────────────────────────────────────────────────────
# PostgreSQL is used in production because:
#   - Handles multiple concurrent writes (SQLite has locking issues with multiple workers)
#   - Better performance for large datasets
#   - Supports advanced features (JSON fields, full-text search)
#
# Set these in your server's environment variables (never hardcode):
#   DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        # Keep database connections alive for 60s — avoids overhead of creating
        # a new connection for every single request
        'CONN_MAX_AGE': 60,
    }
}

# ─── SECURITY HEADERS ─────────────────────────────────────────────────────────
# These tell the browser how to handle your site securely.
# They are added to every HTTP response as headers.

# Prevents browsers from sniffing a file's content-type (defense against MIME attacks)
SECURE_CONTENT_TYPE_NOSNIFF = True

# Prevents your site from being embedded in an <iframe> (defense against clickjacking)
X_FRAME_OPTIONS = 'DENY'

# HSTS: tells browsers to ONLY use HTTPS for this domain for the next year
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session and CSRF cookies only sent over HTTPS connections
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
