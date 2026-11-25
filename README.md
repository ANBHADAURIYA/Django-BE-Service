# Django Backend Service

A production-ready REST API built with Django and Django REST Framework (DRF).  
Supports document management, query logging, paginated lists, file uploads, and token-based authentication.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Reference](#api-reference)
- [Testing Guide](#testing-guide)
- [Production Deployment](#production-deployment)

---

## Features

- Token-based authentication (register, login, protected endpoints)
- Full CRUD for Documents — JSON body or file upload
- File validation — allowed types (pdf, txt, docx, doc) and max size (10 MB, returns HTTP 413)
- Paginated list endpoints — `count`, `next`, `previous`, `results`
- Query logging — record and retrieve query history
- Owner-only access — users can only see/delete their own data
- Split settings — separate configs for development and production
- CORS support via `django-cors-headers`
- Static file serving via `whitenoise`
- Production-grade server via `gunicorn`

---

## Tech Stack

| Package | Purpose |
|---------|---------|
| Django 4.2 | Web framework |
| Django REST Framework | API layer (serializers, views, token auth) |
| python-decouple | Reads secrets from `.env` — no hardcoded credentials |
| django-cors-headers | Allows frontend apps on other domains to call this API |
| whitenoise | Serves static files in production without nginx |
| gunicorn | Production WSGI server |
| SQLite (dev) / PostgreSQL (prod) | Database |

---

## Project Structure

```
Django-BE-Service/
│
├── manage.py                      ← Django CLI (runserver, migrate, etc.)
├── requirements.txt               ← All Python dependencies
├── .env.example                   ← Template for environment variables
├── .gitignore
│
├── config/                        ← Django project configuration
│   ├── settings/
│   │   ├── base.py                ← Settings shared by all environments
│   │   ├── development.py         ← Dev: SQLite, DEBUG=True, open CORS
│   │   └── production.py          ← Prod: PostgreSQL, DEBUG=False, security headers
│   ├── urls.py                    ← Root URL router
│   ├── wsgi.py                    ← Production server entry point (gunicorn)
│   └── asgi.py                    ← Async server entry point
│
├── api/                           ← Main application
│   ├── models.py                  ← Database models: Document, QueryLog, UserSession
│   ├── serializers.py             ← JSON ↔ Python validation and conversion
│   ├── views.py                   ← Request handlers (business logic)
│   ├── urls.py                    ← URL patterns for all endpoints
│   ├── pagination.py              ← Custom pagination (count/next/previous/results)
│   └── migrations/                ← Auto-generated database schema changes
│
└── media/                         ← Uploaded files stored here (not committed to git)
```

---

## Local Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd Django-BE-Service
```

### Step 2 — Create and activate a virtual environment

A virtual environment isolates this project's packages from your global Python installation.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt. Run this activation command every time you open a new terminal.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set a unique `SECRET_KEY`. Generate one with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5 — Create the database

```bash
python manage.py migrate
```

This creates `db.sqlite3` with all required tables.

### Step 6 — (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

Visit `http://127.0.0.1:8000/admin/` to manage users and data via Django's built-in admin panel.

---

## Environment Variables

Copy `.env.example` to `.env`. Never commit `.env` to git.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | Django secret key — generate a random one |
| `DEBUG` | No | `True` | `True` for dev, `False` for production |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated hostnames |
| `MAX_UPLOAD_SIZE_MB` | No | `10` | Maximum file upload size in megabytes |
| `ALLOWED_FILE_TYPES` | No | `pdf,txt,docx,doc` | Comma-separated allowed file extensions |
| `CORS_ALLOW_ALL_ORIGINS` | No | `True` (dev) | Set `False` in production |
| `CORS_ALLOWED_ORIGINS` | No | — | Comma-separated allowed frontend origins |

**Production-only variables** (only needed with `production.py` settings):

| Variable | Description |
|----------|-------------|
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host (default: `localhost`) |
| `DB_PORT` | PostgreSQL port (default: `5432`) |

---

## Running the Server

### Development

```bash
python manage.py runserver
# Server starts at http://127.0.0.1:8000/
```

### Production (gunicorn)

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

---

## API Reference

### Base URL

```
http://127.0.0.1:8000
```

### Authentication

All endpoints except **register** and **login** require a token in the `Authorization` header:

```
Authorization: Token <your-token-here>
```

You receive a token when you register or log in.

---

### Auth Endpoints

#### `POST /auth/register`

Create a new user account. Returns a token immediately.

**Request body:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "mypassword123",
  "password_confirm": "mypassword123"
}
```

**Success — HTTP 201:**
```json
{
  "message": "User registered successfully.",
  "token": "298d84224c7eedd622f7da2e695190d19b821de4",
  "username": "alice"
}
```

**Error — HTTP 400** (e.g., username taken):
```json
{
  "username": ["A user with that username already exists."]
}
```

---

#### `POST /auth/login`

Authenticate and retrieve your token.

**Request body:**
```json
{
  "username": "alice",
  "password": "mypassword123"
}
```

**Success — HTTP 200:**
```json
{
  "token": "298d84224c7eedd622f7da2e695190d19b821de4",
  "username": "alice"
}
```

**Error — HTTP 401:**
```json
{
  "error": "Invalid username or password."
}
```

---

### Document Endpoints

#### `POST /documents`

Create a document. Supports two modes:

**Mode 1 — JSON body:**
```
Content-Type: application/json
Authorization: Token <token>

{"title": "My Doc", "content": "Some text content here."}
```

**Mode 2 — File upload (multipart):**
```
Content-Type: multipart/form-data
Authorization: Token <token>

title: My PDF Doc
content: Description of the file
file: <file attachment>
```

**Success — HTTP 201:**
```json
{
  "id": 1,
  "title": "My Doc",
  "content": "Some text content here.",
  "file": null,
  "uploaded_at": "2026-11-24T09:00:00Z",
  "owner": "alice"
}
```

**Errors:**
- `HTTP 400` — missing required field or invalid file type
- `HTTP 413` — file exceeds the 10 MB size limit
- `HTTP 401` — no token provided

---

#### `GET /documents`

List your documents, paginated.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 10 | Records per page (max 100) |

**Example:** `GET /documents?page=1&page_size=5`

**Success — HTTP 200:**
```json
{
  "count": 42,
  "next": "http://127.0.0.1:8000/documents?page=2&page_size=5",
  "previous": null,
  "results": [
    {
      "id": 3,
      "title": "My Doc",
      "content": "...",
      "file": null,
      "uploaded_at": "2026-11-24T09:00:00Z",
      "owner": "alice"
    }
  ]
}
```

---

#### `GET /documents/{id}`

Retrieve a single document by ID.

**Success — HTTP 200:** returns the document object.

**Errors:**
- `HTTP 404` — document not found, or belongs to a different user

---

#### `DELETE /documents/{id}`

Delete a document.

**Success — HTTP 204:** empty response body.

**Errors:**
- `HTTP 404` — document does not exist
- `HTTP 403` — document exists but you are not the owner

---

### Query Endpoints

#### `POST /query`

Log a new query.

**Request body:**
```json
{
  "query_text": "What documents do I have about Django?"
}
```

**Success — HTTP 201:**
```json
{
  "id": 1,
  "query_text": "What documents do I have about Django?",
  "result_summary": "",
  "created_at": "2026-11-24T09:00:00Z",
  "user": "alice"
}
```

---

#### `GET /queries`

List your query history, paginated. Same `page` and `page_size` parameters as `/documents`.

**Success — HTTP 200:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [...]
}
```

---

### HTTP Status Code Reference

| Code | Meaning | When it occurs |
|------|---------|----------------|
| 200 | OK | Successful GET |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Missing field, invalid file type, validation error |
| 401 | Unauthorized | No token or invalid credentials |
| 403 | Forbidden | You are authenticated but do not own the resource |
| 404 | Not Found | Resource does not exist or does not belong to you |
| 413 | Request Entity Too Large | Uploaded file exceeds the size limit |

---

## Testing Guide

### Option A — Postman (Recommended for beginners)

Postman is a GUI tool for testing APIs. Download it at [postman.com](https://www.postman.com/downloads/).

**Setup steps:**

1. Open Postman and create a new **Collection** called `Django Backend Service`.

2. Create a **Collection Variable** called `token` (leave value empty for now).

3. Add a **register** request:
   - Method: `POST`
   - URL: `http://127.0.0.1:8000/auth/register`
   - Body → raw → JSON:
     ```json
     {
       "username": "alice",
       "email": "alice@example.com",
       "password": "mypassword123",
       "password_confirm": "mypassword123"
     }
     ```
   - In the **Tests** tab, add this script to auto-save your token:
     ```javascript
     const response = pm.response.json();
     pm.collectionVariables.set("token", response.token);
     ```

4. For all other requests, add this **Authorization** header:
   ```
   Key:   Authorization
   Value: Token {{token}}
   ```

5. Run requests in this order:
   - Register → Login → POST /documents → GET /documents → GET /documents/1 → DELETE /documents/1 → POST /query → GET /queries

**Testing file upload in Postman:**
- Set method to `POST`, URL to `http://127.0.0.1:8000/documents`
- Body → **form-data** (not raw JSON)
- Add keys: `title` (text), `content` (text), `file` (change type to **File** in the dropdown)
- Attach a `.pdf` or `.txt` file

**Testing file size rejection (413):**
- Create a file larger than 10 MB and upload it — you should get `HTTP 413`

**Testing file type rejection (400):**
- Upload a `.exe` or `.jpg` file — you should get `HTTP 400` with an error message

---

### Option B — curl (Command Line)

Replace `YOUR_TOKEN` with the token you receive from register/login.

```bash
# 1. Register a new user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"mypassword123","password_confirm":"mypassword123"}'

# 2. Login (returns the same token)
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"mypassword123"}'

# 3. Create a document (JSON)
curl -X POST http://127.0.0.1:8000/documents \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Doc","content":"Hello Django!"}'

# 4. Create a document (file upload)
curl -X POST http://127.0.0.1:8000/documents \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "title=My PDF" \
  -F "content=Description" \
  -F "file=@/path/to/your/file.pdf"

# 5. List documents (paginated)
curl "http://127.0.0.1:8000/documents?page=1&page_size=5" \
  -H "Authorization: Token YOUR_TOKEN"

# 6. Get a single document
curl http://127.0.0.1:8000/documents/1 \
  -H "Authorization: Token YOUR_TOKEN"

# 7. Delete a document
curl -X DELETE http://127.0.0.1:8000/documents/1 \
  -H "Authorization: Token YOUR_TOKEN"

# 8. Post a query
curl -X POST http://127.0.0.1:8000/query \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query_text":"What documents do I have?"}'

# 9. Get query history
curl "http://127.0.0.1:8000/queries" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Testing error scenarios:**

```bash
# No token → should return 401
curl http://127.0.0.1:8000/documents

# Wrong file type → should return 400
curl -X POST http://127.0.0.1:8000/documents \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "title=Bad File" \
  -F "content=test" \
  -F "file=@script.exe"

# Delete another user's document → should return 403
# (register a second user, get their token, try to delete user 1's document)
```

---

### Option C — Django Admin Panel

The admin panel lets you view and manage all data through a browser UI.

1. Create a superuser: `python manage.py createsuperuser`
2. Visit: `http://127.0.0.1:8000/admin/`
3. Log in with your superuser credentials
4. You can view/edit all Users, Documents, QueryLogs, and Auth Tokens

---

### Verification Checklist

After running all tests, confirm the following:

- [ ] `POST /auth/register` → HTTP 201 with a `token` field
- [ ] `POST /auth/login` → HTTP 200 with the same token
- [ ] `GET /documents` without token → HTTP 401
- [ ] `POST /documents` with JSON → HTTP 201, `owner` = your username
- [ ] `GET /documents` → HTTP 200 with `count`, `next`, `previous`, `results`
- [ ] `GET /documents/1` → HTTP 200 with the document
- [ ] `GET /documents/999` → HTTP 404
- [ ] `DELETE /documents/1` → HTTP 204 (empty body)
- [ ] `DELETE /documents/1` as a different user → HTTP 403
- [ ] Upload a `.txt` file → HTTP 201, `file` field has a URL
- [ ] Upload a `.exe` file → HTTP 400 with file type error
- [ ] Upload a file > 10 MB → HTTP 413

---

## Production Deployment

### Quick steps (any Linux server or cloud platform)

```bash
# 1. Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.production
export SECRET_KEY="your-generated-secret-key"
export ALLOWED_HOSTS="api.yourdomain.com"
export DB_NAME="mydb"
export DB_USER="myuser"
export DB_PASSWORD="securepassword"
export DB_HOST="your-postgres-host"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Collect static files (whitenoise serves these)
python manage.py collectstatic --noinput

# 4. Apply database migrations
python manage.py migrate

# 5. Start gunicorn (4 worker processes)
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

### Production checklist

- [ ] `DEBUG=False` in production settings
- [ ] `SECRET_KEY` is a long random string (not the development one)
- [ ] `ALLOWED_HOSTS` is set to your actual domain
- [ ] PostgreSQL is configured (not SQLite)
- [ ] `CORS_ALLOW_ALL_ORIGINS=False`, `CORS_ALLOWED_ORIGINS` set to your frontend URL
- [ ] `.env` is NOT committed to git
- [ ] `media/` files are stored in cloud storage (AWS S3, Azure Blob, etc.) — not on disk
- [ ] HTTPS is configured (via nginx/load balancer in front of gunicorn)
- [ ] gunicorn is managed by a process supervisor (systemd, supervisord)

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'decouple'` | Virtual environment not activated | Run `.\venv\Scripts\Activate.ps1` |
| `django.core.exceptions.ImproperlyConfigured` | `.env` file missing or `SECRET_KEY` not set | Copy `.env.example` to `.env` and set `SECRET_KEY` |
| `python: command not found` | Python not in PATH | Use `python3` or `py` on Windows |
| `HTTP 401 on all requests` | Forgot the `Authorization` header | Add `Authorization: Token <your-token>` |
| `HTTP 400 on file upload` | Wrong file type | Use `.pdf`, `.txt`, `.docx`, or `.doc` |
| `No such table: api_document` | Migrations not run | Run `python manage.py migrate` |
