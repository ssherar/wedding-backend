from typing import Dict

from connexion.exceptions import ProblemException
from .models import db, Token, User
from .utils import success, fail, info, Message


def change_password(body: Dict[str, str], user: User) -> (Message, int):
    """
    Changes the users password if they are logged in
    """
    password = body.get("password", None)
    if not password:
        return fail("You did not provide a password"), 404
    user.password = password
    db.session.commit()

    return success("Password changed successfully"), 200


def forgotten_password(body: Dict[str, str], user: User = None) -> (Message, int):
    """
    Sends an email to the user (if they exist) from the email passed
    in by the body of the request with a 24 hour time sensitive code.

    It will always return HTTP OK and INFO so to stop account guessing
    """
    email = body.get("email", None)
    user: User = User.query.filter_by(email=email).first()
    if user is not None:
        user.generate_recovery_code()
        #  Send email!
    return info("An email has been sent to the email associated to this user if it exists. Please check your inbox"), 200


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


def logout(body: Dict[str, str] , user: User = None, token_info=None) -> (Message, int):
    token: str = token_info.get("token")
    Token.revoke(token)

    return success("Logged out successfully!"), 200


def register_user():
    pass


def reset_password(body: Dict[str, str], user: User = None) -> (Message, int):
    code = body.get("reset_code", None)
    password = body.get("password", None)

    if code is None:
        return fail("Code was not provided"), 404
    if password is None:
        return fail("Password was not provided"), 404

    try:
        user: User = User.validate_recovery_code(code)
    except Exception as e:
        return fail(str(e)), 404

    user.password = password
    db.session.commit()
    return success("Password has been updated successfully. Please try and login again"), 200


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
