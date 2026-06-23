import db.queries.goals as goals_q
import db.queries.accounts as accounts_q
import db.queries.users as users_q

from utils.money import to_minor_units
from utils.enums import GoalStatus, normalize_enum_value
from utils.dates import parse_datetime


def get_goals(user_id: int):
    return goals_q.get_goals(user_id)


def get_goal(goal_id: int):
    return goals_q.get_goal(goal_id)


def _ensure_account_exists(account_id: int):
    account = accounts_q.get_account(account_id)
    if account is None:
        raise ValueError("Account does not exist")
    return account


def create_goal(user_id: int, name: str, target_amount, target_date=None):
    name = name.strip()
    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")
    if not name:
        raise ValueError("Goal name is required")

    target_amount_minor = to_minor_units(target_amount)
    if target_amount_minor <= 0:
        raise ValueError("Target amount must be greater than zero")

    goal_id = goals_q.create_goal(
        user_id=user_id,
        name=name,
        target_amount_minor=target_amount_minor,
        target_date=parse_datetime(target_date, "Target date"),
    )
    return {"goal_id": goal_id}


def update_goal(goal_id: int, name: str | None = None, target_amount=None, target_date=None, status: str | None = None):
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
        target_amount_minor = to_minor_units(target_amount)
        if target_amount_minor <= 0:
            raise ValueError("Target amount must be greater than zero")
        kwargs["target_amount_minor"] = target_amount_minor
    if target_date is not None:
        kwargs["target_date"] = parse_datetime(target_date, "Target date")
    if status is not None:
        kwargs["status"] = normalize_enum_value(status, GoalStatus, "Invalid goal status")

    if kwargs:
        goals_q.update_goal(goal_id, **kwargs)
    return {"status": "updated"}


def complete_goal(goal_id: int):
    if goals_q.get_goal(goal_id) is None:
        raise ValueError("Goal does not exist")

    goals_q.update_goal(
        goal_id,
        status=GoalStatus.COMPLETED.value,
    )

    return {"status": "completed"}


def get_goal_accounts(goal_id: int):
    if goals_q.get_goal(goal_id) is None:
        raise ValueError("Goal does not exist")
    return goals_q.get_goal_accounts(goal_id)


def add_account_to_goal(goal_id: int, account_id: int, allocated_amount=0):
    goal = goals_q.get_goal(goal_id)
    if goal is None:
        raise ValueError("Goal does not exist")

    account = _ensure_account_exists(account_id)
    if account["user_id"] != goal["user_id"]:
        raise ValueError("Goal account must belong to the same user")
    if account["status"] != "active":
        raise ValueError("Goal account must be active")

    allocated_amount_minor = to_minor_units(allocated_amount)
    if allocated_amount_minor < 0:
        raise ValueError("Allocated amount cannot be negative")

    goals_q.create_goal_account(
        goal_id=goal_id,
        account_id=account_id,
        allocated_amount_minor=allocated_amount_minor,
    )

    return {"status": "added"}


def update_goal_account_allocation(goal_id: int, account_id: int, allocated_amount):
    goal = goals_q.get_goal(goal_id)
    if goal is None:
        raise ValueError("Goal does not exist")

    account = _ensure_account_exists(account_id)
    if account["user_id"] != goal["user_id"]:
        raise ValueError("Goal account must belong to the same user")

    goal_accounts = goals_q.get_goal_accounts(goal_id)
    if not any(row["account_id"] == account_id for row in goal_accounts):
        raise ValueError("Account is not linked to this goal")

    allocated_amount_minor = to_minor_units(allocated_amount)
    if allocated_amount_minor < 0:
        raise ValueError("Allocated amount cannot be negative")

    goals_q.update_goal_account(
        goal_id=goal_id,
        account_id=account_id,
        allocated_amount_minor=allocated_amount_minor,
    )

    return {"status": "updated"}


def remove_account_from_goal(goal_id: int, account_id: int):
    if goals_q.get_goal(goal_id) is None:
        raise ValueError("Goal does not exist")

    goal_accounts = goals_q.get_goal_accounts(goal_id)
    if not any(row["account_id"] == account_id for row in goal_accounts):
        raise ValueError("Account is not linked to this goal")

    goals_q.delete_goal_account(goal_id, account_id)

    return {"status": "removed"}
