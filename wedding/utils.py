from typing import Dict
import functools

from connexion.exceptions import ProblemException
from .models import User


def admin_required(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        user: User = kwargs.get("user")
        if user.admin:
            return f(*args, **kwargs)
        raise ProblemException(403, "Unauthorized", "You are not authorized to visit this page")

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
