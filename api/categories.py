import services.category_service as service
from api.responses import ok, fail


def get_category_groups(user_id):
    try:
        return ok(service.get_category_groups(user_id))
    except ValueError as e:
        return fail(e)


def get_categories(group_id):
    try:
        return ok(service.get_categories(group_id))
    except ValueError as e:
        return fail(e)


def get_all_categories(user_id):
    try:
        return ok(service.get_all_categories(user_id))
    except ValueError as e:
        return fail(e)


def create_category_group(user_id, name, type):
    try:
        return ok(service.create_category_group(user_id, name, type))
    except ValueError as e:
        return fail(e)


def create_category(group_id, name):
    try:
        return ok(service.create_category(group_id, name))
    except ValueError as e:
        return fail(e)


def update_category_group(group_id, name=None, type=None, is_active=None):
    try:
        return ok(service.update_category_group(group_id, name=name, type=type, is_active=is_active))
    except ValueError as e:
        return fail(e)


def update_category(category_id, name=None, is_active=None):
    try:
        return ok(service.update_category(category_id, name=name, is_active=is_active))
    except ValueError as e:
        return fail(e)


def deactivate_category(category_id):
    try:
        return ok(service.deactivate_category(category_id))
    except ValueError as e:
        return fail(e)


def deactivate_category_group(group_id):
    try:
        return ok(service.deactivate_category_group(group_id))
    except ValueError as e:
        return fail(e)


def remove_category(category_id):
    try:
        return ok(service.remove_category(category_id))
    except ValueError as e:
        return fail(e)


def remove_category_group(group_id):
    try:
        return ok(service.remove_category_group(group_id))
    except ValueError as e:
        return fail(e)
