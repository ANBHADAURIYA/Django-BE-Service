"""
URL patterns for the api app.

These are included by config/urls.py with no prefix, so:
  path('documents', ...)      → matches  GET/POST /documents
  path('documents/<int:pk>',) → matches  GET/DELETE /documents/42
  path('query', ...)          → matches  POST /query
  path('queries', ...)        → matches  GET /queries
  path('auth/register', ...)  → matches  POST /auth/register
  path('auth/login', ...)     → matches  POST /auth/login

How URL patterns work:
  - path('documents', view)        matches EXACT path /documents
  - path('documents/<int:pk>', ..) matches /documents/1, /documents/42, etc.
    The <int:pk> part captures the number and passes it to the view as pk=42

.as_view() converts a class-based view into a function that Django can call.
The name= parameter is optional — it lets you reverse URLs by name in code.
"""
from django.urls import path

from .views import (
    DocumentDetailView,
    DocumentListCreateView,
    LoginView,
    QueryCreateView,
    QueryListView,
    RegisterView,
)

urlpatterns = [
    # ── Authentication (no token required) ───────────────────────────────────
    path('auth/register', RegisterView.as_view(), name='auth-register'),
    path('auth/login', LoginView.as_view(), name='auth-login'),

    # ── Documents ─────────────────────────────────────────────────────────────
    # GET + POST on the collection URL /documents
    path('documents', DocumentListCreateView.as_view(), name='document-list-create'),

    # GET + DELETE on the item URL /documents/<id>
    # <int:pk> captures the numeric ID from the URL
    path('documents/<int:pk>', DocumentDetailView.as_view(), name='document-detail'),

    # ── Queries ───────────────────────────────────────────────────────────────
    # POST to submit a new query
    path('query', QueryCreateView.as_view(), name='query-create'),

    # GET to list query history
    path('queries', QueryListView.as_view(), name='query-list'),
]
