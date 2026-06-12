from sqlalchemy import select, insert, update
from db.tables import account
from db.connection import get_conn


def get_accounts(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(account)
            .where(account.c.user_id == user_id)
            .where(account.c.status == "active")
            .order_by(account.c.name)
        )
        return [dict(row._mapping) for row in result]


def get_account(account_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(account).where(account.c.account_id == account_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_account(user_id: int, name: str, type: str):
    with get_conn() as conn:
        result = conn.execute(
            insert(account).values(
                user_id=user_id,
                name=name,
                type=type,
            )
        )
        return result.inserted_primary_key[0]


def update_account(account_id: int, **kwargs):
    allowed = {"name", "type", "status"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return

    with get_conn() as conn:
        conn.execute(
            update(account)
            .where(account.c.account_id == account_id)
            .values(**clean_values)
        )


def archive_account(account_id: int):
    with get_conn() as conn:
        conn.execute(
            update(account)
            .where(account.c.account_id == account_id)
            .values(status="archived")
        )