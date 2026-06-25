from datetime import datetime

from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_budgets(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            "SELECT * FROM budget WHERE user_id = ? ORDER BY start_date DESC",
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_budget(budget_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM budget WHERE budget_id = ?",
            (budget_id,),
        ).fetchone()
        return row_to_dict(row)


def create_budget(
    user_id: int,
    name: str,
    period_type: str,
    start_date,
    end_date=None,
):
    with get_conn() as conn:
        cursor = execute(
            conn,
            """
            INSERT INTO budget (
                user_id, name, period_type, start_date, end_date, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, period_type, start_date, end_date, datetime.now()),
        )
        return cursor.lastrowid


def update_budget(budget_id: int, **kwargs):
    allowed = {"name", "period_type", "start_date", "end_date"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update("budget", "budget_id", budget_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)


def delete_budget(budget_id: int):
    with get_conn() as conn:
        execute(conn, "DELETE FROM budget WHERE budget_id = ?", (budget_id,))


def get_budget_item(budget_item_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM budget_item WHERE budget_item_id = ?",
            (budget_item_id,),
        ).fetchone()
        return row_to_dict(row)


def get_budget_items(budget_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            "SELECT * FROM budget_item WHERE budget_id = ? ORDER BY category_id",
            (budget_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def create_budget_item(
    budget_id: int,
    category_id: int,
    planned_amount_minor: int,
    rollover_enabled: bool = False,
):
    with get_conn() as conn:
        cursor = execute(
            conn,
            """
            INSERT INTO budget_item (
                budget_id, category_id, planned_amount_minor, rollover_enabled
            )
            VALUES (?, ?, ?, ?)
            """,
            (budget_id, category_id, planned_amount_minor, rollover_enabled),
        )
        return cursor.lastrowid


def update_budget_item(budget_item_id: int, **kwargs):
    allowed = {"category_id", "planned_amount_minor", "rollover_enabled"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update("budget_item", "budget_item_id", budget_item_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)


def delete_budget_item(budget_item_id: int):
    with get_conn() as conn:
        execute(
            conn,
            "DELETE FROM budget_item WHERE budget_item_id = ?",
            (budget_item_id,),
        )
