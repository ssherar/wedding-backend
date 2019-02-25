from connexion.exceptions import ProblemException
from .models import User


def change_password():
    pass


def forgotten_password():
    pass


def login():
    pass


def logout():
    pass


def register_user():
    pass


def reset_password():
    pass


def verify_user():
    pass


def check_token(token: str, required_scopes=None) -> any:
    """
    Verify if given JWT token is valid and not expired, returning a user if successful.

    :param token: the JWT token given to the function by connexion
    :param required_scopes: not used
    :return: A user if token is valid, otherwise a 401 Unauthorized exception will be raised
    """
    try:
        user: User = User.validate_token(token)
        return {
            'sub': user
        }
    except ProblemException as e:
        raise e
