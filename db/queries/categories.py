from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_category_groups(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT *
            FROM category_group
            WHERE user_id = ? AND is_active = 1
            ORDER BY type, name
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_all_category_groups(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT *
            FROM category_group
            WHERE user_id = ?
            ORDER BY type, name
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_category_group(group_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM category_group WHERE group_id = ?",
            (group_id,),
        ).fetchone()
        return row_to_dict(row)


def get_category_group_by_user_type_name(
    user_id: int,
    type: str,
    name: str,
    exclude_group_id: int | None = None,
):
    sql = """
        SELECT *
        FROM category_group
        WHERE user_id = ? AND type = ? AND lower(name) = lower(?)
    """
    params = [user_id, type, name]

    if exclude_group_id is not None:
        sql += " AND group_id != ?"
        params.append(exclude_group_id)

    with get_conn() as conn:
        row = execute(conn, sql, params).fetchone()
        return row_to_dict(row)


def get_categories_by_group(group_id: int, active_only: bool = False):
    sql = "SELECT * FROM category WHERE group_id = ?"
    params = [group_id]

    if active_only:
        sql += " AND is_active = 1"

    sql += " ORDER BY name"

    with get_conn() as conn:
        rows = execute(conn, sql, params).fetchall()
        return rows_to_dicts(rows)


def get_all_categories(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT category.*
            FROM category
            JOIN category_group ON category.group_id = category_group.group_id
            WHERE category_group.user_id = ?
                AND category_group.is_active = 1
                AND category.is_active = 1
            ORDER BY category_group.type, category.name
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_all_categories_for_user(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT category.*
            FROM category
            JOIN category_group ON category.group_id = category_group.group_id
            WHERE category_group.user_id = ?
            ORDER BY category_group.type, category.name
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_category(category_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            "SELECT * FROM category WHERE category_id = ?",
            (category_id,),
        ).fetchone()
        return row_to_dict(row)


def get_category_by_group_name(
    group_id: int,
    name: str,
    exclude_category_id: int | None = None,
):
    sql = """
        SELECT *
        FROM category
        WHERE group_id = ? AND lower(name) = lower(?)
    """
    params = [group_id, name]

    if exclude_category_id is not None:
        sql += " AND category_id != ?"
        params.append(exclude_category_id)

    with get_conn() as conn:
        row = execute(conn, sql, params).fetchone()
        return row_to_dict(row)


def create_category_group(
    user_id: int,
    name: str,
    type: str,
    is_system: bool = False,
):
    with get_conn() as conn:
        cursor = execute(
            conn,
            """
            INSERT INTO category_group (user_id, name, type, is_system, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (user_id, name, type, is_system),
        )
        return cursor.lastrowid


def create_category(
    group_id: int,
    name: str,
    is_system: bool = False,
):
    with get_conn() as conn:
        cursor = execute(
            conn,
            """
            INSERT INTO category (group_id, name, is_system, is_active)
            VALUES (?, ?, ?, 1)
            """,
            (group_id, name, is_system),
        )
        return cursor.lastrowid


def update_category_group(group_id: int, **kwargs):
    allowed = {"name", "type", "is_active"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update("category_group", "group_id", group_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)


def update_category(category_id: int, **kwargs):
    allowed = {"name", "is_active"}
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update("category", "category_id", category_id, clean_values)
    if statement is None:
        return None

    sql, params = statement
    with get_conn() as conn:
        execute(conn, sql, params)


def delete_category_group(group_id: int):
    with get_conn() as conn:
        execute(conn, "DELETE FROM category_group WHERE group_id = ?", (group_id,))


def delete_category(category_id: int):
    with get_conn() as conn:
        execute(conn, "DELETE FROM category WHERE category_id = ?", (category_id,))


def delete_categories_by_group(group_id: int):
    with get_conn() as conn:
        execute(conn, "DELETE FROM category WHERE group_id = ?", (group_id,))


def category_has_references(category_id: int) -> bool:
    with get_conn() as conn:
        for sql in (
            'SELECT transaction_id FROM "transaction" WHERE category_id = ? LIMIT 1',
            "SELECT budget_item_id FROM budget_item WHERE category_id = ? LIMIT 1",
            "SELECT recurring_rule_id FROM recurring_rule WHERE category_id = ? LIMIT 1",
        ):
            if execute(conn, sql, (category_id,)).fetchone() is not None:
                return True

    return False


def get_category_reference_counts(category_id: int):
    with get_conn() as conn:
        transaction_count = execute(
            conn,
            'SELECT COUNT(*) AS count FROM "transaction" WHERE category_id = ?',
            (category_id,),
        ).fetchone()["count"]
        budget_item_count = execute(
            conn,
            "SELECT COUNT(*) AS count FROM budget_item WHERE category_id = ?",
            (category_id,),
        ).fetchone()["count"]
        recurring_count = execute(
            conn,
            "SELECT COUNT(*) AS count FROM recurring_rule WHERE category_id = ?",
            (category_id,),
        ).fetchone()["count"]

    return {
        "transactions": transaction_count,
        "budget_items": budget_item_count,
        "recurring": recurring_count,
    }


def group_has_referenced_categories(group_id: int) -> bool:
    sql_statements = (
        """
        SELECT "transaction".transaction_id
        FROM "transaction"
        WHERE category_id IN (
            SELECT category_id FROM category WHERE group_id = ?
        )
        LIMIT 1
        """,
        """
        SELECT budget_item.budget_item_id
        FROM budget_item
        WHERE category_id IN (
            SELECT category_id FROM category WHERE group_id = ?
        )
        LIMIT 1
        """,
        """
        SELECT recurring_rule.recurring_rule_id
        FROM recurring_rule
        WHERE category_id IN (
            SELECT category_id FROM category WHERE group_id = ?
        )
        LIMIT 1
        """,
    )

    with get_conn() as conn:
        for sql in sql_statements:
            if execute(conn, sql, (group_id,)).fetchone() is not None:
                return True

    return False
