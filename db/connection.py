from contextlib import contextmanager
from datetime import datetime
import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "finance.db")

DATE_FIELDS = {
    "created_at",
    "start_date",
    "end_date",
    "next_due_date",
    "target_date",
    "transaction_date",
}

BOOL_FIELDS = {
    "is_system",
    "is_active",
    "rollover_enabled",
}


def _adapt_value(value):
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, bool):
        return int(value)
    return value


def adapt_params(params):
    if params is None:
        return ()
    if isinstance(params, dict):
        return {key: _adapt_value(value) for key, value in params.items()}
    return tuple(_adapt_value(value) for value in params)


def row_to_dict(row):
    if row is None:
        return None

    data = dict(row)

    for field in DATE_FIELDS:
        value = data.get(field)
        if isinstance(value, str):
            data[field] = datetime.fromisoformat(value)

    for field in BOOL_FIELDS:
        if field in data and data[field] is not None:
            data[field] = bool(data[field])

    return data


def rows_to_dicts(rows):
    return [row_to_dict(row) for row in rows]


def execute(conn, sql, params=()):
    return conn.execute(sql, adapt_params(params))


def execute_many(conn, sql, params):
    return conn.executemany(sql, [adapt_params(row) for row in params])


def build_update(table_name: str, key_name: str, key_value, values: dict):
    if not values:
        return None

    assignments = ", ".join(f"{column} = ?" for column in values)
    sql = f"UPDATE {table_name} SET {assignments} WHERE {key_name} = ?"
    params = [*values.values(), key_value]
    return sql, params


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
