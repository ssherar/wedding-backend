import connexion

from .models import db, flask_bcrypt
from .config import config_by_name


def create_app(config_name, options):
    api = connexion.FlaskApp(__name__, specification_dir="specs/", options=options)
    app = api.app
    app.config.from_object(config_by_name[config_name])
    api.add_api("api.yml")
    db.init_app(app)
    flask_bcrypt.init_app(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, x-api-key"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,PATCH"
        )
        return response

    return app
