import functools
from flask import request
from .models import User


def auth_required(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        token = request.headers.get("X-API-Token")
        authed = User.validate_token(token)
        if isinstance(authed, User):
            kwargs["user"] = authed
            return f(*args, **kwargs)
        return ({"status": "failed", "message": authed}, 401)

    return inner


def admin_required(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        token = request.headers.get("X-API-Token")
        authed = User.validate_token(token)
        if isinstance(authed, User) and authed.admin:
            kwargs["user"] = authed
            return f(*args, **kwargs)
        return {"status": "failed", "message": "not an admin"}, 401

    return inner
