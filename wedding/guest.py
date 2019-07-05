from typing import Dict, List

from .models import db, Guest, User, MenuItem, MenuCourse
from .utils import admin_required, fail, success, Message


@admin_required
def update_menu_options(body, id: int, user: User, *args) -> (Message, int):
    starter_id = body.get("starter_id", 0)
    main_id = body.get("main_id", 0)
    desert_id = body.get("desert_id", 0)

    guest = Guest.query.get(id)
    if guest is None:
        return fail("Guest not found"), 404

    message = _update_menu_choices(guest, starter_id, main_id, desert_id)
    if message is not None:
        return message, 401

    db.session.commit()
    return success("Guest menu choices have been updated"), 201


@admin_required
def patch_guest(body, id: int, user: User, *args) -> (Message, int):
    name = body.get("name", None)
    type_ = body.get("type", "ADULT")
    coming = body.get("coming", None)
    plus_one = body.get("plus_one", False)
    starter_id = body.get("first_course", 0)
    main_id = body.get("main_course", 0)
    desert_id = body.get("desert", 0)

    guest = Guest.query.get(id)
    if guest is None:
        return fail("Guest not found"), 404

    message = _update_menu_choices(guest, starter_id, main_id, desert_id)
    if message is not None:
        return message, 401

    if name is not None:
        guest.name = name

    guest.type_ = type_
    guest.is_coming = coming
    guest.plus_one = plus_one

    db.session.commit()

    return success("Guest has been updated"), 201


def _update_menu_choices(
    guest: Guest, starter_id: int, main_id: int, desert_id: int
) -> Message:
    if starter_id is not None and starter_id > 0:
        starter = MenuItem.query.filter_by(
            course=MenuCourse.STARTER, id=starter_id
        ).first()
        if starter is None:
            return fail(f"Starter ID '{starter_id} is not a valid starter")
        else:
            guest.first_course = starter_id

    if main_id is not None and main_id > 0:
        main = MenuItem.query.filter_by(course=MenuCourse.MAIN, id=main_id).first()
        if main is None:
            return fail(f"Main ID '{main_id}' is not a valid main course")
        else:
            guest.main_course = main_id

    if desert_id is not None and desert_id > 0:
        desert = MenuItem.query.filter_by(
            course=MenuCourse.DESERT, id=desert_id
        ).first()
        if desert is None:
            return fail(f"Desert ID '{desert_id}' is not a valid desert course")
        else:
            guest.desert_course = desert_id

    return None
