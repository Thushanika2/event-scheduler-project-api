from flask import Flask, jsonify
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.config import Config
from app.extensions import db, jwt
from app.routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from app.models.user_model import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        return User.query.get(int(jwt_data["sub"]))

    @app.errorhandler(OperationalError)
    @app.errorhandler(ProgrammingError)
    def handle_db_error(error):
        db.session.rollback()
        return jsonify({"error": "Database connection error."}), 503

    register_blueprints(app)

    with app.app_context():
        from app.models import (  # noqa: F401
            agenda_item_model,
            attendee_model,
            organiser_model,
            session_model,
            user_model,
        )

        db.create_all()

    return app
