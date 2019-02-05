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
    email_verification_model = auth_api.model(
        "email_verification_model",
        {
            "verification_code": fields.String(
                required=True,
                description="Verification code found in email sent to user",
            )
        },
    )
    forgotten_password_model = auth_api.model(
        "forgotten_password_model",
        {
            "email": fields.String(
                required=True,
                description="Email address to potentially send a recovery email to",
            )
        },
    )

    reset_password_model = auth_api.model(
        "reset_password_model",
        {
            "reset_code": fields.String(
                required=True,
                description="Code that was generated and sent to the user via email",
            ),
            "password": fields.String(
                required=True, description="New password to be set to the user"
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
        user = User.query.filter_by(email=data["email"]).first()
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

        new_user.untrust_email()

        db.session.add(new_user)
        db.session.commit()
        return ({"status": "201", "message": "account created"}, 201)

    @staticmethod
    def login(data):
        user = User.query.filter_by(email=data["email"]).first()
        if user:
            if user.verified is False:
                return (
                    {"status": "failed", "message": "email has not been verified"},
                    410,
                )
            if user.check_password(data["password"]):
                token = user.generate_jwt()
                return (
                    {
                        "status": "success",
                        "message": "logged in successfully",
                        "token": token,
                    },
                    200,
                )
        return (
            {"status": "failed", "message": "username/password combo incorrect"},
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

    @staticmethod
    def verify_email(code):
        message, error = User.validate_email_code(code)
        if error:
            return ({"status": "fail", "message": message}, 410)
        return ({"status": "success", "message": message}, 200)

    @staticmethod
    def send_forgotten_email(email_address):
        user = User.query.filter_by(email=email_address).first()
        if user is not None:
            user.generate_recovery_code()
            #  Send email!
        return {}, 200

    @staticmethod
    def reset_password(code, password):
        user = User.validate_recovery_code(code)
        print(user)
        if user is not None:
            user.password = password
            db.session.commit()
            return (
                {
                    "status": "success",
                    "message": "Password has been updated successfully",
                },
                200,
            )
        return (
            {
                "status": "fail",
                "message": "Code is invalid. Please try and reset your password again",
            },
            400,
        )

