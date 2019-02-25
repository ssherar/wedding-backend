from typing import Dict
import functools

from connexion.exceptions import ProblemException
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
        user = kwargs.get("user")
        if not user.admin:
            return f(*args, **kwargs)
        raise ProblemException(404, "Unauthorized", "You are not authorized to visit this page")

    return inner


Message = Dict[str, str]


def _message(status: str, message: str, **kwargs) -> Message:
    return {
        **kwargs,
        "status": status,
        "message": message
    }


def success(message: str, **kwargs) -> Message:
    return _message("SUCCESS", message, **kwargs)


def fail(message: str, **kwargs) -> Message:
    return _message("FAIL", message, **kwargs)


def info(message: str, **kwargs) -> Message:
    return _message("INFO", message, **kwargs)
