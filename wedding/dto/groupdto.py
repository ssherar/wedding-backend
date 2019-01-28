from flask_restplus import Namespace, fields
from .userdto import UserDTO


class GroupDTO(object):
    group_api = Namespace("group", description="Invitation Group related operations")

    group_model = group_api.model(
        "group_model",
        {
            "id": fields.Integer(
                description="The groups unique ID number", readonly=True
            ),
            "name": fields.String(
                description="Name of the invitation group", attribute="friendly_name"
            ),
            "code": fields.String(
                description="Unique code to allow a new user to register as part of the party",
                attribute="group_code",
            ),
            "users": fields.List(fields.Nested(UserDTO.user_model)),
            "invitation": fields.Nested(UserDTO.invitation_model),
        },
    )
