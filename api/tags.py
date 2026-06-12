import services.tag_service as service


def get_tags(user_id):
    return service.get_tags(user_id)


def get_tag(tag_id):
    return service.get_tag(tag_id)


def create_tag(user_id, name, color=None):
    try:
        return service.create_tag(user_id, name, color=color)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_tag(tag_id, name=None, color=None):
    try:
        service.update_tag(tag_id, name=name, color=color)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def delete_tag(tag_id):
    try:
        service.delete_tag(tag_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def get_transaction_tags(transaction_id):
    return service.get_transaction_tags(transaction_id)


def add_tag_to_transaction(transaction_id, tag_id):
    try:
        service.add_tag_to_transaction(transaction_id, tag_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def remove_tag_from_transaction(transaction_id, tag_id):
    service.remove_tag_from_transaction(transaction_id, tag_id)
