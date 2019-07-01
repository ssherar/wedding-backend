from flask.json import dumps
from typing import Dict, List

from .models import db, User, Invitation, Guest, ResponseType, InvitationType
from .utils import admin_required, success, fail, Message


@admin_required
def all_users(user, *args) -> (List[Dict[str, str]], int):
    users: User = User.query.all()
    return [u.dump() for u in users], 200


def submit_invitation(body: Dict[str, str], user: User, *args) -> (Message, int):
    ig = user.associated_guest.invitation_group
    invitation: Invitation = ig.invitation
    guests: List[Guest] = ig.guests

    if body["invitation"]["response"] == "DECLINED":
        invitation.response = ResponseType.DECLINED
        db.session.commit()
        return success("Your response has been saved"), 200
    else:
        _process_invitation(invitation, body["invitation"])
        _process_guests(guests, body["guests"])
        db.session.commit()
        return success("Your response has been saved"), 200
    pass


def _process_invitation(invitation: Invitation, invData: Dict[str, str]):
    invitation.response = ResponseType.CONFIRMED
    invitation.requirements = invData["requirements"]
    if Invitation.invitation_type == InvitationType.HOUSE:
        invitation.staying_in_house = invData["staying_in_house"]
    else:
        invitation.staying_in_house = False


def _process_guests(guests: List[Guest], guestData: List[Dict[str, str]]):
    for gd in guestData:
        guest: Guest = list(filter(lambda x: x.id == gd["id"], guests))[0]
        guest.is_coming = gd["is_coming"]
        if not gd["is_coming"]:
            continue
        guest.first_course = gd["first_course"]
        guest.main_course = gd["main_course"]
        guest.desert_course = gd["desert_course"]


def get_invitation(user: User, *args) -> (Dict[str, str], int):
    return user.associated_guest.invitation_group.dump(), 200


def get_me(user: User, *args) -> (Dict[str, str], int):
    return user.dump(), 200


def patch_me(body: Dict[str, str], user: User) -> (Message, int):
    user.email = body.get("email", user.email)
    user.firstname = body.get("firstname", user.firstname)
    user.lastname = body.get("lastname", user.lastname)
    db.session.commit()
    return success("User profile updated successfully"), 200


def find_user(q: str, orphaned: bool):
    query = User.query.filter(User.fullname.like(f"%{q}%"))
    a = query.all()
    print(a[0].associated_guest)
    if orphaned:
        a = [u for u in a if u.associated_guest is None]
    return [u.dump() for u in a]


@admin_required
def get_user(user_id, user, *args) -> (Dict[str, str], int):
    u: User = User.query.get(user_id)
    if u:
        return u.dump(), 200
    else:
        return fail(f"User with ID {user_id} does not exist."), 404


@admin_required
def patch_user(user_id, user, body: Dict[str, str], *args) -> (Message, int):
    u: User = User.query.get(user_id)
    if u is None:
        return fail(f"User with ID {user_id} does not exist."), 404

    u.email = body.get("email", u.email)
    u.firstname = body.get("firstname", u.firstname)
    u.lastname = body.get("lastname", u.lastname)
    if user.id != u.id:
        u.admin = body.get("admin", u.admin)
    db.session.commit()
    return success(f"User '{u.fullname}' ({user_id}) has been updated"), 200


@admin_required
def delete_user(user_id, user):
    u: User = User.query.get(user_id)
    if u is None:
        return fail(f"User with ID {user_id} does not exist."), 404

    db.session.delete(u)
    db.session.commit()

    return success(f"User '{user_id}'' has been deleted"), 204
