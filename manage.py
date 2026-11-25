#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Usage:
  python manage.py runserver        — start the development server
  python manage.py makemigrations   — generate migration files after changing models
  python manage.py migrate          — apply migrations to the database
  python manage.py createsuperuser  — create an admin user
"""
import os
import sys


def main():
    # Default to development settings unless DJANGO_ENV is set
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and your "
            "virtual environment is activated."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
