from datetime import datetime, timezone

from db.connection import execute


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def as_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def get_or_create_user(conn, name: str = "Me") -> int:
    row = execute(
        conn,
        "SELECT user_id FROM user WHERE name = ?",
        (name,),
    ).fetchone()

    if row is not None:
        return row["user_id"]

    cursor = execute(
        conn,
        "INSERT INTO user (name, created_at) VALUES (?, ?)",
        (name, utc_now()),
    )
    return cursor.lastrowid


def get_or_create_category_group(
    conn,
    *,
    user_id: int,
    name: str,
    type_: str,
    is_system: bool = True,
) -> int:
    row = execute(
        conn,
        """
        SELECT group_id
        FROM category_group
        WHERE user_id = ? AND type = ? AND name = ?
        """,
        (user_id, type_, name),
    ).fetchone()

    if row is not None:
        return row["group_id"]

    cursor = execute(
        conn,
        """
        INSERT INTO category_group (user_id, name, type, is_system, is_active)
        VALUES (?, ?, ?, ?, 1)
        """,
        (user_id, name, type_, is_system),
    )
    return cursor.lastrowid


def get_or_create_category(
    conn,
    *,
    group_id: int,
    name: str,
    is_system: bool = True,
) -> int:
    row = execute(
        conn,
        """
        SELECT category_id
        FROM category
        WHERE group_id = ? AND name = ?
        """,
        (group_id, name),
    ).fetchone()

    if row is not None:
        return row["category_id"]

    cursor = execute(
        conn,
        """
        INSERT INTO category (group_id, name, is_system, is_active)
        VALUES (?, ?, ?, 1)
        """,
        (group_id, name, is_system),
    )
    return cursor.lastrowid


def get_or_create_account(
    conn,
    *,
    user_id: int,
    name: str,
    type_: str,
    opening_balance_minor: int,
) -> int:
    row = execute(
        conn,
        """
        SELECT account_id
        FROM account
        WHERE user_id = ? AND name = ?
        """,
        (user_id, name),
    ).fetchone()

    if row is not None:
        return row["account_id"]

    cursor = execute(
        conn,
        """
        INSERT INTO account (
            user_id, name, type, opening_balance_minor, created_at, status
        )
        VALUES (?, ?, ?, ?, ?, 'active')
        """,
        (user_id, name, type_, opening_balance_minor, utc_now()),
    )
    return cursor.lastrowid


def get_or_create_budget(
    conn,
    *,
    user_id: int,
    name: str,
    period_type: str,
    start_date: str,
    end_date: str,
) -> int:
    start_dt = as_datetime(start_date)
    end_dt = as_datetime(end_date)

    row = execute(
        conn,
        """
        SELECT budget_id
        FROM budget
        WHERE user_id = ? AND name = ? AND start_date = ?
        """,
        (user_id, name, start_dt),
    ).fetchone()

    if row is not None:
        return row["budget_id"]

    cursor = execute(
        conn,
        """
        INSERT INTO budget (
            user_id, name, period_type, start_date, end_date, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, period_type, start_dt, end_dt, utc_now()),
    )
    return cursor.lastrowid


def get_or_create_budget_item(
    conn,
    *,
    budget_id: int,
    category_id: int,
    planned_amount_minor: int,
    rollover_enabled: bool = False,
) -> int:
    row = execute(
        conn,
        """
        SELECT budget_item_id
        FROM budget_item
        WHERE budget_id = ? AND category_id = ?
        """,
        (budget_id, category_id),
    ).fetchone()

    if row is not None:
        return row["budget_item_id"]

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


def get_or_create_recurring_rule(
    conn,
    *,
    account_id: int,
    category_id: int,
    name: str,
    expected_amount_minor: int,
    interval: int,
    frequency_unit: str,
    start_date: str,
    next_due_date: str,
) -> int:
    start_dt = as_datetime(start_date)
    next_due_dt = as_datetime(next_due_date)

    row = execute(
        conn,
        """
        SELECT recurring_rule_id
        FROM recurring_rule
        WHERE account_id = ? AND category_id = ? AND name = ?
        """,
        (account_id, category_id, name),
    ).fetchone()

    if row is not None:
        return row["recurring_rule_id"]

    cursor = execute(
        conn,
        """
        INSERT INTO recurring_rule (
            account_id, category_id, name, expected_amount_minor,
            interval, frequency_unit, start_date, next_due_date, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """,
        (
            account_id,
            category_id,
            name,
            expected_amount_minor,
            interval,
            frequency_unit,
            start_dt,
            next_due_dt,
        ),
    )
    return cursor.lastrowid


def get_or_create_goal(
    conn,
    *,
    user_id: int,
    name: str,
    target_amount_minor: int,
    target_date: str,
) -> int:
    target_dt = as_datetime(target_date)

    row = execute(
        conn,
        """
        SELECT goal_id
        FROM goal
        WHERE user_id = ? AND name = ?
        """,
        (user_id, name),
    ).fetchone()

    if row is not None:
        return row["goal_id"]

    cursor = execute(
        conn,
        """
        INSERT INTO goal (
            user_id, name, target_amount_minor, target_date, status
        )
        VALUES (?, ?, ?, ?, 'active')
        """,
        (user_id, name, target_amount_minor, target_dt),
    )
    return cursor.lastrowid


def link_goal_account(
    conn,
    *,
    goal_id: int,
    account_id: int,
    allocated_amount_minor: int,
) -> None:
    execute(
        conn,
        """
        INSERT OR IGNORE INTO goal_account (
            goal_id, account_id, allocated_amount_minor
        )
        VALUES (?, ?, ?)
        """,
        (goal_id, account_id, allocated_amount_minor),
    )


def insert_sample_transaction(
    conn,
    *,
    account_id: int,
    category_id: int,
    budget_item_id: int | None,
    recurring_rule_id: int | None,
    payee: str,
    amount_minor: int,
    transaction_date: str,
    notes: str,
) -> None:
    txn_dt = as_datetime(transaction_date)

    row = execute(
        conn,
        """
        SELECT transaction_id
        FROM "transaction"
        WHERE account_id = ?
            AND amount_minor = ?
            AND transaction_date = ?
            AND payee = ?
        """,
        (account_id, amount_minor, txn_dt, payee),
    ).fetchone()

    if row is not None:
        return

    execute(
        conn,
        """
        INSERT INTO "transaction" (
            account_id, category_id, budget_item_id, recurring_rule_id,
            payee, amount_minor, transaction_date, notes, created_at, transfer_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            account_id,
            category_id,
            budget_item_id,
            recurring_rule_id,
            payee,
            amount_minor,
            txn_dt,
            notes,
            utc_now(),
        ),
    )