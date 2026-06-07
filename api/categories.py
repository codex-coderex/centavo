import db.queries.categories as q


def get_category_groups(user_id):
    return q.get_category_groups(user_id)


def get_categories(group_id):
    return q.get_categories(group_id)


def get_all_categories(user_id):
    return q.get_all_categories(user_id)


def create_category_group(user_id, name, type):
    group_id = q.create_category_group(user_id, name, type)
    return {"group_id": group_id}


def create_category(group_id, name, color=None):
    # is_system is always False — only the seed can create system categories
    category_id = q.create_category(group_id, name, color=color, is_system=False)
    return {"category_id": category_id}


def update_category(category_id, name=None, color=None, is_active=None):
    # is_system is not accepted — system categories are immutable
    kwargs = {k: v for k, v in {
        "name": name,
        "color": color,
        "is_active": is_active,
    }.items() if v is not None}
    q.update_category(category_id, **kwargs)


def deactivate_category(category_id):
    q.deactivate_category(category_id)
