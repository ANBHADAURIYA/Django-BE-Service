"""
Root URL configuration for the entire Django project.

Every HTTP request starts here. This file delegates groups of URLs
to individual apps using include().

Think of it as the main switchboard:
  - /admin/ → Django's built-in admin interface
  - /auth/  → Registration and login (in api/urls.py)
  - /       → All document and query endpoints (in api/urls.py)
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django's built-in admin panel
    # Visit http://localhost:8000/admin/ and log in with your superuser account
    path('admin/', admin.site.urls),

    # All API endpoints — delegated to api/urls.py
    # include() means: "strip the prefix and pass the rest to that app's urls.py"
    path('', include('api.urls')),
]

# In development ONLY: let Django's dev server serve uploaded media files.
# In production, your web server (nginx) or cloud storage (S3) handles this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
