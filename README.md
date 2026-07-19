# Flask Notes Application

A clean and simple web application built with Flask and Flask-SQLAlchemy to manage personal notes securely.

## Features
- **User Authentication:** Secure registration, login, and logout flows.
- **Personal Dashboard:** Users can only view, create, and manage their own notes.
- **Persistent Database:** Uses SQLite to safely store user profiles and note contents.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd notes_app
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install flask flask-sqlalchemy
   ```

4. **Initialize the database table schema:**
   ```bash
   flask shell
   >>> from extensions import db
   >>> db.create_all()
   >>> exit()
   ```

5. **Run the local development server:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000` to use the application!


## Running with Docker

This project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

To run with Docker (requires Docker Desktop):
```bash
docker compose up --build
```

This starts two containers:
- `web` — the Flask application (served via Gunicorn)
- `db` — a PostgreSQL 16 database

The app will be available at `http://localhost:5000`.

**Note:** environment variables (`SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`) are configured in `docker-compose.yml` for local development — replace these with secure values before any real deployment.
