import os
from flask import Flask
from extensions import db
from config import config

from models import User, Note


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

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

    @app.route("/")
    def hello_world():
        return """
        <h1>Hello, World!</h1>
        <p>My Notes App</p>
        <p>Project setup done and database connected.</p>
        """

    with app.app_context():
        db.create_all()

    print(app.url_map)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)