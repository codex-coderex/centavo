import db.queries.categories as categories_q
import db.queries.users as users_q

from utils.enums import CategoryGroupType, normalize_enum_value


UNCATEGORIZED_NAME = "Uncategorized"


def get_category_groups(user_id: int):
    return categories_q.get_category_groups(user_id)


def get_all_category_groups(user_id: int):
    return categories_q.get_all_category_groups(user_id)


def get_categories(group_id: int):
    return categories_q.get_categories_by_group(group_id, active_only=True)


def get_all_categories(user_id: int):
    return categories_q.get_all_categories(user_id)


def get_all_categories_for_user(user_id: int):
    return categories_q.get_all_categories_for_user(user_id)


def create_category_group(user_id: int, name: str, type: str):
    name = name.strip()

    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    if not name:
        raise ValueError("Category group name is required")

    type = normalize_enum_value(type, CategoryGroupType, "Invalid category group type")

    group_id = categories_q.create_category_group(
        user_id=user_id,
        name=name,
        type=type,
        is_system=False
    )

    return {"group_id": group_id}


def create_category(group_id: int, name: str):
    name = name.strip()

    if not name:
        raise ValueError("Category name is required")

    group = categories_q.get_category_group(group_id)

    if group is None:
        raise ValueError("Category group does not exist")

    if not group["is_active"]:
        raise ValueError("Cannot add category to an inactive group")

    category_id = categories_q.create_category(group_id=group_id, name=name, is_system=False)

    return {"category_id": category_id}


def update_category_group(
    group_id: int,
    name: str | None = None,
    type: str | None = None,
    is_active: bool | None = None
):
    group = categories_q.get_category_group(group_id)

    if group is None:
        raise ValueError("Category group does not exist")
    if group["name"] == UNCATEGORIZED_NAME and is_active is False:
        raise ValueError("Uncategorized group cannot be deactivated")

    kwargs = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Category group name cannot be empty")
        kwargs["name"] = name
    if type is not None:
        kwargs["type"] = normalize_enum_value(type, CategoryGroupType, "Invalid category group type")
    if is_active is not None:
        kwargs["is_active"] = is_active

    if kwargs:
        categories_q.update_category_group(group_id, **kwargs)

    return {"status": "updated"}


def update_category(
    category_id: int,
    name: str | None = None,
    is_active: bool | None = None
):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if category["name"] == UNCATEGORIZED_NAME and is_active is False:
        raise ValueError("Uncategorized category cannot be deactivated")

    kwargs = {}

    if name is not None:
        name = name.strip()

        if not name:
            raise ValueError("Category name cannot be empty")

        kwargs["name"] = name

    if is_active is not None:
        kwargs["is_active"] = is_active

    if kwargs:
        categories_q.update_category(category_id, **kwargs)

    return {"status": "updated"}


def deactivate_category(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if category["name"] == UNCATEGORIZED_NAME:
        raise ValueError("Uncategorized category cannot be deactivated")

    categories_q.update_category(category_id, is_active=False)

    return {"status": "deactivated"}


def deactivate_category_group(group_id: int):
    group = categories_q.get_category_group(group_id)

    if group is None:
        raise ValueError("Category group does not exist")

    if group["name"] == UNCATEGORIZED_NAME:
        raise ValueError("Uncategorized group cannot be deactivated")

    categories_q.update_category_group(group_id, is_active=False)

    return {"status": "deactivated"}


def remove_category(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if category["name"] == UNCATEGORIZED_NAME:
        raise ValueError("Uncategorized cannot be deleted")

    if category["is_system"]:
        raise ValueError("Default categories cannot be deleted. Disable them instead.")

    refs = categories_q.get_category_reference_counts(category_id)

    if refs["transactions"] or refs["budget_items"] or refs["recurring"]:
        raise ValueError("This category is in use. Move its transactions, budget items, and recurring rules before deleting it.")

    categories_q.delete_category(category_id)

    return {"status": "deleted"}


def remove_category_group(group_id: int):
    group = categories_q.get_category_group(group_id)

    if group is None:
        raise ValueError("Category group does not exist")

    if group["name"] == UNCATEGORIZED_NAME:
        raise ValueError("Uncategorized group cannot be deleted")

    if group["is_system"]:
        raise ValueError("Default category groups cannot be deleted. Disable them instead.")

    if categories_q.group_has_referenced_categories(group_id):
        raise ValueError("This group contains categories that are in use. Move those categories before deleting the group.")

    categories_q.delete_categories_by_group(group_id)
    categories_q.delete_category_group(group_id)

    return {"status": "deleted"}
