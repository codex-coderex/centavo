import services.category_service as service
from api.responses import safe


def get_category_groups(user_id):
    return safe(lambda: service.get_category_groups(user_id))


def get_all_category_groups(user_id):
    return safe(lambda: service.get_all_category_groups(user_id))


def get_categories(group_id):
    return safe(lambda: service.get_categories(group_id))


def get_all_categories(user_id):
    return safe(lambda: service.get_all_categories(user_id))


def get_all_categories_for_user(user_id):
    return safe(lambda: service.get_all_categories_for_user(user_id))


def create_category_group(user_id, name, type):
    return safe(lambda: service.create_category_group(user_id, name, type))


def create_category(group_id, name):
    return safe(lambda: service.create_category(group_id, name))


def update_category_group(group_id, name=None, type=None, is_active=None):
    return safe(lambda: service.update_category_group(group_id, name=name, type=type, is_active=is_active))


def update_category(category_id, name=None, is_active=None):
    return safe(lambda: service.update_category(category_id, name=name, is_active=is_active))


def deactivate_category(category_id):
    return safe(lambda: service.deactivate_category(category_id))


def deactivate_category_group(group_id):
    return safe(lambda: service.deactivate_category_group(group_id))


def remove_category(category_id):
    return safe(lambda: service.remove_category(category_id))


def remove_category_group(group_id):
    return safe(lambda: service.remove_category_group(group_id))
