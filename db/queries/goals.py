from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_goals(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            "SELECT * FROM goal WHERE user_id = ? ORDER BY status, target_date",
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_goal(goal_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM goal WHERE goal_id = ?",
            (goal_id,),
        ).fetchone()
        return row_to_dict(row)


def create_goal(
    user_id: int,
    name: str,
    target_amount_minor: int,
    target_date=None,
):
    with get_conn() as conn:
        cursor = execute(
            conn,
            """
            INSERT INTO goal (user_id, name, target_amount_minor, target_date, status)
            VALUES (?, ?, ?, ?, 'active')
            """,
            (user_id, name, target_amount_minor, target_date),
        )
        return cursor.lastrowid


def update_goal(goal_id: int, **kwargs):
    allowed = {"name", "target_amount_minor", "target_date", "status"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update("goal", "goal_id", goal_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)


def delete_goal(goal_id: int):
    with get_conn() as conn:
        execute(conn, "DELETE FROM goal WHERE goal_id = ?", (goal_id,))


def get_goal_accounts(goal_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            "SELECT * FROM goal_account WHERE goal_id = ?",
            (goal_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_goal_account(goal_id: int, account_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            """
            SELECT *
            FROM goal_account
            WHERE goal_id = ? AND account_id = ?
            """,
            (goal_id, account_id),
        ).fetchone()
        return row_to_dict(row)


def get_goal_accounts_by_account(account_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            "SELECT * FROM goal_account WHERE account_id = ?",
            (account_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_allocated_amount_for_account(account_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            """
            SELECT COALESCE(SUM(allocated_amount_minor), 0) AS allocated_amount_minor
            FROM goal_account
            WHERE account_id = ?
            """,
            (account_id,),
        ).fetchone()
        return row["allocated_amount_minor"]


def create_goal_account(
    goal_id: int,
    account_id: int,
    allocated_amount_minor: int = 0,
):
    with get_conn() as conn:
        execute(
            conn,
            """
            INSERT INTO goal_account (goal_id, account_id, allocated_amount_minor)
            VALUES (?, ?, ?)
            """,
            (goal_id, account_id, allocated_amount_minor),
        )


def update_goal_account(
    goal_id: int,
    account_id: int,
    allocated_amount_minor: int,
):
    with get_conn() as conn:
        execute(
            conn,
            """
            UPDATE goal_account
            SET allocated_amount_minor = ?
            WHERE goal_id = ? AND account_id = ?
            """,
            (allocated_amount_minor, goal_id, account_id),
        )


def delete_goal_account(goal_id: int, account_id: int):
    with get_conn() as conn:
        execute(
            conn,
            "DELETE FROM goal_account WHERE goal_id = ? AND account_id = ?",
            (goal_id, account_id),
        )
