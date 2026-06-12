from sqlalchemy import select, insert, update
from db.tables import user
from db.connection import get_conn
from datetime import datetime


def get_users():
    with get_conn() as conn:
        result = conn.execute(select(user))
        return [dict(row._mapping) for row in result]


def get_user(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(user).where(user.c.user_id == user_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_user(name: str, currency_code: str):
    with get_conn() as conn:
        result = conn.execute(
            insert(user).values(
                name=name,
                currency_code=currency_code.upper(),
                created_at=datetime.now(),
            )
        )
        return result.inserted_primary_key[0]


def update_user(user_id: int, **kwargs):
    allowed = {"name", "currency_code"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if "currency_code" in clean_values and clean_values["currency_code"]:
        clean_values["currency_code"] = clean_values["currency_code"].upper()

    if not clean_values:
        return

    with get_conn() as conn:
        conn.execute(
            update(user)
            .where(user.c.user_id == user_id)
            .values(**clean_values)
        )