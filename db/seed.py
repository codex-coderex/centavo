from db.connection import get_conn
from db.seed_helper import (
    get_or_create_account,
    get_or_create_budget,
    get_or_create_budget_item,
    get_or_create_category,
    get_or_create_category_group,
    get_or_create_goal,
    get_or_create_recurring_rule,
    get_or_create_user,
    insert_sample_transaction,
    link_goal_account,
)


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


def seed_sample_data(conn, user_id: int, category_ids: dict[str, int]) -> None:
    accounts = {
        "Everyday Checking": get_or_create_account(
            conn,
            user_id=user_id,
            name="Everyday Checking",
            type_="checking",
            opening_balance_minor=35_000_00,
        ),
        "Savings Vault": get_or_create_account(
            conn,
            user_id=user_id,
            name="Savings Vault",
            type_="savings",
            opening_balance_minor=80_000_00,
        ),
        "Cash Wallet": get_or_create_account(
            conn,
            user_id=user_id,
            name="Cash Wallet",
            type_="cash",
            opening_balance_minor=5_000_00,
        ),
        "Rewards Credit Card": get_or_create_account(
            conn,
            user_id=user_id,
            name="Rewards Credit Card",
            type_="credit_card",
            opening_balance_minor=-12_000_00,
        ),
    }

    budgets = {
        "Sample Essentials Budget": get_or_create_budget(
            conn,
            user_id=user_id,
            name="Sample Essentials Budget",
            period_type="custom",
            start_date="2026-05-01",
            end_date="2026-06-30",
        ),
        "Sample Lifestyle Budget": get_or_create_budget(
            conn,
            user_id=user_id,
            name="Sample Lifestyle Budget",
            period_type="custom",
            start_date="2026-05-01",
            end_date="2026-06-30",
        ),
        "Sample Savings Budget": get_or_create_budget(
            conn,
            user_id=user_id,
            name="Sample Savings Budget",
            period_type="custom",
            start_date="2026-05-01",
            end_date="2026-06-30",
        ),
    }

    budget_items: dict[str, int] = {}

    budget_plan = {
        "Sample Essentials Budget": {
            "Rent": 24_000_00,
            "Groceries": 16_000_00,
            "Electricity": 4_000_00,
            "Internet": 2_500_00,
            "Fuel": 5_000_00,
        },
        "Sample Lifestyle Budget": {
            "Dining Out": 6_000_00,
            "Coffee": 2_000_00,
            "Subscriptions": 1_500_00,
            "Pharmacy": 2_000_00,
            "Grooming": 2_500_00,
        },
        "Sample Savings Budget": {
            "Emergency Fund": 10_000_00,
            "Investment": 8_000_00,
            "Gifts Given": 3_000_00,
        },
    }

    for budget_name, items in budget_plan.items():
        for category_name, planned_amount_minor in items.items():
            budget_items[category_name] = get_or_create_budget_item(
                conn,
                budget_id=budgets[budget_name],
                category_id=category_ids[category_name],
                planned_amount_minor=planned_amount_minor,
                rollover_enabled=budget_name != "Sample Lifestyle Budget",
            )

    recurring_rules = {
        "Monthly Salary": get_or_create_recurring_rule(
            conn,
            account_id=accounts["Everyday Checking"],
            category_id=category_ids["Salary"],
            name="Monthly Salary",
            expected_amount_minor=65_000_00,
            interval=1,
            frequency_unit="month",
            start_date="2026-05-01",
            next_due_date="2026-07-01",
        ),
        "Apartment Rent": get_or_create_recurring_rule(
            conn,
            account_id=accounts["Everyday Checking"],
            category_id=category_ids["Rent"],
            name="Apartment Rent",
            expected_amount_minor=-24_000_00,
            interval=1,
            frequency_unit="month",
            start_date="2026-05-02",
            next_due_date="2026-07-02",
        ),
        "Home Internet": get_or_create_recurring_rule(
            conn,
            account_id=accounts["Rewards Credit Card"],
            category_id=category_ids["Internet"],
            name="Home Internet",
            expected_amount_minor=-2_499_00,
            interval=1,
            frequency_unit="month",
            start_date="2026-05-03",
            next_due_date="2026-07-03",
        ),
        "Gym Membership": get_or_create_recurring_rule(
            conn,
            account_id=accounts["Rewards Credit Card"],
            category_id=category_ids["Fitness"],
            name="Gym Membership",
            expected_amount_minor=-1_200_00,
            interval=1,
            frequency_unit="month",
            start_date="2026-05-04",
            next_due_date="2026-07-04",
        ),
    }

    goals = {
        "Emergency Fund": get_or_create_goal(
            conn,
            user_id=user_id,
            name="Emergency Fund",
            target_amount_minor=150_000_00,
            target_date="2026-12-31",
        ),
        "New Laptop": get_or_create_goal(
            conn,
            user_id=user_id,
            name="New Laptop",
            target_amount_minor=75_000_00,
            target_date="2026-10-31",
        ),
        "Holiday Trip": get_or_create_goal(
            conn,
            user_id=user_id,
            name="Holiday Trip",
            target_amount_minor=120_000_00,
            target_date="2026-11-30",
        ),
    }

    link_goal_account(
        conn,
        goal_id=goals["Emergency Fund"],
        account_id=accounts["Savings Vault"],
        allocated_amount_minor=45_000_00,
    )
    link_goal_account(
        conn,
        goal_id=goals["New Laptop"],
        account_id=accounts["Everyday Checking"],
        allocated_amount_minor=15_000_00,
    )
    link_goal_account(
        conn,
        goal_id=goals["Holiday Trip"],
        account_id=accounts["Cash Wallet"],
        allocated_amount_minor=8_000_00,
    )

    transactions = [
        ("2026-05-01", "Everyday Checking", 65_000_00, "Centavo Demo Employer", "Salary", "Monthly Salary"),
        ("2026-05-02", "Everyday Checking", -24_000_00, "Sample Property Management", "Rent", "Apartment Rent"),
        ("2026-05-03", "Rewards Credit Card", -2_499_00, "Fiber Internet Co.", "Internet", "Home Internet"),
        ("2026-05-04", "Rewards Credit Card", -1_200_00, "Fit Club", "Fitness", "Gym Membership"),
        ("2026-05-05", "Rewards Credit Card", -3_850_00, "Fresh Mart", "Groceries", None),
        ("2026-05-07", "Cash Wallet", -450_00, "Corner Coffee", "Coffee", None),
        ("2026-05-09", "Rewards Credit Card", -1_250_00, "Lunch Spot", "Dining Out", None),
        ("2026-05-11", "Everyday Checking", -3_200_00, "Fuel Station", "Fuel", None),
        ("2026-05-13", "Rewards Credit Card", -699_00, "StreamBox", "Subscriptions", None),
        ("2026-05-15", "Everyday Checking", 8_000_00, "Freelance Client", "Freelance", None),
        ("2026-05-17", "Rewards Credit Card", -920_00, "Pharmacy Plus", "Pharmacy", None),
        ("2026-05-20", "Everyday Checking", -5_000_00, "Savings Transfer", "Emergency Fund", None),
        ("2026-05-22", "Rewards Credit Card", -1_800_00, "Barber Shop", "Grooming", None),
        ("2026-05-25", "Everyday Checking", -4_000_00, "Brokerage Transfer", "Investment", None),
        ("2026-05-27", "Cash Wallet", -1_500_00, "Birthday Gift", "Gifts Given", None),

        ("2026-06-01", "Everyday Checking", 65_000_00, "Centavo Demo Employer", "Salary", "Monthly Salary"),
        ("2026-06-02", "Everyday Checking", -24_000_00, "Sample Property Management", "Rent", "Apartment Rent"),
        ("2026-06-03", "Rewards Credit Card", -2_499_00, "Fiber Internet Co.", "Internet", "Home Internet"),
        ("2026-06-04", "Rewards Credit Card", -1_200_00, "Fit Club", "Fitness", "Gym Membership"),
        ("2026-06-05", "Rewards Credit Card", -4_100_00, "Fresh Mart", "Groceries", None),
        ("2026-06-07", "Cash Wallet", -520_00, "Corner Coffee", "Coffee", None),
        ("2026-06-09", "Rewards Credit Card", -1_450_00, "Lunch Spot", "Dining Out", None),
        ("2026-06-11", "Everyday Checking", -3_500_00, "Fuel Station", "Fuel", None),
        ("2026-06-13", "Rewards Credit Card", -699_00, "StreamBox", "Subscriptions", None),
        ("2026-06-15", "Everyday Checking", 10_000_00, "Freelance Client", "Freelance", None),
        ("2026-06-17", "Rewards Credit Card", -780_00, "Pharmacy Plus", "Pharmacy", None),
        ("2026-06-20", "Everyday Checking", -5_000_00, "Savings Transfer", "Emergency Fund", None),
        ("2026-06-22", "Rewards Credit Card", -1_650_00, "Barber Shop", "Grooming", None),
        ("2026-06-25", "Everyday Checking", -4_000_00, "Brokerage Transfer", "Investment", None),
        ("2026-06-27", "Cash Wallet", -1_200_00, "Family Gift", "Gifts Given", None),
    ]

    for transaction_date, account_name, amount_minor, payee, category_name, recurring_rule_name in transactions:
        insert_sample_transaction(
            conn,
            account_id=accounts[account_name],
            category_id=category_ids[category_name],
            budget_item_id=budget_items.get(category_name),
            recurring_rule_id=recurring_rules.get(recurring_rule_name) if recurring_rule_name else None,
            payee=payee,
            amount_minor=amount_minor,
            transaction_date=transaction_date,
            notes="Demo sample data",
        )


def run_seed(sample_data: bool = False) -> None:
    with get_conn() as conn:
        user_id = get_or_create_user(conn, "Me")
        category_ids = seed_categories(conn, user_id)

        if sample_data:
            seed_sample_data(conn, user_id, category_ids)