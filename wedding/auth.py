from typing import Dict

from connexion.exceptions import ProblemException
from .models import Token, User
from .utils import success, fail, Message


def change_password():
    pass


def forgotten_password():
    pass


def login(body: Dict[str, str], user: User = None) -> (Message, int):
    """
    Authenticates a user from a given email/pasword passed in the request body.

    200 is only ever given when the token has been generated and passed back. Otherwise
    all the other responses will be 404 and a non-descript error message to stop any potential
    guessing of account emails

    :param body: Parameters passed in the body of the request
    :param user: The user calling the command, normally `None` and will be overwritten
    :return: A `Message` type and the HTTP status code (404 or 200)
    """
    email: str = body.get('email', None)
    password: str = body.get('password', None)

    if email is None or password is None:
        return fail("Email/Password combo incorrect"), 404

    user: User = User.query.filter_by(email=email).first()
    if user is None:
        return fail("Email/Password combo incorrect"), 404

    if not user.verified:
        return fail("Email has not been verified."), 404

    if user.check_password(password):
        token = user.generate_jwt()
        return success("User logged in", token=token), 200
    else:
        return fail("Email/Password combo incorrect"), 404


def logout(body, user: User = None, token_info=None) -> (Message, int):
    token: str = token_info.get("token")
    Token.revoke(token)

    return success("Logged out successfully!"), 200


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
            'sub': user,
            'token': token
        }
    except ProblemException as e:
        raise e
