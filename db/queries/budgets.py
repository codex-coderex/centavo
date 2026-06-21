from datetime import datetime

from sqlalchemy import select, insert, update, delete
from db.connection import get_conn
from db.tables import budget, budget_item


def _row_to_dict(row):
    return dict(row._mapping) if row else None


def _rows_to_dicts(rows):
    return [dict(row._mapping) for row in rows]


def get_budgets(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(budget)
            .where(budget.c.user_id == user_id)
            .order_by(budget.c.start_date.desc())
        )
        return _rows_to_dicts(result)


def get_budget(budget_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(budget).where(budget.c.budget_id == budget_id)
        ).first()

        return _row_to_dict(row)


def get_budget_for_user(user_id: int, budget_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(budget)
            .where(budget.c.budget_id == budget_id)
            .where(budget.c.user_id == user_id)
        ).first()

        return _row_to_dict(row)


def create_budget(
    user_id: int,
    name: str,
    period_type: str,
    start_date,
    end_date=None,
):
    with get_conn() as conn:
        result = conn.execute(
            insert(budget).values(
                user_id=user_id,
                name=name,
                period_type=period_type,
                start_date=start_date,
                end_date=end_date,
                created_at=datetime.now(),
            )
        )
        return result.inserted_primary_key[0]


def update_budget(budget_id: int, **kwargs):
    allowed = {"name", "period_type", "start_date", "end_date"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    if not clean_values:
        return None

    with get_conn() as conn:
        conn.execute(
            update(budget)
            .where(budget.c.budget_id == budget_id)
            .values(**clean_values)
        )


def delete_budget(budget_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(budget).where(budget.c.budget_id == budget_id)
        )


def get_budget_item(budget_item_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(budget_item)
            .where(budget_item.c.budget_item_id == budget_item_id)
        ).first()

        return _row_to_dict(row)


def get_budget_items(budget_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(budget_item)
            .where(budget_item.c.budget_id == budget_id)
            .order_by(budget_item.c.category_id)
        )
        return _rows_to_dicts(result)


def get_budget_item_for_category(budget_id: int, category_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(budget_item)
            .where(budget_item.c.budget_id == budget_id)
            .where(budget_item.c.category_id == category_id)
        ).first()

        return _row_to_dict(row)


def create_budget_item(
    budget_id: int,
    category_id: int,
    planned_amount_minor: int,
    rollover_enabled: bool = False,
):
    with get_conn() as conn:
        result = conn.execute(
            insert(budget_item).values(
                budget_id=budget_id,
                category_id=category_id,
                planned_amount_minor=planned_amount_minor,
                rollover_enabled=rollover_enabled,
            )
        )
        return result.inserted_primary_key[0]


def update_budget_item(budget_item_id: int, **kwargs):
    allowed = {"category_id", "planned_amount_minor", "rollover_enabled"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    if not clean_values:
        return None

    with get_conn() as conn:
        conn.execute(
            update(budget_item)
            .where(budget_item.c.budget_item_id == budget_item_id)
            .values(**clean_values)
        )


def delete_budget_item(budget_item_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(budget_item)
            .where(budget_item.c.budget_item_id == budget_item_id)
        )


def delete_budget_items(budget_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(budget_item)
            .where(budget_item.c.budget_id == budget_id)
        )
