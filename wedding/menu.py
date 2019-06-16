from typing import List
from .models import db, MenuItem, User
from .utils import admin_required, fail, success


def get_all(user: User, *args):
    items: List[MenuItem] = MenuItem.query.all()
    return [i.dump() for i in items], 200


def get_item(id: int, user: User, *args):
    item: MenuItem = MenuItem.query.get(id)
    if item is None:
        return fail(f"Menu item with id {id} does not exist"), 404
    return item.dump()


@admin_required
def update_item(id: int, body, user: User, *args):
    item: MenuItem = MenuItem.query.get(id)
    if item is None:
        return fail(f"Menu item with id {id} does not exist"), 404

    item.course = body.get("course", item.course)
    item.description = body.get("description", item.description)
    item.gluten_free = body.get("gluten_free", item.gluten_free)
    item.vegetarian = body.get("vegetarian", item.vegetarian)
    item.additional_info = body.get("additional_info", item.additional_info)

    db.session.commit()

    return success(f"Menu item {id} has been updated"), 200


def delete_item(id: int, user: User, *args):
    item: MenuItem = MenuItem.query.get(id)
    if item is None:
        return fail(f"Menu item with id {id} does not exist"), 404

    db.session.delete(item)
    db.session.commit()

    return success(f"Menu item with id {id} has been deleted"), 200


def create_item(body, user: User, *args):
    course = body.get("course")
    description = body.get("description")
    gluten_free = body.get("gluten_free")
    vegetarian = body.get("vegetarian")
    additional_info = body.get("additional_info")

    if course is None:
        return fail(f"The course value is required"), 400
    if description is None:
        return fail(f"The description value is required"), 400
    if gluten_free is None:
        return fail(f"The gluten_free value is required"), 400
    if vegetarian is None:
        return fail(f"The vegetarian value is required"), 400

    item = MenuItem()
    item.course = course
    item.description = description
    item.gluten_free = gluten_free
    item.vegetarian = vegetarian
    item.additional_info = additional_info

    db.session.add(item)
    db.session.commit()

    return success("The menu item has been created"), 200
