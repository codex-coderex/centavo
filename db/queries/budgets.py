from sqlalchemy import select, insert, update, delete
from db.tables import budget, budget_item
from db.connection import get_conn


def get_budgets(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(budget)
            .where(budget.c.user_id == user_id)
            .order_by(budget.c.start_date.desc())
        )
        return [dict(row._mapping) for row in result]


def get_budget(budget_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(budget).where(budget.c.budget_id == budget_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_budget(
    user_id: int,
    name: str,
    period: str,
    start_date: str,
    end_date: str | None = None,
):
    with get_conn() as conn:
        result = conn.execute(
            insert(budget).values(
                user_id=user_id,
                name=name,
                period=period,
                start_date=start_date,
                end_date=end_date,
            )
        )
        return result.inserted_primary_key[0]


def update_budget(budget_id: int, **kwargs):
    allowed = {"name", "period", "start_date", "end_date"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return

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
        result = conn.execute(
            select(budget_item)
            .where(budget_item.c.budget_item_id == budget_item_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def get_budget_items(budget_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(budget_item)
            .where(budget_item.c.budget_id == budget_id)
        )
        return [dict(row._mapping) for row in result]


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
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return

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