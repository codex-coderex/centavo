from datetime import datetime, timezone

from sqlalchemy import select

from db.connection import get_conn
from db.tables import (
    user,
    account,
    category_group,
    category,
    transaction,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_or_create_user(conn, name: str = "Me") -> int:
    existing = conn.execute(
        select(user.c.user_id).where(user.c.name == name)
    ).scalar_one_or_none()

    if existing is not None:
        return existing

    result = conn.execute(
        user.insert().values(
            name=name,
            created_at=utc_now(),
        )
    )

    return int(result.inserted_primary_key[0])


def get_or_create_category_group(
    conn,
    *,
    user_id: int,
    name: str,
    type_: str,
    is_system: bool = True,
) -> int:
    existing = conn.execute(
        select(category_group.c.group_id).where(
            category_group.c.user_id == user_id,
            category_group.c.type == type_,
            category_group.c.name == name,
        )
    ).scalar_one_or_none()

    if existing is not None:
        return existing

    result = conn.execute(
        category_group.insert().values(
            user_id=user_id,
            name=name,
            type=type_,
            is_system=is_system,
            is_active=True,
        )
    )

    return int(result.inserted_primary_key[0])


def get_or_create_category(
    conn,
    *,
    group_id: int,
    name: str,
    is_system: bool = True,
) -> int:
    existing = conn.execute(
        select(category.c.category_id).where(
            category.c.group_id == group_id,
            category.c.name == name,
        )
    ).scalar_one_or_none()

    if existing is not None:
        return existing

    result = conn.execute(
        category.insert().values(
            group_id=group_id,
            name=name,
            is_system=is_system,
            is_active=True,
        )
    )

    return int(result.inserted_primary_key[0])


def seed_categories(conn, user_id: int) -> dict[str, int]:
    groups: list[tuple[str, str, list[str]]] = [
        ("Income", "income", [
            "Salary",
            "Freelance",
            "Business",
            "Interest",
            "Gifts Received",
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
    existing = conn.execute(
        select(account.c.account_id).where(
            account.c.user_id == user_id,
            account.c.name == name,
        )
    ).scalar_one_or_none()

    if existing is not None:
        return existing

    result = conn.execute(
        account.insert().values(
            user_id=user_id,
            name=name,
            type=type_,
            opening_balance_minor=opening_balance_minor,
            created_at=utc_now(),
            status="active",
        )
    )

    return int(result.inserted_primary_key[0])


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

        exists = conn.execute(
            select(transaction.c.transaction_id).where(
                transaction.c.account_id == account_id,
                transaction.c.amount_minor == amount_minor,
                transaction.c.transaction_date == txn_dt,
                transaction.c.payee == payee,
            )
        ).scalar_one_or_none()

        if exists is not None:
            continue

        conn.execute(
            transaction.insert().values(
                account_id=account_id,
                category_id=category_ids[category_name],
                recurring_rule_id=None,
                payee=payee,
                amount_minor=amount_minor,
                transaction_date=txn_dt,
                notes=None,
                created_at=utc_now(),
                transfer_id=None,
            )
        )


def run_seed(sample_data: bool = False) -> None:
    with get_conn() as conn:
        user_id = get_or_create_user(conn, "Me")
        category_ids = seed_categories(conn, user_id)

        if sample_data:
            seed_sample_data(conn, user_id, category_ids)