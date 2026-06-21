import services.user_service as service
from api.responses import ok, fail


def get_users():
    try:
        return ok(service.get_users())
    except ValueError as e:
        return fail(e)


def get_user(user_id):
    try:
        return ok(service.get_user(user_id))
    except ValueError as e:
        return fail(e)


def create_user(name):
    try:
        return ok(service.create_user(name))
    except ValueError as e:
        return fail(e)


def update_user(user_id, name=None):
    try:
        return ok(service.update_user(user_id, name=name))
    except ValueError as e:
        return fail(e)
