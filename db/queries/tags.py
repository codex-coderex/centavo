from sqlalchemy import select, insert, update, delete
from db.tables import tag, transaction_tag
from db.connection import get_conn


def get_tags(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(tag)
            .where(tag.c.user_id == user_id)
            .order_by(tag.c.name)
        )
        return [dict(row._mapping) for row in result]


def get_tag(tag_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(tag).where(tag.c.tag_id == tag_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_tag(user_id: int, name: str, color: str | None = None):
    with get_conn() as conn:
        result = conn.execute(
            insert(tag).values(
                user_id=user_id,
                name=name,
                color=color,
            )
        )
        return result.inserted_primary_key[0]


def update_tag(tag_id: int, **kwargs):
    allowed = {"name", "color"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return

    with get_conn() as conn:
        conn.execute(
            update(tag)
            .where(tag.c.tag_id == tag_id)
            .values(**clean_values)
        )


def delete_tag(tag_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(tag)
            .where(tag.c.tag_id == tag_id)
        )


def get_transaction_tags(transaction_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(tag)
            .join(transaction_tag, tag.c.tag_id == transaction_tag.c.tag_id)
            .where(transaction_tag.c.transaction_id == transaction_id)
            .order_by(tag.c.name)
        )
        return [dict(row._mapping) for row in result]


def add_tag_to_transaction(transaction_id: int, tag_id: int):
    with get_conn() as conn:
        conn.execute(
            insert(transaction_tag)
            .prefix_with("OR IGNORE")
            .values(
                transaction_id=transaction_id,
                tag_id=tag_id,
            )
        )


def remove_tag_from_transaction(transaction_id: int, tag_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(transaction_tag)
            .where(transaction_tag.c.transaction_id == transaction_id)
            .where(transaction_tag.c.tag_id == tag_id)
        )