from flask_restplus import Resource

# from flask import request
from ..dto import GroupDTO
from ..utils import admin_required
from ..models import InvitationGroup

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
