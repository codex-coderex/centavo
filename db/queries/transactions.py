from sqlalchemy import select, insert, update
from db.tables import transaction, account
from db.connection import get_conn
from datetime import datetime


def get_transactions_by_user(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction)
            .join(account, transaction.c.account_id == account.c.account_id)
            .where(account.c.user_id == user_id)
            .order_by(transaction.c.txn_date.desc())
        )
        return [dict(row._mapping) for row in result]


def get_transactions_by_account(account_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction)
            .where(transaction.c.account_id == account_id)
            .order_by(transaction.c.txn_date.desc())
        )
        return [dict(row._mapping) for row in result]


def get_transaction(transaction_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction)
            .where(transaction.c.transaction_id == transaction_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_transaction(
    account_id: int,
    amount_minor: int,
    txn_date: str,
    category_id: int,
    merchant: str | None = None,
    note: str | None = None,
    goal_id: int | None = None,
    recurring_id: int | None = None,
):
    with get_conn() as conn:
        return create_transaction_with_conn(
            conn,
            account_id,
            amount_minor,
            txn_date,
            category_id,
            merchant,
            note,
            goal_id,
            recurring_id,
        )


def create_transaction_with_conn(
    conn,
    account_id: int,
    amount_minor: int,
    txn_date: str,
    category_id: int,
    merchant: str | None = None,
    note: str | None = None,
    goal_id: int | None = None,
    recurring_id: int | None = None,
):
    result = conn.execute(
        insert(transaction).values(
            account_id=account_id,
            amount_minor=amount_minor,
            txn_date=txn_date,
            category_id=category_id,
            merchant=merchant,
            note=note,
            goal_id=goal_id,
            recurring_id=recurring_id,
        )
    )
    return result.inserted_primary_key[0]


def update_transaction(transaction_id: int, **kwargs):
    with get_conn() as conn:
        update_transaction_with_conn(conn, transaction_id, **kwargs)


def update_transaction_with_conn(conn, transaction_id: int, **kwargs):
    allowed = {
        "account_id",
        "amount_minor",
        "txn_date",
        "category_id",
        "merchant",
        "note",
        "goal_id",
        "recurring_id",
        "transfer_pair_id",
        "status",
        "needs_review",
    }

    clean_values = {k: v for k, v in kwargs.items() if k in allowed}
    clean_values["updated_at"] = datetime.now()

    conn.execute(
        update(transaction)
        .where(transaction.c.transaction_id == transaction_id)
        .values(**clean_values)
    )