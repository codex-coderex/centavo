from sqlalchemy import select

from db.connection import get_conn
from db.tables import currency, user
from db.queries.currency import seed_currency
from db.queries.categories import create_category_group, create_category
from db.queries.users import create_user
from db.queries.accounts import create_account
from db.queries.transactions import create_transaction


def has_seed_data() -> bool:
    """
    Returns True if the required app seed data already exists.

    We check currency because currency is seeded before users/categories.
    """
    with get_conn() as conn:
        result = conn.execute(select(currency.c.code).limit(1))
        return result.first() is not None


def has_user() -> bool:
    """
    Returns True if at least one user exists.
    """
    with get_conn() as conn:
        result = conn.execute(select(user.c.user_id).limit(1))
        return result.first() is not None


def seed_currencies():
    currencies = [
        ("PHP", "Philippine Peso", "₱", 2),
        ("USD", "US Dollar", "$", 2),
        ("EUR", "Euro", "€", 2),
        ("GBP", "British Pound", "£", 2),
        ("JPY", "Japanese Yen", "¥", 0),
    ]

    for code, name, symbol, decimal_places in currencies:
        seed_currency(code, name, symbol, decimal_places)


def seed_categories(user_id: int) -> dict[str, int]:
    groups = [
        ("Income", "income", [
            ("Salary", "#4CAF50"),
            ("Freelance", "#8BC34A"),
            ("Business", "#CDDC39"),
            ("Interest", "#66BB6A"),
            ("Gifts Received", "#A5D6A7"),
        ]),
        ("Housing", "expense", [
            ("Rent", "#EF5350"),
            ("Electricity", "#E53935"),
            ("Water", "#1E88E5"),
            ("Internet", "#AB47BC"),
            ("Repairs", "#EC407A"),
        ]),
        ("Food", "expense", [
            ("Groceries", "#FF9800"),
            ("Dining Out", "#FF5722"),
            ("Coffee", "#795548"),
            ("Delivery", "#FFA726"),
        ]),
        ("Transport", "expense", [
            ("Fuel", "#607D8B"),
            ("Fare", "#78909C"),
            ("Parking", "#90A4AE"),
            ("Vehicle Maintenance", "#546E7A"),
        ]),
        ("Transfer", "expense", [
            ("Transfer", "#607D8B"),
        ]),
        ("Health", "expense", [
            ("Medical", "#00ACC1"),
            ("Pharmacy", "#00897B"),
            ("Dental", "#26A69A"),
            ("Fitness", "#80CBC4"),
        ]),
        ("Personal", "expense", [
            ("Clothing", "#F06292"),
            ("Grooming", "#F48FB1"),
            ("Subscriptions", "#CE93D8"),
            ("Education", "#9575CD"),
        ]),
        ("Family", "expense", [
            ("Allowance", "#FFB74D"),
            ("Gifts Given", "#FFCC02"),
            ("Dependents", "#FFE082"),
        ]),
        ("Savings & Investment", "expense", [
            ("Emergency Fund", "#3F51B5"),
            ("Investment", "#1565C0"),
            ("SSS/Pag-IBIG/PhilHealth", "#0288D1"),
        ]),
        ("Miscellaneous", "expense", [
            ("Fees & Charges", "#BDBDBD"),
            ("Donations", "#9E9E9E"),
            ("Others", "#757575"),
        ]),
        ("Uncategorized", "expense", [
            ("Uncategorized", "#9E9E9E"),
        ]),
    ]

    category_ids = {}

    for group_name, group_type, categories in groups:
        group_id = create_category_group(user_id, group_name, group_type)

        for category_name, color in categories:
            category_id = create_category(
                group_id=group_id,
                name=category_name,
                color=color,
                is_system=True,
            )
            category_ids[category_name] = category_id

    return category_ids


def seed_sample_data(user_id: int, category_ids: dict[str, int]):
    account_id = create_account(
        user_id=user_id,
        name="Main Account",
        type="checking",
    )

    transactions = [
        (account_id, 25000, "2025-01-01", "Company Inc", "Salary"),
        (account_id, -1500, "2025-01-03", "SM Supermarket", "Groceries"),
        (account_id, -500, "2025-01-05", "Jollibee", "Dining Out"),
        (account_id, -3000, "2025-01-07", "Meralco", "Electricity"),
        (account_id, -800, "2025-01-10", "Grab", "Fare"),
        (account_id, 5000, "2025-01-15", "Client A", "Freelance"),
        (account_id, -2000, "2025-01-18", "Mercury Drug", "Pharmacy"),
        (account_id, -1200, "2025-01-20", "Puregold", "Groceries"),
    ]

    for account_id, amount_minor, txn_date, merchant, category_name in transactions:
        create_transaction(
            account_id=account_id,
            amount_minor=amount_minor,
            txn_date=txn_date,
            merchant=merchant,
            category_id=category_ids[category_name],
        )


def run_seed(sample_data: bool = False):
    """
    Seeds required app data.

    This should be safe to call on startup.
    """
    if has_seed_data():
        return

    seed_currencies()

    if has_user():
        return

    user_id = create_user("Me", "PHP")
    category_ids = seed_categories(user_id)

    if sample_data:
        seed_sample_data(user_id, category_ids)