from flask_restplus import Api
from flask import Blueprint
from .auth import api as auth_ns
from .user import api as user_ns
from .group import api as group_ns

api_blueprint = Blueprint("api", __name__)
authorisations = {"jwt": {"type": "apiKey", "in": "header", "name": "X-API-Token"}}

api = Api(
    api_blueprint,
    title="Wedding API",
    version="1.0",
    description="Wedding API",
    authorizations=authorisations,
    security=["jwt"],
)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(user_ns, "/profile")
api.add_namespace(group_ns, "/groups")
