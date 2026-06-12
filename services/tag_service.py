import db.queries.tags as tags_q
import db.queries.transactions as transactions_q


def get_tags(user_id: int):
    return tags_q.get_tags(user_id)


def get_tag(tag_id: int):
    return tags_q.get_tag(tag_id)


def create_tag(user_id: int, name: str, color: str | None = None):
    name = name.strip()

    if not name:
        raise ValueError("Tag name is required")

    tag_id = tags_q.create_tag(
        user_id=user_id,
        name=name,
        color=color,
    )

    return {"tag_id": tag_id}


def update_tag(tag_id: int, name: str | None = None, color: str | None = None):
    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Tag name cannot be empty")
        kwargs["name"] = name

    if color is not None:
        kwargs["color"] = color

    if kwargs:
        tags_q.update_tag(tag_id, **kwargs)


def delete_tag(tag_id: int):
    tags_q.delete_tag(tag_id)


def get_transaction_tags(transaction_id: int):
    return tags_q.get_transaction_tags(transaction_id)


def add_tag_to_transaction(transaction_id: int, tag_id: int):
    if transactions_q.get_transaction(transaction_id) is None:
        raise ValueError("Transaction does not exist")

    if tags_q.get_tag(tag_id) is None:
        raise ValueError("Tag does not exist")

    tags_q.add_tag_to_transaction(transaction_id, tag_id)


def remove_tag_from_transaction(transaction_id: int, tag_id: int):
    tags_q.remove_tag_from_transaction(transaction_id, tag_id)