from datetime import datetime

from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_accounts(user_id: int, active_only: bool = True):
    sql = "SELECT * FROM account WHERE user_id = ?"
    params = [user_id]

    if active_only:
        sql += " AND status = ?"
        params.append("active")

    sql += " ORDER BY name"

    with get_conn() as conn:
        rows = execute(conn, sql, params).fetchall()
        return rows_to_dicts(rows)


def get_account(account_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM account WHERE account_id = ?",
            (account_id,),
        ).fetchone()
        return row_to_dict(row)


def get_active_account_by_name(user_id: int, name: str, exclude_account_id: int | None = None):
    sql = """
        SELECT *
        FROM account
        WHERE user_id = ? AND name = ? AND status = 'active'
    """
    params = [user_id, name]

    if exclude_account_id is not None:
        sql += " AND account_id != ?"
        params.append(exclude_account_id)

    with get_conn() as conn:
        row = execute(conn, sql, params).fetchone()
        return row_to_dict(row)


def create_account(
    user_id: int,
    name: str,
    type: str,
    opening_balance_minor: int = 0,
):
    with get_conn() as conn:
        cursor = execute(
            conn,
            """
            INSERT INTO account (
                user_id, name, type, opening_balance_minor, created_at, status
            )
            VALUES (?, ?, ?, ?, ?, 'active')
            """,
            (user_id, name, type, opening_balance_minor, datetime.now()),
        )
        return cursor.lastrowid


def update_account(account_id: int, **kwargs):
    allowed = {"name", "type", "opening_balance_minor", "status"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update("account", "account_id", account_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)
