from flask_restplus import Namespace, fields
from ..models import ResponseType, InvitationType


class UserDTO(object):
    user_api = Namespace("user", description="User relatded operations")
    user_model = user_api.model(
        "user",
        {
            "id": fields.Integer(description="the user's ID number", readonly=True),
            "email": fields.String(description="user email address", readonly=True),
            "firstname": fields.String(description="user's firstname"),
            "lastname": fields.String(description="user's lastname"),
            "fullname": fields.String(description="user's fullname"),
            "admin": fields.Boolean(description="Is the user admin?"),
            "group_name": fields.String(
                description="Invitation Group name",
                readonly=True,
                attribute="invitation_group.friendly_name",
            ),
        },
    )
    invitation_model = user_api.model(
        "invitation",
        {
            "response": fields.String(
                description="response back to the invitation",
                enum=ResponseType._member_names_,
                required=True,
            ),
            "type": fields.String(
                description="invitation type",
                enum=InvitationType._member_names_,
                attribute="invitation_type",
                readonly=True,
            ),
            "requirements": fields.String(description="dietary requirements"),
            "plus_one": fields.Boolean(
                description="guest allowed plus one", readonly=True
            ),
            "plus_one_name": fields.String(description="Plus one name"),
            "locked": fields.Boolean(
                description="Is the invitation locked", readonly=True
            ),
            "group_name": fields.String(
                description="Invitation Group name",
                readonly=True,
                attribute="invitation_group.friendly_name",
            ),
        },
    )
