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
