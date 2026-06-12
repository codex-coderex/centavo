import db.queries.categories as categories_q
from utils.enums import CategoryGroupType


def get_category_groups(user_id: int):
    return categories_q.get_category_groups(user_id)


def get_categories(group_id: int):
    return categories_q.get_categories(group_id)


def get_all_categories(user_id: int):
    return categories_q.get_all_categories(user_id)


def create_category_group(user_id: int, name: str, type: str):
    name = name.strip()
    type = type.strip().lower()

    if not name:
        raise ValueError("Category group name is required")

    if type not in CategoryGroupType:
        raise ValueError("Invalid category group type")

    group_id = categories_q.create_category_group(
        user_id=user_id,
        name=name,
        type=type,
    )

    return {"group_id": group_id}


def create_category(group_id: int, name: str, color: str | None = None):
    name = name.strip()

    if not name:
        raise ValueError("Category name is required")

    category_id = categories_q.create_category(
        group_id=group_id,
        name=name,
        color=color,
        is_system=False,
    )

    return {"category_id": category_id}


def update_category(
    category_id: int,
    name: str | None = None,
    color: str | None = None,
    is_active: bool | None = None,
):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if category["is_system"]:
        raise ValueError("System categories cannot be edited")

    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Category name cannot be empty")
        kwargs["name"] = name

    if color is not None:
        kwargs["color"] = color

    if is_active is not None:
        kwargs["is_active"] = is_active

    if kwargs:
        categories_q.update_category(category_id, **kwargs)


def deactivate_category(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if category["is_system"]:
        raise ValueError("System categories cannot be deactivated")

    categories_q.deactivate_category(category_id)