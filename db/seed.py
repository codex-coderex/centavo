from db.queries.currency import create_currency
from db.queries.categories import create_category_group, create_category
from db.queries.users import create_user, get_all_users
from db.queries.accounts import create_account
from db.queries.transactions import create_transaction
from db.connection import get_conn
from db.tables import currency, category_group
from sqlalchemy import select
from datetime import datetime

def is_fresh_db():
    with get_conn() as conn:
        result = conn.execute(select(currency))
        return result.first() is None

def seed_required(user_id: int):

    # currencies
    currencies = [
        ("PHP", "Philippine Peso", "₱", 2),
        ("USD", "US Dollar", "$", 2),
        ("EUR", "Euro", "€", 2),
        ("GBP", "British Pound", "£", 2),
        ("JPY", "Japanese Yen", "¥", 0),
    ]
    for code, name, symbol, decimal_places in currencies:
        create_currency(code, name, symbol, decimal_places)

    # system category groups + categories
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

    for group_name, group_type, categories in groups:
        group_id = create_category_group(user_id, group_name, group_type)
        for cat_name, color in categories:
            create_category(group_id, cat_name, color)

def seed_sample_data(user_id: int, account_id: int):

    transactions = [
        (account_id, 25000,   "2025-01-01", "Company Inc",    "Salary"),
        (account_id, -1500,   "2025-01-03", "SM Supermarket", "Groceries"),
        (account_id, -500,    "2025-01-05", "Jollibee",       "Dining Out"),
        (account_id, -3000,   "2025-01-07", "Meralco",        "Utilities"),
        (account_id, -800,    "2025-01-10", "Grab",           "Fare"),
        (account_id, 5000,    "2025-01-15", "Client A",       "Freelance"),
        (account_id, -2000,   "2025-01-18", "Mercury Drug",   "Pharmacy"),
        (account_id, -1200,   "2025-01-20", "Puregold",       "Groceries"),
    ]

    for account_id, amount, txn_date, merchant, _ in transactions:
        create_transaction(
            account_id=account_id,
            amount=amount,
            txn_date=txn_date,
            merchant=merchant
        )

def run_seed(sample_data: bool = False):
    """
    Entry point called from main.py on first launch.
    sample_data=True only if user opted in.
    """
    if not is_fresh_db():
        return  # already seeded, do nothing

    # create default user
    user_id = create_user("Me")

    # always seed required data
    seed_required(user_id)

    # optionally seed sample data
    if sample_data:
        account_id = create_account(
            user_id=user_id,
            name="Main Account",
            type="checking",
            currency_code="PHP"
        )
        seed_sample_data(user_id, account_id)