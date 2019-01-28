from flask_restplus import Resource

from flask import request
from ..dto import GroupDTO
from ..utils import admin_required
from ..models import InvitationGroup, db

api = GroupDTO.group_api
_group = GroupDTO.group_model


@api.route("/all")
class AllGroups(Resource):
    @api.doc("Get all groups")
    @api.marshal_with(_group)
    @admin_required
    def get(self, user=None):
        igs = InvitationGroup.query.all()
        return igs, 200


@api.route("/<int:group_id>")
class SingleGroup(Resource):
    @api.doc("Get a single group from parameters")
    @api.marshal_with(_group)
    @admin_required
    def get(self, group_id, user=None):
        return InvitationGroup.query.get_or_404(group_id), 200

    @api.doc("Update a groups values")
    @api.expect(_group)
    @admin_required
    def patch(self, group_id, user=None):
        payload = request.json
        group = InvitationGroup.query.get_or_404(group_id)
        group.friendly_name = payload.get("name", group.friendly_name)
        group.group_code = payload.get("code", group.group_code)
        db.session.commit()
        return {"status": "success", "message": "group updated"}, 200

    @api.doc("Delete a group")
    @admin_required
    def delete(self, group_id, user=None):
        group = InvitationGroup.query.get_or_404(group_id)
        db.session.delete(group)
        db.session.commit()
        return {"status": "success", "message": "group successfully deleted"}, 204


@api.route("/create")
class NewGroup(Resource):
    @api.doc("Create a new group and associated invitation")
    @api.expect(_group)
    @admin_required
    def post(self, user=None):
        payload = request.json
        invitation_data = payload.get("invitation")

        group = InvitationGroup()

        group.invitation.invitation_type = invitation_data.get("type")
        group.invitation.plus_one = invitation_data.get("plus_one")

        group.friendly_name = payload.get("name")
        group.group_code = payload.get("code")
        
        db.session.add(group)
        db.session.commit()

        return {"status": "success", "message": "group successfully created"}, 201
