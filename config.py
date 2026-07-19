import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "notesapp")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "notesapp-jwt-secret")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:CHANGE_ME@localhost:5432/notes_app"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "txt",
        "docx",
        "xlsx",
        "zip",
    }

    TESSERACT_CMD = os.environ.get(
        "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    SWAGGER = {
        "title": "Notes App API",
        "uiversion": 3,
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: **Bearer &lt;your_token&gt;**",
            }
        },
    }


config = Config
