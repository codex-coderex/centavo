import db.queries.goals as goals_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q
import db.queries.transactions as transactions_q

from services.currency_service import get_account_decimal_places
from utils.money import to_minor_units
from utils.enums import GoalStatus, normalize_enum_value


def get_goals(user_id: int):
    return goals_q.get_goals(user_id)


def get_goal(goal_id: int):
    return goals_q.get_goal(goal_id)


def _ensure_account_exists(account_id: int):
    account = accounts_q.get_account(account_id)

    if account is None:
        raise ValueError("Account does not exist")

    return account


def _ensure_active_category_exists(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if not category["is_active"]:
        raise ValueError("Category is inactive")

    return category


def create_goal(
    user_id: int,
    name: str,
    target_amount,
    account_id: int,
    target_date: str | None = None,
):
    name = name.strip()

    if not name:
        raise ValueError("Goal name is required")

    account = _ensure_account_exists(account_id)

    if account["user_id"] != user_id:
        raise ValueError("Account does not belong to this user")

    decimal_places = get_account_decimal_places(account_id)
    target_amount_minor = to_minor_units(target_amount, decimal_places)

    if target_amount_minor <= 0:
        raise ValueError("Target amount must be greater than zero")

    goal_id = goals_q.create_goal(
        user_id=user_id,
        name=name,
        target_amount_minor=target_amount_minor,
        account_id=account_id,
        target_date=target_date,
    )

    return {"goal_id": goal_id}


def update_goal(
    goal_id: int,
    name: str | None = None,
    target_amount=None,
    target_date: str | None = None,
    status: str | None = None,
):
    goal = goals_q.get_goal(goal_id)

    if goal is None:
        raise ValueError("Goal does not exist")

    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Goal name cannot be empty")
        kwargs["name"] = name

    if target_amount is not None:
        decimal_places = get_account_decimal_places(goal["account_id"])
        target_amount_minor = to_minor_units(target_amount, decimal_places)

        if target_amount_minor <= 0:
            raise ValueError("Target amount must be greater than zero")

        kwargs["target_amount_minor"] = target_amount_minor

    if target_date is not None:
        kwargs["target_date"] = target_date

    if status is not None:
        kwargs["status"] = normalize_enum_value(
            status,
            GoalStatus,
            "Invalid goal status",
        )

    if kwargs:
        goals_q.update_goal(goal_id, **kwargs)


def complete_goal(goal_id: int):
    if goals_q.get_goal(goal_id) is None:
        raise ValueError("Goal does not exist")

    goals_q.complete_goal(goal_id)


def fund_goal(
    goal_id: int,
    amount,
    txn_date: str,
    category_id: int,
):
    goal = goals_q.get_goal(goal_id)

    if goal is None:
        raise ValueError("Goal does not exist")

    _ensure_active_category_exists(category_id)

    decimal_places = get_account_decimal_places(goal["account_id"])
    amount_minor = to_minor_units(amount, decimal_places)

    if amount_minor <= 0:
        raise ValueError("Funding amount must be greater than zero")

    transaction_id = transactions_q.create_transaction(
        account_id=goal["account_id"],
        amount_minor=-amount_minor,
        txn_date=txn_date,
        category_id=category_id,
        goal_id=goal_id,
    )

    return {"transaction_id": transaction_id}