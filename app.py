import os
from flask import Flask, jsonify
from sqlalchemy import text
from extensions import db, jwt, limiter
from config import config
from flask_migrate import Migrate
from flasgger import Swagger
from models import User, Note, Tag, Category, Attachment


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    swagger = Swagger(app)

    os.makedirs(app.instance_path, exist_ok=True)

    try:
        from routes.auth import auth_bp
        from routes.notes import notes_bp
        from routes.api import api_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(notes_bp)
        app.register_blueprint(api_bp)

    except Exception as e:
        print("Blueprint import error:", e)

    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {e}"

        status_code = 200 if db_status == "ok" else 503
        return (
            jsonify(
                {
                    "status": "ok" if db_status == "ok" else "degraded",
                    "database": db_status,
                }
            ),
            status_code,
        )

    @app.route("/")
    def hello_world():
        return """
        <h1>Hello, World!</h1>
        <p>My Notes App</p>
        <p>Project setup done and database connected.</p>
        """

    print(app.url_map)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
