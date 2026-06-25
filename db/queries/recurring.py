from datetime import datetime

from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_recurring_rules(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT recurring_rule.*
            FROM recurring_rule
            JOIN account ON recurring_rule.account_id = account.account_id
            WHERE account.user_id = ?
            ORDER BY recurring_rule.next_due_date
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_recurring_rule(recurring_rule_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM recurring_rule WHERE recurring_rule_id = ?",
            (recurring_rule_id,),
        ).fetchone()
        return row_to_dict(row)


def get_due_recurring_rules(as_of=None):
    if as_of is None:
        as_of = datetime.now()

    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT *
            FROM recurring_rule
            WHERE status = 'active' AND next_due_date <= ?
            """,
            (as_of,),
        ).fetchall()
        return rows_to_dicts(rows)


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
    cursor = execute(
        conn,
        """
        INSERT INTO recurring_rule (
            account_id, category_id, name, expected_amount_minor, interval,
            frequency_unit, start_date, next_due_date, end_date, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """,
        (
            account_id,
            category_id,
            name,
            expected_amount_minor,
            interval,
            frequency_unit,
            start_date,
            next_due_date,
            end_date,
        ),
    )
    return cursor.lastrowid


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
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update(
        "recurring_rule",
        "recurring_rule_id",
        recurring_rule_id,
        clean_values,
    )
    if statement is None:
        return None

    sql, params = statement
    execute(conn, sql, params)
