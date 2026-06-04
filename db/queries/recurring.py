from sqlalchemy import select, insert, update
from db.tables import recurring, transaction, account
from db.connection import get_conn
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_recurring(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(recurring)
            .join(account, recurring.c.account_id == account.c.account_id)
            .where(account.c.user_id == user_id)
        )
        return [dict(row._mapping) for row in result]

def get_due_recurring():
    with get_conn() as conn:
        result = conn.execute(
            select(recurring)
            .where(recurring.c.status == "active")
            .where(recurring.c.next_due <= datetime.now())
        )
        return [dict(row._mapping) for row in result]

def create_recurring(account_id: int, amount: float,
                    interval: int, frequency_unit: str, next_due: str,
                     category_id: int = None, merchant: str = None,
                     end_date: str = None):
    with get_conn() as conn:
        result = conn.execute(
            insert(recurring).values(
                account_id=account_id,
                amount=amount,
                interval=interval,
                frequency_unit=frequency_unit,
                next_due=next_due,
                category_id=category_id,
                merchant=merchant,
                end_date=end_date,
                status="active"
            )
        )
        return result.inserted_primary_key[0]

def generate_transaction(recurring_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(recurring).where(recurring.c.recurring_id == recurring_id)
        ).first()

        if not row:
            return None

        r = dict(row._mapping)

        # create the transaction
        conn.execute(
            insert(transaction).values(
                account_id=r["account_id"],
                category_id=r["category_id"],
                recurring_id=recurring_id,
                merchant=r["merchant"],
                amount=r["amount"],
                txn_date=datetime.now(),
                status="cleared",
                needs_review=False,
                updated_at=datetime.now()
            )
        )

        # calculate next due date
        next_due = _next_due(r["next_due"], r["interval"], r["frequency_unit"])

        # deactivate if past end date
        if r["end_date"] and next_due > r["end_date"]:
            conn.execute(
                update(recurring)
                .where(recurring.c.recurring_id == recurring_id)
                .values(status="inactive")
            )
        else:
            conn.execute(
                update(recurring)
                .where(recurring.c.recurring_id == recurring_id)
                .values(next_due=next_due)
            )

def pause_recurring(recurring_id: int):
    with get_conn() as conn:
        conn.execute(
            update(recurring)
            .where(recurring.c.recurring_id == recurring_id)
            .values(status="paused")
        )

def resume_recurring(recurring_id: int):
    with get_conn() as conn:
        conn.execute(
            update(recurring)
            .where(recurring.c.recurring_id == recurring_id)
            .values(status="active")
        )

def _next_due(current_due: datetime, interval: int, frequency_unit: str) -> datetime:
    if isinstance(current_due, str):
        current_due = datetime.fromisoformat(current_due)
    match frequency_unit:
        case "day":   return current_due + relativedelta(days=interval)
        case "week":  return current_due + relativedelta(weeks=interval)
        case "month": return current_due + relativedelta(months=interval)
        case "year":  return current_due + relativedelta(years=interval)
        case _:
            raise ValueError(f"Unknown frequency_unit: {frequency_unit}")