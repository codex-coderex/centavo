import db.queries.accounts as accounts_q
import db.queries.currency as currency_q
from utils.enums import AccountStatus


def get_accounts(user_id: int):
    return accounts_q.get_accounts(user_id)


def get_account(account_id: int):
    return accounts_q.get_account(account_id)


def create_account(user_id: int, name: str, type: str, currency_code: str):
    name = name.strip()
    type = type.strip()
    currency_code = currency_code.strip().upper()

    if not name:
        raise ValueError("Account name is required")

    if not type:
        raise ValueError("Account type is required")

    if currency_q.get_currency(currency_code) is None:
        raise ValueError("Currency does not exist")

    account_id = accounts_q.create_account(
        user_id=user_id,
        name=name,
        type=type,
        currency_code=currency_code,
    )

    return {"account_id": account_id}


def update_account(
    account_id: int,
    name: str | None = None,
    type: str | None = None,
    currency_code: str | None = None,
    status: str | None = None,
):
    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Account name cannot be empty")
        kwargs["name"] = name

    if type is not None:
        type = type.strip()
        if not type:
            raise ValueError("Account type cannot be empty")
        kwargs["type"] = type

    if currency_code is not None:
        currency_code = currency_code.strip().upper()
        if currency_q.get_currency(currency_code) is None:
            raise ValueError("Currency does not exist")
        kwargs["currency_code"] = currency_code

    if status is not None:
        if status not in AccountStatus:
            raise ValueError("Invalid account status")
        kwargs["status"] = status

    if kwargs:
        accounts_q.update_account(account_id, **kwargs)


def archive_account(account_id: int):
    accounts_q.archive_account(account_id)