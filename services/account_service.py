import db.queries.accounts as accounts_q
import db.queries.users as users_q

from utils.enums import AccountStatus, AccountType, normalize_enum_value
from utils.money import to_minor_units


def get_accounts(user_id: int, active_only: bool = True):
    return accounts_q.get_accounts(user_id, active_only=active_only)


def get_account(account_id: int):
    return accounts_q.get_account(account_id)


def create_account(user_id: int, name: str, type: str, opening_balance=0):
    name = name.strip()

    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    if not name:
        raise ValueError("Account name is required")

    type = normalize_enum_value(
        type,
        AccountType,
        "Invalid account type",
    )

    account_id = accounts_q.create_account(
        user_id=user_id,
        name=name,
        type=type,
        opening_balance_minor=to_minor_units(opening_balance),
    )

    return {"account_id": account_id}


def update_account(
    account_id: int,
    name: str | None = None,
    type: str | None = None,
    opening_balance=None,
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
        kwargs["type"] = normalize_enum_value(
            type,
            AccountType,
            "Invalid account type",
        )

    if opening_balance is not None:
        kwargs["opening_balance_minor"] = to_minor_units(opening_balance)

    if status is not None:
        kwargs["status"] = normalize_enum_value(
            status,
            AccountStatus,
            "Invalid account status",
        )

    if kwargs:
        accounts_q.update_account(account_id, **kwargs)

    return {"status": "updated"}


def archive_account(account_id: int):
    if accounts_q.get_account(account_id) is None:
        raise ValueError("Account does not exist")

    accounts_q.update_account(
        account_id,
        status=AccountStatus.ARCHIVED.value,
    )

    return {"status": "archived"}