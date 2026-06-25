from datetime import datetime, timezone

from db.connection import execute, get_conn


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


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


def seed_categories(conn, user_id: int) -> dict[str, int]:
    groups: list[tuple[str, str, list[str]]] = [
        ("Income", "income", [
            "Salary",
            "Freelance",
            "Business",
            "Interest",
            "Gifts Received",
        ]),
        ("Transfer", "transfer", [
            "Account Transfer",
        ]),
        ("Housing", "expense", [
            "Rent",
            "Electricity",
            "Water",
            "Internet",
            "Repairs",
        ]),
        ("Food", "expense", [
            "Groceries",
            "Dining Out",
            "Coffee",
            "Delivery",
        ]),
        ("Transport", "expense", [
            "Fuel",
            "Fare",
            "Parking",
            "Vehicle Maintenance",
        ]),
        ("Health", "expense", [
            "Medical",
            "Pharmacy",
            "Dental",
            "Fitness",
        ]),
        ("Personal", "expense", [
            "Clothing",
            "Grooming",
            "Subscriptions",
            "Education",
        ]),
        ("Family", "expense", [
            "Allowance",
            "Gifts Given",
            "Dependents",
        ]),
        ("Savings & Investment", "expense", [
            "Emergency Fund",
            "Investment",
            "SSS/Pag-IBIG/PhilHealth",
        ]),
        ("Miscellaneous", "expense", [
            "Fees & Charges",
            "Donations",
            "Others",
        ]),
        ("Uncategorized", "expense", [
            "Uncategorized",
        ]),
    ]

    category_ids: dict[str, int] = {}

    for group_name, group_type, category_names in groups:
        group_id = get_or_create_category_group(
            conn,
            user_id=user_id,
            name=group_name,
            type_=group_type,
            is_system=True,
        )

        for category_name in category_names:
            category_id = get_or_create_category(
                conn,
                group_id=group_id,
                name=category_name,
                is_system=True,
            )
            category_ids[category_name] = category_id

    return category_ids


def get_or_create_account(
    conn,
    *,
    user_id: int,
    name: str,
    type_: str = "checking",
    opening_balance_minor: int = 0,
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


def seed_sample_data(conn, user_id: int, category_ids: dict[str, int]) -> None:
    account_id = get_or_create_account(
        conn,
        user_id=user_id,
        name="Main Account",
        type_="checking",
        opening_balance_minor=0,
    )

    sample_transactions = [
        (2_500_000, "2025-01-01", "Company Inc", "Salary"),
        (-150_000, "2025-01-03", "SM Supermarket", "Groceries"),
        (-50_000, "2025-01-05", "Jollibee", "Dining Out"),
        (-300_000, "2025-01-07", "Meralco", "Electricity"),
        (-80_000, "2025-01-10", "Grab", "Fare"),
        (500_000, "2025-01-15", "Client A", "Freelance"),
        (-200_000, "2025-01-18", "Mercury Drug", "Pharmacy"),
        (-120_000, "2025-01-20", "Puregold", "Groceries"),
    ]

    for amount_minor, txn_date, payee, category_name in sample_transactions:
        txn_dt = datetime.fromisoformat(txn_date)
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
            continue

        execute(
            conn,
            """
            INSERT INTO "transaction" (
                account_id, category_id, recurring_rule_id, payee, amount_minor,
                transaction_date, notes, created_at, transfer_id
            )
            VALUES (?, ?, NULL, ?, ?, ?, NULL, ?, NULL)
            """,
            (
                account_id,
                category_ids[category_name],
                payee,
                amount_minor,
                txn_dt,
                utc_now(),
            ),
        )


def run_seed(sample_data: bool = False) -> None:
    with get_conn() as conn:
        user_id = get_or_create_user(conn, "Me")
        category_ids = seed_categories(conn, user_id)

        if sample_data:
            seed_sample_data(conn, user_id, category_ids)
