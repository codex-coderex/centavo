from sqlalchemy import select, insert, update
from db.tables import goal
from db.connection import get_conn


def get_goals(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(goal)
            .where(goal.c.user_id == user_id)
            .order_by(goal.c.status, goal.c.target_date)
        )
        return [dict(row._mapping) for row in result]


def get_goal(goal_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(goal).where(goal.c.goal_id == goal_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_goal(
    user_id: int,
    name: str,
    target_amount_minor: int,
    account_id: int,
    target_date: str | None = None,
):
    with get_conn() as conn:
        result = conn.execute(
            insert(goal).values(
                user_id=user_id,
                name=name,
                target_amount_minor=target_amount_minor,
                target_date=target_date,
                account_id=account_id,
            )
        )
        return result.inserted_primary_key[0]


def update_goal(goal_id: int, **kwargs):
    allowed = {
        "name",
        "target_amount_minor",
        "account_id",
        "target_date",
        "status",
    }
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return

    with get_conn() as conn:
        conn.execute(
            update(goal)
            .where(goal.c.goal_id == goal_id)
            .values(**clean_values)
        )


def complete_goal(goal_id: int):
    with get_conn() as conn:
        conn.execute(
            update(goal)
            .where(goal.c.goal_id == goal_id)
            .values(status="completed")
        )