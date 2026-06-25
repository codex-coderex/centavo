from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_tags(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            "SELECT * FROM tag WHERE user_id = ? ORDER BY name",
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_tag(tag_id: int):
    with get_conn() as conn:
        row = execute(conn, "SELECT * FROM tag WHERE tag_id = ?", (tag_id,)).fetchone()
        return row_to_dict(row)


def get_tag_by_user_name(user_id: int, name: str, exclude_tag_id: int | None = None):
    sql = """
        SELECT *
        FROM tag
        WHERE user_id = ? AND lower(name) = lower(?)
    """
    params = [user_id, name]

    if exclude_tag_id is not None:
        sql += " AND tag_id != ?"
        params.append(exclude_tag_id)

    with get_conn() as conn:
        row = execute(conn, sql, params).fetchone()
        return row_to_dict(row)


def create_tag(user_id: int, name: str):
    with get_conn() as conn:
        cursor = execute(
            conn,
            "INSERT INTO tag (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
        return cursor.lastrowid


def update_tag(tag_id: int, **kwargs):
    clean_values = {key: value for key, value in kwargs.items() if key == "name"}

    statement = build_update("tag", "tag_id", tag_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)


def delete_tag(tag_id: int):
    with get_conn() as conn:
        execute(conn, "DELETE FROM tag WHERE tag_id = ?", (tag_id,))


def get_transaction_tags(transaction_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT tag.*
            FROM tag
            JOIN transaction_tag ON tag.tag_id = transaction_tag.tag_id
            WHERE transaction_tag.transaction_id = ?
            ORDER BY tag.name
            """,
            (transaction_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def create_transaction_tag(transaction_id: int, tag_id: int):
    with get_conn() as conn:
        execute(
            conn,
            """
            INSERT OR IGNORE INTO transaction_tag (transaction_id, tag_id)
            VALUES (?, ?)
            """,
            (transaction_id, tag_id),
        )


def delete_transaction_tag(transaction_id: int, tag_id: int):
    with get_conn() as conn:
        execute(
            conn,
            "DELETE FROM transaction_tag WHERE transaction_id = ? AND tag_id = ?",
            (transaction_id, tag_id),
        )
