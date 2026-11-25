"""
Base settings — shared by ALL environments (development and production).

development.py and production.py both start with:
    from .base import *
Then they override only what differs between environments.

Think of this as the "template" that both environments fill in.
"""
from pathlib import Path

from decouple import Csv, config

# ─── BASE DIRECTORY ──────────────────────────────────────────────────────────
# BASE_DIR = Django-BE-Service/ (the project root)
# We calculate it by going up 3 parent levels from this file:
#   base.py -> settings/ -> config/ -> Django-BE-Service/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── SECURITY ────────────────────────────────────────────────────────────────
# SECRET_KEY is read from the .env file — never hardcoded here.
# python-decouple will raise an error if SECRET_KEY is not in .env.
# This forces developers to always set it explicitly.
SECRET_KEY = config('SECRET_KEY')

# ─── INSTALLED APPS ──────────────────────────────────────────────────────────
# This list tells Django which features/apps are active.
# Each string maps to an app's apps.py AppConfig or just the app directory.
INSTALLED_APPS = [
    # Django's built-in apps (always needed)
    'django.contrib.admin',         # The /admin web interface
    'django.contrib.auth',          # User model, login, password hashing
    'django.contrib.contenttypes',  # Needed by auth and other Django internals
    'django.contrib.sessions',      # Session framework
    'django.contrib.messages',      # One-time flash messages
    'django.contrib.staticfiles',   # Static file (CSS/JS) management

    # Third-party apps
    'rest_framework',               # Django REST Framework — our entire API layer
    'rest_framework.authtoken',     # DRF's Token model (creates the authtoken_token table)
    'corsheaders',                  # Adds CORS headers so browsers can call this API

    # Our app — where our models, views, and serializers live
    'api',
]

# ─── MIDDLEWARE ───────────────────────────────────────────────────────────────
# Middleware = code that runs on EVERY request and response (like a pipeline).
# IMPORTANT: Order matters! Each middleware wraps all those below it.
# CorsMiddleware MUST be before CommonMiddleware to handle preflight (OPTIONS) requests.
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # CORS — first!
    'django.middleware.security.SecurityMiddleware',  # Security headers + HTTPS redirect
    'whitenoise.middleware.WhiteNoiseMiddleware',      # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Reads session, sets request.user
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ─── PASSWORD VALIDATION ─────────────────────────────────────────────────────
# Django validates passwords against these rules automatically.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNATIONALIZATION ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True  # Store all datetimes as UTC — prevents timezone confusion

# ─── STATIC FILES ─────────────────────────────────────────────────────────────
# Static files = CSS, JS, images bundled WITH the app (not user uploads).
# collectstatic gathers them all to STATIC_ROOT for production serving.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise compresses and fingerprints static files for production caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── MEDIA FILES ──────────────────────────────────────────────────────────────
# Media files = files uploaded by users (documents, images).
# Django stores the FILE PATH in the DB; the actual bytes go in MEDIA_ROOT.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── DJANGO REST FRAMEWORK ────────────────────────────────────────────────────
# Global defaults for every API view.
# Individual views can override these with permission_classes = [...] on the class.
REST_FRAMEWORK = {
    # How DRF identifies "who is making this request"
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    # Every endpoint requires a valid token UNLESS the view overrides this
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Paginate all list endpoints automatically
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardResultsPagination',
    'PAGE_SIZE': 10,
}

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Which browser origins (domains) are allowed to call this API.
# Without this, browsers block requests from frontend apps on other domains.
# development.py sets CORS_ALLOW_ALL_ORIGINS = True for convenience.
# production.py uses CORS_ALLOWED_ORIGINS to whitelist specific domains.
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000',
    cast=Csv(),
)

# ─── FILE UPLOAD LIMITS ───────────────────────────────────────────────────────
# Read from .env — defaults to 10 MB if not set.
MAX_UPLOAD_SIZE_MB = config('MAX_UPLOAD_SIZE_MB', default=10, cast=int)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Comma-separated list of allowed file extensions (without the dot)
ALLOWED_UPLOAD_EXTENSIONS = set(
    config('ALLOWED_FILE_TYPES', default='pdf,txt,docx,doc', cast=Csv())
)

# Django rejects request bodies larger than this BEFORE they reach our view.
# Adding a small buffer (1 MB) to allow for form field overhead alongside the file.
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_BYTES + (1 * 1024 * 1024)
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_BYTES
