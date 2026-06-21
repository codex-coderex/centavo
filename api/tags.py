import services.tag_service as service
from api.responses import ok, fail


def get_tags(user_id):
    try:
        return ok(service.get_tags(user_id))
    except ValueError as e:
        return fail(e)


def get_tag(tag_id):
    try:
        return ok(service.get_tag(tag_id))
    except ValueError as e:
        return fail(e)


def create_tag(user_id, name):
    try:
        return ok(service.create_tag(user_id, name))
    except ValueError as e:
        return fail(e)


def update_tag(tag_id, name=None):
    try:
        return ok(service.update_tag(tag_id, name=name))
    except ValueError as e:
        return fail(e)


def delete_tag(tag_id):
    try:
        return ok(service.delete_tag(tag_id))
    except ValueError as e:
        return fail(e)


def get_transaction_tags(transaction_id):
    try:
        return ok(service.get_transaction_tags(transaction_id))
    except ValueError as e:
        return fail(e)


def add_tag_to_transaction(transaction_id, tag_id):
    try:
        return ok(service.add_tag_to_transaction(transaction_id, tag_id))
    except ValueError as e:
        return fail(e)


def remove_tag_from_transaction(transaction_id, tag_id):
    try:
        return ok(service.remove_tag_from_transaction(transaction_id, tag_id))
    except ValueError as e:
        return fail(e)
