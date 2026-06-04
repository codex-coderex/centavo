from sqlalchemy import select, insert, update
from db.tables import goal, transaction
from db.connection import get_conn
from datetime import datetime

def get_goals(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(goal).where(goal.c.user_id == user_id)
        )
        return [dict(row._mapping) for row in result]

def get_goal(goal_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(goal).where(goal.c.goal_id == goal_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None

def create_goal(user_id: int, name: str, target_amount: float,
                target_date: str = None, account_id: int = None):
    with get_conn() as conn:
        result = conn.execute(
            insert(goal).values(
                user_id=user_id,
                name=name,
                target_amount=target_amount,
                target_date=target_date,
                account_id=account_id,
                status="active"
            )
        )
        return result.inserted_primary_key[0]

def update_goal(goal_id: int, **kwargs):
    with get_conn() as conn:
        conn.execute(
            update(goal)
            .where(goal.c.goal_id == goal_id)
            .values(**kwargs)
        )

def complete_goal(goal_id: int):
    with get_conn() as conn:
        conn.execute(
            update(goal)
            .where(goal.c.goal_id == goal_id)
            .values(status="completed")
        )

def fund_goal(goal_id: int, account_id: int,
              amount: float, txn_date: str):
    with get_conn() as conn:
        # debit the account and link to goal in one transaction
        conn.execute(
            insert(transaction).values(
                account_id=account_id,
                goal_id=goal_id,
                amount=-amount,
                txn_date=txn_date,
                status="cleared",
                needs_review=False,
                updated_at=datetime.now()
            )
        )