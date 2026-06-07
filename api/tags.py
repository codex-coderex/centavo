import db.queries.tags as q


def get_tags(user_id):
    return q.get_tags(user_id)


def get_tag(tag_id):
    return q.get_tag(tag_id)


def create_tag(user_id, name, color=None):
    tag_id = q.create_tag(user_id, name, color)
    return {"tag_id": tag_id}


def update_tag(tag_id, name=None, color=None):
    kwargs = {k: v for k, v in {
        "name": name,
        "color": color,
    }.items() if v is not None}
    q.update_tag(tag_id, **kwargs)


def delete_tag(tag_id):
    q.delete_tag(tag_id)


def get_transaction_tags(transaction_id):
    return q.get_transaction_tags(transaction_id)


def add_tag_to_transaction(transaction_id, tag_id):
    q.add_tag_to_transaction(transaction_id, tag_id)


def remove_tag_from_transaction(transaction_id, tag_id):
    q.remove_tag_from_transaction(transaction_id, tag_id)
