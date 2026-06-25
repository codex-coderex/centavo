from datetime import datetime

from db.connection import build_update, execute, get_conn, row_to_dict, rows_to_dicts


def get_transactions_by_user(user_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT "transaction".*
            FROM "transaction"
            JOIN account ON "transaction".account_id = account.account_id
            WHERE account.user_id = ?
            ORDER BY "transaction".transaction_date DESC
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_transactions_by_account(account_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT *
            FROM "transaction"
            WHERE account_id = ?
            ORDER BY transaction_date DESC
            """,
            (account_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_transaction(transaction_id: int):
    with get_conn() as conn:
        row = execute(
            conn,
            'SELECT * FROM "transaction" WHERE transaction_id = ?',
            (transaction_id,),
        ).fetchone()
        return row_to_dict(row)


def create_transaction(
    account_id: int,
    amount_minor: int,
    transaction_date,
    category_id: int,
    budget_item_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
    transfer_id: int | None = None,
):
    with get_conn() as conn:
        return create_transaction_with_conn(
            conn=conn,
            account_id=account_id,
            amount_minor=amount_minor,
            transaction_date=transaction_date,
            category_id=category_id,
            budget_item_id=budget_item_id,
            payee=payee,
            notes=notes,
            recurring_rule_id=recurring_rule_id,
            transfer_id=transfer_id,
        )


def create_transaction_with_conn(
    conn,
    account_id: int,
    amount_minor: int,
    transaction_date,
    category_id: int,
    budget_item_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
    transfer_id: int | None = None,
):
    cursor = execute(
        conn,
        """
        INSERT INTO "transaction" (
            account_id, category_id, budget_item_id, payee, amount_minor,
            transaction_date, notes, created_at, recurring_rule_id, transfer_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            account_id,
            category_id,
            budget_item_id,
            payee,
            amount_minor,
            transaction_date,
            notes,
            datetime.now(),
            recurring_rule_id,
            transfer_id,
        ),
    )
    return cursor.lastrowid


def update_transaction(transaction_id: int, **kwargs):
    with get_conn() as conn:
        update_transaction_with_conn(conn, transaction_id, **kwargs)


def update_transaction_with_conn(conn, transaction_id: int, **kwargs):
    allowed = {
        "account_id",
        "category_id",
        "budget_item_id",
        "payee",
        "amount_minor",
        "transaction_date",
        "notes",
        "recurring_rule_id",
        "transfer_id",
    }
    clean_values = {key: value for key, value in kwargs.items() if key in allowed}

    statement = build_update(
        '"transaction"',
        "transaction_id",
        transaction_id,
        clean_values,
    )
    if statement is None:
        return None

    sql, params = statement
    execute(conn, sql, params)


def delete_transaction(transaction_id: int):
    with get_conn() as conn:
        execute(
            conn,
            'DELETE FROM "transaction" WHERE transaction_id = ?',
            (transaction_id,),
        )


def get_transactions_by_transfer(transfer_id: int):
    with get_conn() as conn:
        rows = execute(
            conn,
            """
            SELECT *
            FROM "transaction"
            WHERE transfer_id = ?
            ORDER BY transaction_id
            """,
            (transfer_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def delete_transactions_by_transfer_with_conn(conn, transfer_id: int):
    execute(
        conn,
        'DELETE FROM "transaction" WHERE transfer_id = ?',
        (transfer_id,),
    )
