import datetime
from flask_restplus import Namespace, fields
from ..models import db, User, InvitationGroup, Token


class AuthDTO(object):
    auth_api = Namespace("auth", description="auth related operations")
    password_model = auth_api.model(
        "password_model",
        {"password": fields.String(required=True, description="user password")},
    )
    login_model = auth_api.inherit(
        "login_user",
        password_model,
        {"email": fields.String(required=True, description="user email address")},
    )
    registration_model = auth_api.inherit(
        "registration_user",
        login_model,
        {
            "firstname": fields.String(required=True, description="user's firstname"),
            "lastname": fields.String(required=True, description="user's lastname"),
            "registration_code": fields.String(
                required=True, description="Invitation groups code"
            ),
        },
    )

    @staticmethod
    def create(data):
        ig = (
            InvitationGroup.query.filter_by(group_code=data["registration_code"])
        ).first()
        if not ig:
            return (
                {"status": "fail", "message": "registration code does not exist"},
                409,
            )
        user = (User.query.filter_by(email=data["email"])).first()
        if user:
            return (
                {
                    "status": "fail",
                    "message": "an account already exists with that email",
                },
                409,
            )
            new_user = User(
                email=data["email"],
                password=data["password"],
                firstname=data["firstname"],
                lastname=data["lastname"],
                registered_on=datetime.datetime.now(),
            )
            new_user.invitation_group = ig
            db.session.add(new_user)
            db.session.commit()
            return ({"status": "201", "message": "account created"}, 201)

    @staticmethod
    def login(data):
        user = (User.query.filter_by(email=data["email"])).first()
        if user:
            if user.check_password(data["password"]):
                token = user.generate_jwt()
                print(token)
                return (
                    {
                        "status": "success",
                        "message": "logged in successfully",
                        "token": token,
                    },
                    200,
                )
                return (
                    {
                        "status": "failed",
                        "message": "username/password combo incorrect",
                    },
                    404,
                )

    @staticmethod
    def logout(auth_token):
        print(auth_token)
        user = User.validate_token(auth_token)
        if isinstance(user, User):
            Token.revoke(auth_token)
            return ({"status": "success", "message": "logged out successfully"}, 200)
            if isinstance(user, str):
                return ({"status": "fail", "message": user}, 400)
                return ({"status": "fail", "message": "unknown error"}, 501)


# okay decompiling __pycache__/authdto.cpython-36.pyc
