from typing import Dict, List

from .models import db, User
from .utils import admin_required, success, fail, Message


@admin_required
def all_users(user, *args) -> (List[Dict[str, str]], int):
    users: User = User.query.all()
    return [u.dump() for u in users], 200


def submit_invitation():
    pass


def get_invitation():
    pass


def get_me(user: User, *args) -> (Dict[str, str], int):
    return user.dump(), 200


def patch_me(body: Dict[str, str], user: User) -> (Message, int):
    user.email = body.get("email", user.email)
    user.firstname = body.get("firstname", user.firstname)
    user.lastname = body.get("lastname", user.lastname)
    db.session.commit()
    return success("User profile updated successfully"), 200


def find_user():
    pass


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
