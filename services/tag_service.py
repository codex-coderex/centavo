import db.queries.tags as tags_q
import db.queries.transactions as transactions_q
import db.queries.accounts as accounts_q
import db.queries.users as users_q


def get_tags(user_id: int):
    return tags_q.get_tags(user_id)


def get_tag(tag_id: int):
    return tags_q.get_tag(tag_id)


def create_tag(user_id: int, name: str):
    name = name.strip()
    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")
    if not name:
        raise ValueError("Tag name is required")
    tag_id = tags_q.create_tag(user_id=user_id, name=name)
    return {"tag_id": tag_id}


def update_tag(tag_id: int, name: str | None = None):
    if tags_q.get_tag(tag_id) is None:
        raise ValueError("Tag does not exist")

    kwargs = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Tag name cannot be empty")
        kwargs["name"] = name

    if kwargs:
        tags_q.update_tag(tag_id, **kwargs)
    return {"status": "updated"}


def delete_tag(tag_id: int):
    if tags_q.get_tag(tag_id) is None:
        raise ValueError("Tag does not exist")
    tags_q.delete_tag(tag_id)
    return {"status": "deleted"}


def get_transaction_tags(transaction_id: int):
    return tags_q.get_transaction_tags(transaction_id)


def add_tag_to_transaction(transaction_id: int, tag_id: int):
    transaction = transactions_q.get_transaction(transaction_id)
    if transaction is None:
        raise ValueError("Transaction does not exist")

    tag = tags_q.get_tag(tag_id)
    if tag is None:
        raise ValueError("Tag does not exist")

    account = accounts_q.get_account(transaction["account_id"])
    if account is None:
        raise ValueError("Transaction account does not exist")
    if tag["user_id"] != account["user_id"]:
        raise ValueError("Tag does not belong to the same user as the transaction")

    tags_q.create_transaction_tag(transaction_id, tag_id)
    return {"status": "added"}


def remove_tag_from_transaction(transaction_id: int, tag_id: int):
    tags_q.delete_transaction_tag(transaction_id, tag_id)
    return {"status": "removed"}
