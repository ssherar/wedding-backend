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

    if starter_id > 0:
        starter = MenuItem.query.filter_by(
            course=MenuCourse.STARTER, id=starter_id
        ).first()
        if starter is None:
            return fail(f"Starter ID '{starter_id} is not a valid starter"), 401
        else:
            guest.first_course = starter_id

    if main_id > 0:
        main = MenuItem.query.filter_by(course=MenuCourse.MAIN, id=main_id).first()
        if main is None:
            return fail(f"Main ID '{main_id}' is not a valid main course"), 401
        else:
            guest.main_course = main_id

    if desert_id > 0:
        desert = MenuItem.query.filter_by(
            course=MenuCourse.DESERT, id=desert_id
        ).first()
        if desert is None:
            return fail(f"Desert ID '{desert_id}' is not a valid desert course"), 401
        else:
            guest.desert_course = desert_id

    db.session.commit()
    return success("Guest menu choices have been updated"), 201
