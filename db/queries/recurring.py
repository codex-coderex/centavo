from datetime import datetime

from sqlalchemy import select, insert, update
from db.tables import recurring_rule, account
from db.connection import get_conn


def get_recurring_rules(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(recurring_rule)
            .join(account, recurring_rule.c.account_id == account.c.account_id)
            .where(account.c.user_id == user_id)
            .order_by(recurring_rule.c.next_due_date)
        )
        return [dict(row._mapping) for row in result]


def get_recurring_rule(recurring_rule_id: int):
    with get_conn() as conn:
        row = conn.execute(
            select(recurring_rule)
            .where(recurring_rule.c.recurring_rule_id == recurring_rule_id)
        ).first()

        return dict(row._mapping) if row else None


def get_due_recurring_rules(as_of=None):
    if as_of is None:
        as_of = datetime.now()

    with get_conn() as conn:
        result = conn.execute(
            select(recurring_rule)
            .where(recurring_rule.c.status == "active")
            .where(recurring_rule.c.next_due_date <= as_of)
        )
        return [dict(row._mapping) for row in result]


def create_recurring_rule(
    account_id: int,
    category_id: int,
    name: str,
    expected_amount_minor: int,
    interval: int,
    frequency_unit: str,
    start_date,
    next_due_date,
    end_date=None,
):
    with get_conn() as conn:
        return create_recurring_rule_with_conn(
            conn=conn,
            account_id=account_id,
            category_id=category_id,
            name=name,
            expected_amount_minor=expected_amount_minor,
            interval=interval,
            frequency_unit=frequency_unit,
            start_date=start_date,
            next_due_date=next_due_date,
            end_date=end_date,
        )


def create_recurring_rule_with_conn(
    conn,
    account_id: int,
    category_id: int,
    name: str,
    expected_amount_minor: int,
    interval: int,
    frequency_unit: str,
    start_date,
    next_due_date,
    end_date=None,
):
    result = conn.execute(
        insert(recurring_rule).values(
            account_id=account_id,
            category_id=category_id,
            name=name,
            expected_amount_minor=expected_amount_minor,
            interval=interval,
            frequency_unit=frequency_unit,
            start_date=start_date,
            next_due_date=next_due_date,
            end_date=end_date,
            status="active",
        )
    )
    return result.inserted_primary_key[0]


def update_recurring_rule(recurring_rule_id: int, **kwargs):
    with get_conn() as conn:
        update_recurring_rule_with_conn(conn, recurring_rule_id, **kwargs)


def update_recurring_rule_with_conn(conn, recurring_rule_id: int, **kwargs):
    allowed = {
        "account_id",
        "category_id",
        "name",
        "expected_amount_minor",
        "interval",
        "frequency_unit",
        "start_date",
        "next_due_date",
        "end_date",
        "status",
    }

    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return None

    conn.execute(
        update(recurring_rule)
        .where(recurring_rule.c.recurring_rule_id == recurring_rule_id)
        .values(**clean_values)
    )

