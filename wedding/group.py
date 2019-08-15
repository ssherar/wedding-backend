from typing import Dict, List

from .models import db, InvitationGroup, User, Guest
from .utils import admin_required, fail, success


@admin_required
def all_groups(user: User, *args) -> (List[Dict[str, str]], 200):
    return [g.dump() for g in InvitationGroup.query.all()], 200


@admin_required
def create_group(body, user: User, *args):
    invitation_data = body.get("invitation")

    group = InvitationGroup()

    group.invitation.invitation_type = invitation_data.get("type")
    group.invitation.plus_one = invitation_data.get("plus_one")

    group.friendly_name = body.get("name")
    group.group_code = body.get("code")

    db.session.add(group)
    db.session.commit()
    return success(f"Group {group.friendly_name} has been created!"), 201


def find_by_registration_code(code, *args):
    group = InvitationGroup.query.filter_by(group_code=code).first()
    if group is None:
        return (
            fail(
                f"Group with invitation code '{code}' doesn't exist. Please check and try again"
            ),
            404,
        )
    else:
        available_guests = [g.dump() for g in group.guests if g.user is None]
        return {
            "id": group.id,
            "name": group.friendly_name,
            "registration_code": group.group_code,
            "guests": available_guests,
        }


@admin_required
def delete_group(group_id, user: User, *args):
    group = InvitationGroup.query.get(group_id)
    if group is None:
        return fail(f"Group '{group_id}' does not exist"), 404
    db.session.delete(group)
    db.session.commit()
    return success(f"Group '{group_id}' has been deleted"), 200


@admin_required
def patch_group(group_id, body, user: User, *args):
    group = InvitationGroup.query.get(group_id)
    if group is None:
        return fail(f"Group '{group_id}' does not exist"), 404
    group.friendly_name = body.get("name", group.friendly_name)
    group.group_code = body.get("code", group.group_code)

    inv_payload = body.get("invitation", None)
    if inv_payload is not None:
        invitation = group.invitation
        invitation.response = inv_payload.get("response", invitation.response)
        invitation.invitation_type = inv_payload.get("type", invitation.invitation_type)
        invitation.requirements = inv_payload.get(
            "requirements", invitation.requirements
        )
        invitation.locked = inv_payload.get("locked", invitation.locked)
    db.session.commit()
    return success(f"Group '{group.friendly_name}' updated"), 200


@admin_required
def get_group(group_id, user, *args) -> (Dict[str, str], int):
    ig = InvitationGroup.query.get(group_id)
    if ig is None:
        return fail(f"Group '{group_id}' does not exist"), 404
    return ig.dump(), 200


@admin_required
def add_guest_to_group(group_id, body, user: User, *args):
    ig = InvitationGroup.query.get(group_id)
    if ig is None:
        return fail(f"Group '{group_id}' does not exist"), 404

    guest_name = body.get("name", None)
    if not guest_name:
        return fail("A guest name is requierd")

    guest = Guest(name=guest_name)
    ig.guests.append(guest)
    db.session.commit()

    return success(f"Guest '{guest_name}' has been created", guest=guest.dump())


@admin_required
def remove_guest_from_group(group_id, guest_id, user: User, *args):
    ig = InvitationGroup.query.get(group_id)
    if ig is None:
        return fail(f"Group '{group_id}' does not exist"), 404

    guest = Guest.query.get(guest_id)
    if guest is None:
        return fail(f"Guest with id '{guest_id}' does not exist"), 404

    db.session.delete(guest)
    db.session.commit()

    return success("Guest has been deleted"), 200


@admin_required
def relate_user_and_guest(group_id, body, user: User, *args):
    guest_id = body.get("guest_id")
    user_id = body.get("user_id")
    ig = InvitationGroup.query.get(group_id)
    if ig is None:
        return fail(f"Group '{group_id}' does not exist"), 404

    guest: Guest = Guest.query.get(guest_id)
    if guest is None:
        return fail(f"Guest with id '{guest_id}' does not exist"), 404

    user = User.query.get(user_id)
    if user is None:
        return fail(f"User with id '{user_id}' does not exist"), 404

    guest.user = user
    db.session.commit()
    return (
        success(f"{user.fullname} has been related to the guestname {guest.name}"),
        200,
    )


@admin_required
def remove_relation_from_guest(group_id, body, user: User, *args):
    guest_id = body.get("guest_id")
    ig = InvitationGroup.query.get(group_id)
    if ig is None:
        return fail(f"Group '{group_id}' does not exist"), 404

    guest: Guest = Guest.query.get(guest_id)
    if guest is None:
        return fail(f"Guest with id '{guest_id}' does not exist"), 404

    fullname = guest.user.fullname

    guest.user = None
    db.session.commit()

    return (
        success(
            f"The relationship between user {fullname} and guest {guest.name} as been removed"
        ),
        200,
    )

