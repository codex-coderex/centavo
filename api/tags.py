import services.tag_service as service
from api.responses import safe


def get_tags(user_id):
    return safe(lambda: service.get_tags(user_id))


def get_tag(tag_id):
    return safe(lambda: service.get_tag(tag_id))


def create_tag(user_id, name):
    return safe(lambda: service.create_tag(user_id, name))


def update_tag(tag_id, name=None):
    return safe(lambda: service.update_tag(tag_id, name=name))


def delete_tag(tag_id):
    return safe(lambda: service.delete_tag(tag_id))


def get_transaction_tags(transaction_id):
    return safe(lambda: service.get_transaction_tags(transaction_id))


def add_tag_to_transaction(transaction_id, tag_id):
    return safe(lambda: service.add_tag_to_transaction(transaction_id, tag_id))


def remove_tag_from_transaction(transaction_id, tag_id):
    return safe(lambda: service.remove_tag_from_transaction(transaction_id, tag_id))
