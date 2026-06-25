from datetime import datetime

from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_users():
    with get_conn() as conn:
        rows = execute(conn, "SELECT * FROM user ORDER BY name").fetchall()
        return rows_to_dicts(rows)


def get_user(user_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM user WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return row_to_dict(row)


def create_user(name: str):
    with get_conn() as conn:
        cursor = execute(
            conn,
            "INSERT INTO user (name, created_at) VALUES (?, ?)",
            (name, datetime.now()),
        )
        return cursor.lastrowid
