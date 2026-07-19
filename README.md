# Flask Notes Application

A full-featured, production-style notes application built with Flask, SQLAlchemy, and PostgreSQL — supporting rich text editing, file attachments, AI-powered summarization, OCR, voice input, a documented REST API, and containerized deployment.

## Features

- **User Authentication** — secure registration, login, and logout with hashed passwords
- **Personal Dashboard** — each user manages only their own notes
- **Search** — full-text search across note titles and descriptions
- **Tags** — flexible, user-defined tags for organizing notes
- **Categories** — folder-style organization for notes
- **Pin Notes** — keep important notes at the top of the dashboard
- **Archive Notes** — move notes out of the main view without deleting them
- **Trash & Restore** — soft-delete notes with the ability to restore or permanently delete
- **Rich Text Editor** — format notes with bold, italics, lists, and more (powered by Quill.js)
- **File Attachments** — attach files to any note, with download and removal support
- **AI Note Summarizer** — generate concise summaries of longer notes using a local Hugging Face summarization model (no external API required)
- **OCR (Image to Text)** — extract text directly from image attachments using Tesseract OCR
- **Voice to Text** — dictate notes using the browser's built-in speech recognition
- **REST API** — full CRUD API for notes, tags, and categories, secured with JWT authentication
- **Interactive API Docs** — Swagger UI available at `/apidocs`
- **PostgreSQL** — production-grade relational database with Alembic-based migrations
- **Docker** — containerized deployment with Docker Compose (app + database)

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-JWT-Extended
- **Database:** PostgreSQL
- **Frontend:** Jinja2 templates, Bootstrap, Quill.js (rich text), Web Speech API (voice input)
- **AI/ML:** Hugging Face Transformers (summarization), Tesseract OCR (image-to-text)
- **API Docs:** Flasgger (Swagger UI)
- **Deployment:** Docker, Docker Compose, Gunicorn

## Installation & Setup (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/neha44hegde-stack/notes_app.git
cd notes_app
```

### 2. Set up a virtual environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install PostgreSQL
Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/), then create a database:
```sql
CREATE DATABASE notes_app;
```

### 5. Install Tesseract OCR
Download from the [Tesseract Windows installer](https://github.com/UB-Mannheim/tesseract/wiki) (or your platform's package manager on Mac/Linux).

### 6. Set environment variables
```bash
# Windows PowerShell
$env:DATABASE_URL = "postgresql://postgres:<your-password>@localhost:5432/notes_app"
$env:SECRET_KEY = "your-secret-key"
$env:JWT_SECRET_KEY = "your-jwt-secret-key"
```

### 7. Run database migrations
```bash
flask db upgrade
```

### 8. Run the development server
```bash
flask run
```

Visit `http://127.0.0.1:5000` in your browser.

## Running with Docker

This project also includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

```bash
docker compose up --build
```

This starts two containers:
- `web` — the Flask application (served via Gunicorn)
- `db` — a PostgreSQL 16 database

The app will be available at `http://localhost:5000`.

**Note:** environment variables in `docker-compose.yml` are set for local development convenience — replace them with secure values before any real deployment.

## API Documentation

Once running, interactive API docs are available at:
http://127.0.0.1:5000/apidocs
Key endpoints:
- `POST /api/auth/register` — create an account
- `POST /api/auth/login` — receive a JWT access token
- `GET /api/notes` — list notes (supports `view` and `q` query params)
- `POST /api/notes` — create a note
- `PUT /api/notes/<id>` — update a note
- `DELETE /api/notes/<id>` — move a note to trash

All `/api/notes`, `/api/categories`, and `/api/tags` endpoints require a `Authorization: Bearer <token>` header.
