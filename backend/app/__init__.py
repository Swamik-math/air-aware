from flask import Flask
from flask_cors import CORS

from app.api.routes import api_bp
from app.config import Config
from app.extensions import db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app
