from flask_restplus import Resource
from flask import request
from ..dto import UserDTO
from ..utils import auth_required, admin_required
from ..models import db, User

api = UserDTO.user_api
_profile_user = UserDTO.user_model
_invitation_model = UserDTO.invitation_model


@api.route("/me")
class UserProfile(Resource):
    @api.doc("Get the user profile")
    @api.marshal_with(_profile_user)
    @auth_required
    def get(self, user=None):
        return user, 200

    @api.doc("Update the user profile")
    @api.expect(_profile_user)
    @auth_required
    def patch(self, user=None):
        payload = request.json
        user.email = payload.get("email", user.email)
        user.firstname = payload.get("firstname", user.firstname)
        user.lastname = payload.get("lastname", user.lastname)
        db.session.commit()
        return {"status": "success", "message": "details updated"}, 200


@api.route("/invitation")
class Invitation(Resource):
    @api.doc("get invitation fields")
    @auth_required
    @api.marshal_with(_invitation_model)
    def get(self, user=None):
        return (user.invitation, 200)

    @api.doc("submit invitation")
    @auth_required
    @api.expect(_invitation_model)
    def post(self, user=None):
        invitation = user.invitation
        payload = request.json
        invitation.response = payload["response"]
        invitation.requirements = payload.get("requirements")
        if invitation.plus_one:
            invitation.plus_one_name = payload["plus_one_name"]
        db.session.commit()
        return ({"status": "success", "message": "invitation response updated"}, 200)


@api.route("/all")
class Users(Resource):
    @api.doc("Get all users")
    @api.marshal_with(_profile_user)
    @admin_required
    def get(self, user=None):
        return User.query.all(), 200


@api.route("/<int:user_id>")
class UserDetails(Resource):
    @api.doc("Get a single user")
    @api.marshal_with(_profile_user)
    @admin_required
    def get(self, user_id, user=None):
        return User.query.filter_by(id=user_id).first_or_404()

    @api.doc("Update a single user")
    @api.expect(_profile_user)
    @admin_required
    def patch(self, user_id, user=None):
        payload = request.json
        user = User.query.filter_by(id=user_id).first_or_404()
        user.email = payload.get("email", user.email)
        user.firstname = payload.get("firstname", user.firstname)
        user.lastname = payload.get("lastname", user.lastname)
        user.admin = payload.get("admin", user.admin)
        db.session.commit()
        return {"status": "success", "message": "details updated"}, 200
