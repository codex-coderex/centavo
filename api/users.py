import services.user_service as service
from api.responses import safe


def get_users():
    return safe(lambda: service.get_users())


def get_user(user_id):
    return safe(lambda: service.get_user(user_id))


def create_user(name):
    return safe(lambda: service.create_user(name))


def update_user(user_id, name=None):
    return safe(lambda: service.update_user(user_id, name=name))
