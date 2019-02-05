from flask_restplus import Resource
from flask import request
from ..dto import AuthDTO
from ..utils import auth_required
from ..models import db

api = AuthDTO.auth_api
_reg_user = AuthDTO.registration_model
_login_user = AuthDTO.login_model
_password = AuthDTO.password_model
_email_verification = AuthDTO.email_verification_model
_forgotten_password = AuthDTO.forgotten_password_model
_reset_password = AuthDTO.reset_password_model


@api.route("/register")
class UserCreate(Resource):
    @api.response(201, "User successfully created.")
    @api.response(409, "User already exists")
    @api.doc("Create a new user", security=None)
    @api.expect(_reg_user, validate=True)
    def post(self):
        data = request.json
        return AuthDTO.create(data)


@api.route("/login")
class UserLogin(Resource):
    @api.response(200, "Logged in successfully")
    @api.response(404, "User/Password combo incorrect")
    @api.doc("Login using existing credentials", security=None)
    @api.expect(_login_user, validate=True)
    def post(self):
        data = request.json
        return AuthDTO.login(data)


@api.route("/logout")
class UserLogout(Resource):
    @api.response(200, "User logged out successfully")
    @api.response(404, "User not logged in")
    @api.doc("Logout user by pulling JWT from header")
    @auth_required
    def post(sel, user=None):
        jwt = request.headers.get("X-API-Token")
        return AuthDTO.logout(jwt)


@api.route("/changepassword")
class UserUpdatePassword(Resource):
    @api.response(200, "Password changed successfully")
    @api.response(404, "Unable to update password")
    @api.expect(_password)
    @auth_required
    def post(self, user=None):
        password = request.json.get("password", None)
        user.password = password
        db.session.commit()
        return (
            {"status": "success", "message": "new password has been successfully set"},
            200,
        )


@api.route("/verify")
class UserVerifyEmail(Resource):
    @api.doc("Verify an email address", security=None)
    @api.response(200, "Email was successfully verified")
    @api.response(410, "Email code has expired or is incorrect")
    @api.expect(_email_verification)
    def post(self):
        code = request.json.get("verification_code")
        return AuthDTO.verify_email(code)


@api.route("/forgottenpassword")
class UserForgottenPassword(Resource):
    @api.doc("Send a forgotten message to an email address", security=None)
    @api.expect(_forgotten_password)
    def post(self):
        payload = request.json
        return AuthDTO.send_forgotten_email(payload["email"])


@api.route("/resetpassword")
class UserResetPassword(Resource):
    @api.doc("Reset a users password with given recovery code", security=None)
    @api.expect(_reset_password)
    def post(self):
        payload = request.json
        return AuthDTO.reset_password(payload["reset_code"], payload["password"])
