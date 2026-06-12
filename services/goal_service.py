import db.queries.goals as goals_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q
import db.queries.transactions as transactions_q
from utils.money import to_minor_units
from utils.enums import GoalStatus


def get_goals(user_id: int):
    return goals_q.get_goals(user_id)


def get_goal(goal_id: int):
    return goals_q.get_goal(goal_id)


def create_goal(
    user_id: int,
    name: str,
    target_amount,
    account_id: int,
    target_date: str | None = None,
    decimal_places: int = 2,
):
    name = name.strip()

    if not name:
        raise ValueError("Goal name is required")

    if accounts_q.get_account(account_id) is None:
        raise ValueError("Account does not exist")

    goal_id = goals_q.create_goal(
        user_id=user_id,
        name=name,
        target_amount_minor=to_minor_units(target_amount, decimal_places),
        account_id=account_id,
        target_date=target_date,
    )

    return {"goal_id": goal_id}


def update_goal(
    goal_id: int, 
    name=None, 
    target_amount=None, 
    target_date=None,
    status=None, 
    decimal_places: int = 2
):
    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Goal name cannot be empty")
        kwargs["name"] = name

    if target_amount is not None:
        kwargs["target_amount_minor"] = to_minor_units(target_amount, decimal_places)

    if target_date is not None:
        kwargs["target_date"] = target_date

    if status is not None:
        if status not in GoalStatus:
            raise ValueError("Invalid goal status")
        kwargs["status"] = status

    if kwargs:
        goals_q.update_goal(goal_id, **kwargs)


def complete_goal(goal_id: int):
    goals_q.complete_goal(goal_id)


def fund_goal(
    goal_id: int,
    amount,
    txn_date: str,
    category_id: int,
    decimal_places: int = 2,
):
    goal = goals_q.get_goal(goal_id)

    if goal is None:
        raise ValueError("Goal does not exist")

    if categories_q.get_category(category_id) is None:
        raise ValueError("Category does not exist")

    transaction_id = transactions_q.create_transaction(
        account_id=goal["account_id"],
        amount_minor=-to_minor_units(amount, decimal_places),
        txn_date=txn_date,
        category_id=category_id,
        goal_id=goal_id,
    )

    return {"transaction_id": transaction_id}