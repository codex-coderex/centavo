from sqlalchemy import select, insert, update
from db.tables import recurring, account
from db.connection import get_conn
from datetime import datetime


def get_recurring(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(recurring)
            .join(account, recurring.c.account_id == account.c.account_id)
            .where(account.c.user_id == user_id)
        )
        return [dict(row._mapping) for row in result]


def get_recurring_by_id(recurring_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(recurring)
            .where(recurring.c.recurring_id == recurring_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def get_due_recurring():
    with get_conn() as conn:
        result = conn.execute(
            select(recurring)
            .where(recurring.c.status == "active")
            .where(recurring.c.next_due <= datetime.now())
        )
        return [dict(row._mapping) for row in result]


def create_recurring(
    account_id: int,
    amount_minor: int,
    interval: int,
    frequency_unit: str,
    next_due: str,
    category_id: int,
    merchant: str | None = None,
    end_date: str | None = None,
):
    with get_conn() as conn:
        result = conn.execute(
            insert(recurring).values(
                account_id=account_id,
                amount_minor=amount_minor,
                interval=interval,
                frequency_unit=frequency_unit,
                next_due=next_due,
                category_id=category_id,
                merchant=merchant,
                end_date=end_date,
                status="active",
            )
        )
        return result.inserted_primary_key[0]


def update_recurring(recurring_id: int, **kwargs):
    with get_conn() as conn:
        conn.execute(
            update(recurring)
            .where(recurring.c.recurring_id == recurring_id)
            .values(**kwargs)
        )


def pause_recurring(recurring_id: int):
    update_recurring(recurring_id, status="paused")


def resume_recurring(recurring_id: int):
    update_recurring(recurring_id, status="active")


def deactivate_recurring(recurring_id: int):
    update_recurring(recurring_id, status="inactive")