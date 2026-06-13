import services.category_service as service


def get_category_groups(user_id):
    return service.get_category_groups(user_id)


def get_categories(group_id):
    return service.get_categories(group_id)


def get_all_categories(user_id):
    return service.get_all_categories(user_id)


def create_category_group(user_id, name, type):
    try:
        return service.create_category_group(user_id, name, type)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def create_category(group_id, name, color=None):
    try:
        return service.create_category(group_id, name, color=color)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_category_group(group_id, name=None, type=None, is_active=None):
    try:
        service.update_category_group(group_id, name=name, type=type, is_active=is_active)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_category(category_id, name=None, color=None, is_active=None):
    try:
        service.update_category(category_id, name=name, color=color, is_active=is_active)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def remove_category(category_id):
    try:
        return service.remove_category(category_id)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def remove_category_group(group_id):
    try:
        return service.remove_category_group(group_id)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def deactivate_category(category_id):
    try:
        return service.deactivate_category(category_id)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def deactivate_category_group(group_id):
    try:
        return service.deactivate_category_group(group_id)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
