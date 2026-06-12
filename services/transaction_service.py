from db.connection import get_conn
import db.queries.transactions as transactions_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q
from services.currency_service import get_account_decimal_places
from utils.money import to_minor_units
from utils.enums import TransactionStatus, normalize_enum_value


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


def _ensure_category_exists(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if not category["is_active"]:
        raise ValueError("Category is inactive")

    return category


def create_transaction(
    account_id: int,
    amount,
    txn_date: str,
    category_id: int,
    merchant: str | None = None,
    note: str | None = None,
    goal_id: int | None = None,
    recurring_id: int | None = None,
):
    _get_account(account_id)
    _ensure_category_exists(category_id)

    decimal_places = get_account_decimal_places(account_id)
    amount_minor = to_minor_units(amount, decimal_places)

    transaction_id = transactions_q.create_transaction(
        account_id=account_id,
        amount_minor=amount_minor,
        txn_date=txn_date,
        category_id=category_id,
        merchant=merchant,
        note=note,
        goal_id=goal_id,
        recurring_id=recurring_id,
    )

    return {"transaction_id": transaction_id}


def create_transfer(
    from_account_id: int,
    to_account_id: int,
    amount,
    txn_date: str,
    category_id: int,
):
    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer to the same account")

    from_account = _get_account(from_account_id)
    to_account = _get_account(to_account_id)

    if from_account["user_id"] != to_account["user_id"]:
        raise ValueError("Cannot transfer between accounts owned by different users")

    _ensure_category_exists(category_id)

    decimal_places = get_account_decimal_places(from_account_id)
    amount_minor = to_minor_units(amount, decimal_places)

    if amount_minor <= 0:
        raise ValueError("Transfer amount must be greater than zero")

    with get_conn() as conn:
        debit_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=from_account_id,
            amount_minor=-amount_minor,
            txn_date=txn_date,
            category_id=category_id,
        )

        credit_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=to_account_id,
            amount_minor=amount_minor,
            txn_date=txn_date,
            category_id=category_id,
        )

        transactions_q.update_transaction_with_conn(
            conn,
            debit_id,
            transfer_pair_id=credit_id,
        )

        transactions_q.update_transaction_with_conn(
            conn,
            credit_id,
            transfer_pair_id=debit_id,
        )

    return {
        "debit_transaction_id": debit_id,
        "credit_transaction_id": credit_id,
    }


def update_transaction(
    transaction_id: int,
    merchant: str | None = None,
    amount=None,
    category_id: int | None = None,
    note: str | None = None,
    status: str | None = None,
    needs_review: bool | None = None,
    txn_date: str | None = None,
):
    transaction = transactions_q.get_transaction(transaction_id)

    if transaction is None:
        raise ValueError("Transaction does not exist")

    kwargs = {}

    if merchant is not None:
        kwargs["merchant"] = merchant

    if amount is not None:
        decimal_places = get_account_decimal_places(transaction["account_id"])
        kwargs["amount_minor"] = to_minor_units(amount, decimal_places)

    if category_id is not None:
        _ensure_category_exists(category_id)
        kwargs["category_id"] = category_id

    if note is not None:
        kwargs["note"] = note

    if status is not None:
        kwargs["status"] = normalize_enum_value(
            status,
            TransactionStatus,
            "Invalid transaction status",
        )

    if needs_review is not None:
        kwargs["needs_review"] = needs_review

    if txn_date is not None:
        kwargs["txn_date"] = txn_date

    if kwargs:
        transactions_q.update_transaction(transaction_id, **kwargs)


def flag_for_review(transaction_id: int):
    if transactions_q.get_transaction(transaction_id) is None:
        raise ValueError("Transaction does not exist")

    transactions_q.update_transaction(
        transaction_id,
        needs_review=True,
    )