import functools
from flask import request
from .models import User


def auth_required(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        token = request.headers.get("X-API-Token")
        authed = User.validate_token(token)
        print(authed)
        if isinstance(authed, User):
            kwargs["user"] = authed
            return f(*args, **kwargs)
        return ({"status": "failed", "message": authed}, 401)

    return inner
