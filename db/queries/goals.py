from sqlalchemy import select, insert, update, delete
from db.tables import goal, goal_account
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
        row = conn.execute(
            select(goal).where(goal.c.goal_id == goal_id)
        ).first()

        return dict(row._mapping) if row else None


def create_goal(
    user_id: int,
    name: str,
    target_amount_minor: int,
    target_date=None,
):
    with get_conn() as conn:
        result = conn.execute(
            insert(goal).values(
                user_id=user_id,
                name=name,
                target_amount_minor=target_amount_minor,
                target_date=target_date,
                status="active",
            )
        )
        return result.inserted_primary_key[0]


def update_goal(goal_id: int, **kwargs):
    allowed = {
        "name",
        "target_amount_minor",
        "target_date",
        "status",
    }
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return None

    with get_conn() as conn:
        conn.execute(
            update(goal)
            .where(goal.c.goal_id == goal_id)
            .values(**clean_values)
        )


def get_goal_accounts(goal_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(goal_account)
            .where(goal_account.c.goal_id == goal_id)
        )
        return [dict(row._mapping) for row in result]


def create_goal_account(
    goal_id: int,
    account_id: int,
    allocated_amount_minor: int = 0,
):
    with get_conn() as conn:
        conn.execute(
            insert(goal_account).values(
                goal_id=goal_id,
                account_id=account_id,
                allocated_amount_minor=allocated_amount_minor,
            )
        )


def update_goal_account(
    goal_id: int,
    account_id: int,
    allocated_amount_minor: int,
):
    with get_conn() as conn:
        conn.execute(
            update(goal_account)
            .where(goal_account.c.goal_id == goal_id)
            .where(goal_account.c.account_id == account_id)
            .values(allocated_amount_minor=allocated_amount_minor)
        )


def delete_goal_account(goal_id: int, account_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(goal_account)
            .where(goal_account.c.goal_id == goal_id)
            .where(goal_account.c.account_id == account_id)
        )