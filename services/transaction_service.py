from db.connection import get_conn

import db.queries.transactions as transactions_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q

from utils.money import to_minor_units
from utils.dates import require_datetime


def get_transactions_by_user(user_id: int):
    return transactions_q.get_transactions_by_user(user_id)


def get_transactions_by_account(account_id: int):
    return transactions_q.get_transactions_by_account(account_id)


def get_transaction(transaction_id: int):
    return transactions_q.get_transaction(transaction_id)


def _get_account(account_id: int):
    account = accounts_q.get_account(account_id)
    if account is None:
        raise ValueError("Account does not exist")
    return account


def _ensure_active_account(account_id: int):
    account = _get_account(account_id)
    if account["status"] != "active":
        raise ValueError("Account is archived")
    return account


def _ensure_active_category(category_id: int):
    category = categories_q.get_category(category_id)
    if category is None:
        raise ValueError("Category does not exist")
    if not category["is_active"]:
        raise ValueError("Category is inactive")
    return category


def create_transaction(
    account_id: int,
    amount,
    transaction_date,
    category_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
):
    _ensure_active_account(account_id)

    if category_id is not None:
        _ensure_active_category(category_id)

    amount_minor = to_minor_units(amount)
    if amount_minor == 0:
        raise ValueError("Transaction amount cannot be zero")

    transaction_date = require_datetime(transaction_date, "Transaction date")

    transaction_id = transactions_q.create_transaction(
        account_id=account_id,
        amount_minor=amount_minor,
        transaction_date=transaction_date,
        category_id=category_id,
        payee=payee,
        notes=notes,
        recurring_rule_id=recurring_rule_id,
        transfer_id=None,
    )
    return {"transaction_id": transaction_id}


def create_transfer(
    from_account_id: int,
    to_account_id: int,
    amount,
    transaction_date,
    payee: str | None = "Transfer",
    notes: str | None = None,
):
    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer to the same account")

    from_account = _ensure_active_account(from_account_id)
    to_account = _ensure_active_account(to_account_id)

    if from_account["user_id"] != to_account["user_id"]:
        raise ValueError("Cannot transfer between accounts owned by different users")

    amount_minor = to_minor_units(amount)
    if amount_minor <= 0:
        raise ValueError("Transfer amount must be greater than zero")

    transaction_date = require_datetime(transaction_date, "Transaction date")

    with get_conn() as conn:
        debit_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=from_account_id,
            amount_minor=-amount_minor,
            transaction_date=transaction_date,
            category_id=None,
            payee=payee,
            notes=notes,
            recurring_rule_id=None,
            transfer_id=None,
        )

        credit_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=to_account_id,
            amount_minor=amount_minor,
            transaction_date=transaction_date,
            category_id=None,
            payee=payee,
            notes=notes,
            recurring_rule_id=None,
            transfer_id=debit_id,
        )

        transactions_q.update_transaction_with_conn(
            conn,
            debit_id,
            transfer_id=debit_id,
        )

    return {
        "transfer_id": debit_id,
        "debit_transaction_id": debit_id,
        "credit_transaction_id": credit_id,
    }


def update_transaction(
    transaction_id: int,
    account_id: int | None = None,
    amount=None,
    transaction_date=None,
    category_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
):
    transaction = transactions_q.get_transaction(transaction_id)
    if transaction is None:
        raise ValueError("Transaction does not exist")

    kwargs = {}
    if account_id is not None:
        _ensure_active_account(account_id)
        kwargs["account_id"] = account_id
    if amount is not None:
        amount_minor = to_minor_units(amount)
        if amount_minor == 0:
            raise ValueError("Transaction amount cannot be zero")
        kwargs["amount_minor"] = amount_minor
    if transaction_date is not None:
        kwargs["transaction_date"] = require_datetime(transaction_date, "Transaction date")
    if category_id is not None:
        _ensure_active_category(category_id)
        kwargs["category_id"] = category_id
    if payee is not None:
        kwargs["payee"] = payee
    if notes is not None:
        kwargs["notes"] = notes
    if recurring_rule_id is not None:
        kwargs["recurring_rule_id"] = recurring_rule_id

    if kwargs:
        transactions_q.update_transaction(transaction_id, **kwargs)
    return {"status": "updated"}


def delete_transaction(transaction_id: int):
    if transactions_q.get_transaction(transaction_id) is None:
        raise ValueError("Transaction does not exist")
    transactions_q.delete_transaction(transaction_id)
    return {"status": "deleted"}
