# Flask Notes App

A notes application built using **Flask** and **PostgreSQL**. Users can create, edit, organize, and manage their notes with features like rich text editing, file attachments, OCR, AI summarization, and a REST API.

## Features

* User registration and login
* Create, edit, and delete notes
* Rich text editor
* Search notes
* Categories and tags
* Pin, archive, and trash notes
* File attachments
* OCR to extract text from images
* AI-based note summarization
* Voice-to-text input
* JWT-secured REST API
* Swagger API documentation
* PostgreSQL database
* Docker support

## Tech Stack

**Backend**

* Flask
* SQLAlchemy
* Flask-Migrate
* Flask-JWT-Extended

**Database**

* PostgreSQL

**Frontend**

* HTML
* Bootstrap
* Jinja2
* Quill.js

**Other Tools**

* Hugging Face Transformers
* Tesseract OCR
* Docker
* Gunicorn

## Installation

Clone the repository:

```bash
git clone https://github.com/neha44hegde-stack/notes_app.git
cd notes_app
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a PostgreSQL database:

```sql
CREATE DATABASE notes_app;
```

Set the required environment variables:

```text
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/notes_app
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

Run the migrations:

```bash
flask db upgrade
```

Start the application:

```bash
flask run
```

Open:

```
http://127.0.0.1:5000
```

## Docker

Run the project using Docker:

```bash
docker compose up --build
```

## API

Swagger documentation is available at:

```
http://127.0.0.1:5000/apidocs
```

Some API endpoints:

* `POST /api/auth/register`
* `POST /api/auth/login`
* `GET /api/notes`
* `POST /api/notes`
* `PUT /api/notes/<id>`
* `DELETE /api/notes/<id>`

## Future Improvements

* Add unit tests
* Deploy to a cloud platform
* Improve UI
* Add email verification

## License

This project is for learning and educational purposes.
