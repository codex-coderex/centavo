from datetime import datetime

from sqlalchemy import select, insert, update
from db.tables import user
from db.connection import get_conn


def get_users():
    with get_conn() as conn:
        result = conn.execute(
            select(user).order_by(user.c.name)
        )
        return [dict(row._mapping) for row in result]


def get_user(user_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(user).where(user.c.user_id == user_id)
        ).first()

        return dict(row._mapping) if row else None


def create_user(name: str):
    with get_conn() as conn:
        result = conn.execute(
            insert(user).values(
                name=name,
                created_at=datetime.now(),
            )
        )
        return result.inserted_primary_key[0]


def update_user(user_id: int, **kwargs):
    allowed = {"name"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return None

    with get_conn() as conn:
        conn.execute(
            update(user)
            .where(user.c.user_id == user_id)
            .values(**clean_values)
        )