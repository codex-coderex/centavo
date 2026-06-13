import db.queries.accounts as accounts_q
import db.queries.users as users_q
from utils.enums import AccountStatus, normalize_enum_value


def get_accounts(user_id: int):
    return accounts_q.get_accounts(user_id)


def get_account(account_id: int):
    return accounts_q.get_account(account_id)


def create_account(user_id: int, name: str, type: str):
    name = name.strip()
    type = type.strip()

    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    if not name:
        raise ValueError("Account name is required")

    if not type:
        raise ValueError("Account type is required")

    account_id = accounts_q.create_account(
        user_id=user_id,
        name=name,
        type=type,
    )

    return {"account_id": account_id}


def update_account(
    account_id: int,
    name: str | None = None,
    type: str | None = None,
    status: str | None = None,
):
    if accounts_q.get_account(account_id) is None:
        raise ValueError("Account does not exist")

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

    if status is not None:
        kwargs["status"] = normalize_enum_value(
            status,
            AccountStatus,
            "Invalid account status",
        )

    if kwargs:
        accounts_q.update_account(account_id, **kwargs)


def archive_account(account_id: int):
    if accounts_q.get_account(account_id) is None:
        raise ValueError("Account does not exist")

    accounts_q.archive_account(account_id)