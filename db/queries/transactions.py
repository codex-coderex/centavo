from datetime import datetime

from sqlalchemy import select, insert, update, delete
from db.tables import transaction, account
from db.connection import get_conn


def get_transactions_by_user(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction)
            .join(account, transaction.c.account_id == account.c.account_id)
            .where(account.c.user_id == user_id)
            .order_by(transaction.c.transaction_date.desc())
        )
        return [dict(row._mapping) for row in result]


def get_transactions_by_account(account_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction)
            .where(transaction.c.account_id == account_id)
            .order_by(transaction.c.transaction_date.desc())
        )
        return [dict(row._mapping) for row in result]


def get_transaction(transaction_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(transaction)
            .where(transaction.c.transaction_id == transaction_id)
        ).first()

        return dict(row._mapping) if row else None


def create_transaction(
    account_id: int,
    amount_minor: int,
    transaction_date,
    category_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
    transfer_id: int | None = None,
):
    with get_conn() as conn:
        return create_transaction_with_conn(
            conn=conn,
            account_id=account_id,
            amount_minor=amount_minor,
            transaction_date=transaction_date,
            category_id=category_id,
            payee=payee,
            notes=notes,
            recurring_rule_id=recurring_rule_id,
            transfer_id=transfer_id,
        )


def create_transaction_with_conn(
    conn,
    account_id: int,
    amount_minor: int,
    transaction_date,
    category_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
    transfer_id: int | None = None,
):
    result = conn.execute(
        insert(transaction).values(
            account_id=account_id,
            category_id=category_id,
            recurring_rule_id=recurring_rule_id,
            payee=payee,
            amount_minor=amount_minor,
            transaction_date=transaction_date,
            notes=notes,
            created_at=datetime.now(),
            transfer_id=transfer_id,
        )
    )
    return result.inserted_primary_key[0]


def update_transaction(transaction_id: int, **kwargs):
    with get_conn() as conn:
        update_transaction_with_conn(conn, transaction_id, **kwargs)


def update_transaction_with_conn(conn, transaction_id: int, **kwargs):
    allowed = {
        "account_id",
        "category_id",
        "recurring_rule_id",
        "payee",
        "amount_minor",
        "transaction_date",
        "notes",
        "transfer_id",
    }
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return None

    conn.execute(
        update(transaction)
        .where(transaction.c.transaction_id == transaction_id)
        .values(**clean_values)
    )


def delete_transaction(transaction_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(transaction)
            .where(transaction.c.transaction_id == transaction_id)
        )