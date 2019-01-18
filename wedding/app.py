from flask import Flask
from .models import db, flask_bcrypt
from .config import config_by_name
from .blueprints import api_blueprint


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    flask_bcrypt.init_app(app)
    app.register_blueprint(api_blueprint, url_prefix="/api")

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, x-api-token"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,PATCH"
        )
        return response

    return app
