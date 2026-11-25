"""
Models define the database tables for this application.

Each Python class here becomes one SQL table.
Each class attribute (CharField, TextField, etc.) becomes one column.

When you change a model, run:
    python manage.py makemigrations   ← generates a migration file
    python manage.py migrate          ← applies changes to the database
"""
from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    """
    Represents a document created or uploaded by a user.
    Django creates the SQL table 'api_document' (app_name + model_name, lowercase).

    A document can be:
      - Text-only: title + content, no file
      - File upload: title + content + file (pdf, txt, docx)
    """

    # CharField: short text with a maximum length.
    # max_length=255 is a common convention for titles/names.
    title = models.CharField(max_length=255)

    # TextField: long text with no length limit.
    # Stored as TEXT in SQLite/PostgreSQL.
    # blank=True: the content can be empty (e.g., if only a file is uploaded)
    content = models.TextField(blank=True, default='')

    # FileField: stores the FILE PATH as a string in the database.
    # The actual file bytes are saved to disk at: MEDIA_ROOT/documents/<filename>
    # null=True, blank=True: file is optional — text-only documents are valid
    # upload_to='documents/': files are saved inside the media/documents/ folder
    file = models.FileField(upload_to='documents/', null=True, blank=True)

    # DateTimeField with auto_now_add=True:
    # Automatically set to the current date+time when this record is FIRST created.
    # You can never change it after creation — it is read-only.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # ForeignKey: a link from this table to the User table.
    # Every document is owned by exactly one user.
    # on_delete=CASCADE: if the User is deleted, all their documents are deleted too.
    # related_name='documents': lets you do user.documents.all() to get all docs for a user.
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
    )

    class Meta:
        # Default sort order for queries: newest documents appear first.
        # The '-' prefix means descending order.
        ordering = ['-uploaded_at']

    def __str__(self):
        # This controls what Django shows in the admin panel for this object.
        return self.title


class QueryLog(models.Model):
    """
    Tracks every query a user submits.
    Maps to the SQL table 'api_querylog'.

    In a real AI-powered app, this stores both the user's question
    and the AI's answer summary.
    """

    # The question/search text the user submitted
    query_text = models.TextField()

    # The system's answer or summary (blank until the query is processed)
    result_summary = models.TextField(blank=True, default='')

    # Automatically set to current time when the query is first saved
    created_at = models.DateTimeField(auto_now_add=True)

    # Which user made this query
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='query_logs',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        # Truncate long query text for readability in the admin panel
        preview = self.query_text[:50] + '...' if len(self.query_text) > 50 else self.query_text
        return f"Query by {self.user.username}: {preview}"


class UserSession(models.Model):
    """
    Tracks active user sessions with custom expiry times.
    Maps to the SQL table 'api_usersession'.

    Note: DRF's built-in Token model already handles token storage for auth.
    This model provides additional session metadata like expiry timestamps
    (useful for implementing "remember me for 30 days" features).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_sessions',
    )

    # A session identifier — could be used for custom session management
    token = models.CharField(max_length=255)

    # When this session was created (automatically set)
    created_at = models.DateTimeField(auto_now_add=True)

    # When this session expires — set explicitly when creating a session.
    # Unlike DRF tokens (which never expire), this allows time-limited sessions.
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session for {self.user.username} (expires {self.expires_at})"
