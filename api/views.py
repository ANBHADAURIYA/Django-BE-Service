"""
Views contain the business logic for every API endpoint.

Each class handles ONE URL pattern.
Each method inside a class handles ONE HTTP verb (GET, POST, DELETE).

Flow for every request:
  1. URL router calls the right view class
  2. DRF checks authentication (token valid?) and permission (user logged in?)
  3. The view method runs your logic
  4. Serializer validates input or formats output
  5. View returns a Response (JSON + HTTP status code)
"""
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document, QueryLog
from .pagination import StandardResultsPagination
from .serializers import (
    DocumentSerializer,
    LoginSerializer,
    QueryLogSerializer,
    RegisterSerializer,
)


# ─── AUTH VIEWS ───────────────────────────────────────────────────────────────
# These two views are PUBLIC — they don't require an existing token.
# That's why we set permission_classes = [AllowAny], which overrides
# the global default of IsAuthenticated defined in settings.

class RegisterView(APIView):
    """
    POST /auth/register

    Creates a new user account and returns a token.

    Request body:
        {"username": "alice", "email": "alice@example.com",
         "password": "mypassword123", "password_confirm": "mypassword123"}

    Success response (HTTP 201):
        {"message": "User registered successfully.", "token": "abc...xyz", "username": "alice"}

    Error response (HTTP 400):
        {"password_confirm": ["Passwords do not match."]}
    """
    # AllowAny: anyone can call this endpoint, no token needed.
    # You can't require a token to register — the user doesn't have one yet!
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            # get_or_create returns (token_object, created_boolean)
            # For a brand-new user, the token is always created fresh here.
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'message': 'User registered successfully.',
                    'token': token.key,       # 40-character random string
                    'username': user.username,
                },
                status=status.HTTP_201_CREATED,
            )

        # serializer.errors contains field-level validation errors, e.g.:
        # {"username": ["A user with that username already exists."]}
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /auth/login

    Authenticates a user and returns their token.

    Request body:
        {"username": "alice", "password": "mypassword123"}

    Success response (HTTP 200):
        {"token": "abc...xyz", "username": "alice"}

    Error response (HTTP 401):
        {"error": "Invalid username or password."}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # authenticate() checks the username + password against the database.
        # It handles password hashing internally — you never compare passwords directly.
        # Returns the User object if valid, None if the credentials are wrong.
        user = authenticate(
            request=request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

        if user is None:
            # Security note: don't reveal WHETHER the username exists.
            # "Invalid username or password" (not "username not found") prevents
            # attackers from enumerating valid usernames.
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # get_or_create: if a token exists for this user, return it.
        # This ensures the same token is returned on every login.
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'username': user.username,
            },
            status=status.HTTP_200_OK,
        )


# ─── DOCUMENT VIEWS ───────────────────────────────────────────────────────────

class DocumentListCreateView(APIView):
    """
    GET  /documents    — List the authenticated user's documents (paginated)
    POST /documents    — Create a new document (JSON body or file upload)

    parser_classes tells DRF which Content-Type headers this view accepts:
      - JSONParser:      Content-Type: application/json  (title + content as JSON)
      - MultiPartParser: Content-Type: multipart/form-data  (file upload)
      - FormParser:      Content-Type: application/x-www-form-urlencoded
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """
        Returns the authenticated user's documents, paginated.

        .filter(owner=request.user) is crucial — it ensures users ONLY see
        their own documents, never documents belonging to other users.

        DRF sets request.user automatically from the Authorization token header.
        """
        queryset = Document.objects.filter(owner=request.user)

        # Paginator slices the queryset based on ?page and ?page_size params
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)

        # many=True: serialize a LIST of objects (not just one)
        serializer = DocumentSerializer(page, many=True)

        # get_paginated_response wraps results in {count, next, previous, results}
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Creates a new document.

        Handles two types of requests:
          1. JSON body:  {"title": "My Doc", "content": "Hello world"}
          2. Multipart:  title + content fields + optional file attachment

        File validation has two layers:
          - Layer 1 (here): file SIZE → returns HTTP 413 specifically
          - Layer 2 (serializer): file TYPE → returns HTTP 400
        """
        # ── Layer 1: File size check (must happen BEFORE serializer validation) ──
        # We check here — not in the serializer — because HTTP 413 is a specific
        # status code for "entity too large" that serializers can't return directly.
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            max_bytes = getattr(settings, 'MAX_UPLOAD_SIZE_BYTES', 10 * 1024 * 1024)
            if uploaded_file.size > max_bytes:
                max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 10)
                return Response(
                    {'error': f'File size exceeds the {max_mb} MB limit.'},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )

        # ── Layer 2: Serializer validation (types, required fields, etc.) ──────
        # request.data contains both JSON fields AND multipart form fields.
        serializer = DocumentSerializer(data=request.data)

        if serializer.is_valid():
            # owner=request.user: set the owner from the authenticated user.
            # The client cannot forge this — it comes from the token, not the request body.
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentDetailView(APIView):
    """
    GET    /documents/{id}  — Retrieve a single document
    DELETE /documents/{id}  — Delete a document

    Both require the requesting user to OWN the document.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Returns a single document.

        Returns 404 if the document doesn't exist OR belongs to another user.
        We intentionally don't distinguish these two cases — revealing that a
        document exists but belongs to someone else is an information leak.
        """
        try:
            # filter by BOTH pk AND owner — if either fails, we get 404
            document = Document.objects.get(pk=pk, owner=request.user)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Deletes a document.

        Status code logic (as required by the assignment):
          - 404: document doesn't exist at all
          - 403: document exists but belongs to a different user
          - 204: successfully deleted (No Content — empty response body)

        Why 403 here (not 404): The assignment explicitly requires 403 for
        "not owner" case to distinguish it from "not found."
        """
        try:
            # Look up the document regardless of owner — we need to check ownership
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if document.owner != request.user:
            return Response(
                {'error': 'You do not have permission to delete this document.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        document.delete()
        # HTTP 204 No Content: success, but nothing to return in the body.
        # By convention, DELETE responses have no body.
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── QUERY VIEWS ──────────────────────────────────────────────────────────────

class QueryCreateView(APIView):
    """
    POST /query

    Creates a new QueryLog entry.

    Request body:  {"query_text": "What documents do I have about Django?"}
    Response (HTTP 201):
        {"id": 1, "query_text": "...", "result_summary": "", "created_at": "...", "user": "alice"}

    In a real AI-powered app, this is where you'd call your AI/search service
    to generate a result_summary before saving.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QueryLogSerializer(data=request.data)

        if serializer.is_valid():
            # In a real app: result = call_ai_service(request.data['query_text'])
            # For now, we save with an empty result_summary (can be updated later).
            query_log = serializer.save(user=request.user)
            # Re-serialize to include all read-only fields (id, created_at, user)
            return Response(
                QueryLogSerializer(query_log).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QueryListView(APIView):
    """
    GET /queries

    Returns the authenticated user's query history, paginated.

    Same pattern as DocumentListCreateView.get() — paginator + filter by user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = QueryLog.objects.filter(user=request.user)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = QueryLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
