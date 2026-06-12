import db.queries.users as users_q
from services.currency_service import ensure_currency_exists


def get_users():
    return users_q.get_users()


def get_user(user_id: int):
    return users_q.get_user(user_id)


def create_user(name: str, currency_code: str):
    name = name.strip()
    currency_code = currency_code.strip().upper()

    if not name:
        raise ValueError("User name is required")

    ensure_currency_exists(currency_code)

    user_id = users_q.create_user(name, currency_code)

    return {"user_id": user_id}


def update_user(
    user_id: int,
    name: str | None = None,
    currency_code: str | None = None,
):
    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("User name cannot be empty")
        kwargs["name"] = name

    if currency_code is not None:
        currency_code = currency_code.strip().upper()
        ensure_currency_exists(currency_code)
        kwargs["currency_code"] = currency_code

    if kwargs:
        users_q.update_user(user_id, **kwargs)