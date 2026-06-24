import db.queries.accounts as accounts_q
import db.queries.transactions as transactions_q
import db.queries.users as users_q

from utils.enums import AccountStatus, AccountType, normalize_enum_value
from utils.money import to_minor_units


ACTIVE_ACCOUNT_NAME_ERROR = "An active account with this name already exists. Change the name into something else."


def _with_current_balance(account: dict):
    transactions = transactions_q.get_transactions_by_account(account["account_id"])
    transaction_total = sum(transaction["amount_minor"] for transaction in transactions)

    return {
        **account,
        "current_balance_minor": account["opening_balance_minor"] + transaction_total,
    }


def get_accounts(user_id: int, active_only: bool = True):
    accounts = accounts_q.get_accounts(user_id, active_only=active_only)
    return [_with_current_balance(account) for account in accounts]


def get_account(account_id: int):
    account = accounts_q.get_account(account_id)
    return _with_current_balance(account) if account else None


def create_account(user_id: int, name: str, type: str, opening_balance=0):
    name = name.strip()

    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    if not name:
        raise ValueError("Account name is required")

    if accounts_q.get_active_account_by_name(user_id, name) is not None:
        raise ValueError(ACTIVE_ACCOUNT_NAME_ERROR)

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
    account = accounts_q.get_account(account_id)

    if account is None:
        raise ValueError("Account does not exist")

    kwargs = {}
    final_name = account["name"]
    final_status = account["status"]

    if name is not None:
        name = name.strip()

        if not name:
            raise ValueError("Account name cannot be empty")

        kwargs["name"] = name
        final_name = name

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
        final_status = kwargs["status"]

    if (
        final_status == AccountStatus.ACTIVE.value
        and accounts_q.get_active_account_by_name(
            account["user_id"],
            final_name,
            exclude_account_id=account_id,
        ) is not None
    ):
        raise ValueError(ACTIVE_ACCOUNT_NAME_ERROR)

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
