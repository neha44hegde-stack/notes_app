import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "notesapp"
    JWT_SECRET_KEY = "notesapp-jwt-secret"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR,
        "instance",
        "notes.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {
        "png", "jpg", "jpeg", "gif", "pdf", "txt", "docx", "xlsx", "zip"
    }

    SWAGGER = {
        "title": "Notes App API",
        "uiversion": 3,
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: **Bearer &lt;your_token&gt;**"
            }
        },
    }


config = Config
