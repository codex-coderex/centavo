import db.queries.budgets as budgets_q
import db.queries.categories as categories_q
from utils.money import to_minor_units
from utils.enums import BudgetPeriod


def get_budgets(user_id: int):
    return budgets_q.get_budgets(user_id)


def get_budget(budget_id: int):
    return budgets_q.get_budget(budget_id)


def create_budget(
    user_id: int,
    name: str,
    period: str,
    start_date: str,
    end_date: str | None = None,
):
    name = name.strip()
    period = period.strip().lower()

    if not name:
        raise ValueError("Budget name is required")

    if period not in BudgetPeriod:
        raise ValueError("Invalid budget period")

    budget_id = budgets_q.create_budget(
        user_id=user_id,
        name=name,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )

    return {"budget_id": budget_id}


def update_budget(
    budget_id: int,
    name: str | None = None,
    period: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Budget name cannot be empty")
        kwargs["name"] = name

    if period is not None:
        period = period.strip().lower()
        if period not in BudgetPeriod:
            raise ValueError("Invalid budget period")
        kwargs["period"] = period

    if start_date is not None:
        kwargs["start_date"] = start_date

    if end_date is not None:
        kwargs["end_date"] = end_date

    if kwargs:
        budgets_q.update_budget(budget_id, **kwargs)


def delete_budget(budget_id: int):
    budgets_q.delete_budget(budget_id)


def get_budget_items(budget_id: int):
    return budgets_q.get_budget_items(budget_id)


def create_budget_item(
    budget_id: int,
    category_id: int,
    planned_amount,
    decimal_places: int = 2,
    rollover_enabled: bool = False,
):
    category = categories_q.get_category(category_id)
    if category is None:
        raise ValueError("Category does not exist")

    planned_amount_minor = to_minor_units(planned_amount, decimal_places)

    budget_item_id = budgets_q.create_budget_item(
        budget_id=budget_id,
        category_id=category_id,
        planned_amount_minor=planned_amount_minor,
        rollover_enabled=rollover_enabled,
    )

    return {"budget_item_id": budget_item_id}


def update_budget_item(
    budget_item_id: int,
    planned_amount=None,
    decimal_places: int = 2,
    rollover_enabled: bool | None = None,
):
    kwargs = {}

    if planned_amount is not None:
        kwargs["planned_amount_minor"] = to_minor_units(
            planned_amount,
            decimal_places,
        )

    if rollover_enabled is not None:
        kwargs["rollover_enabled"] = rollover_enabled

    if kwargs:
        budgets_q.update_budget_item(budget_item_id, **kwargs)


def delete_budget_item(budget_item_id: int):
    budgets_q.delete_budget_item(budget_item_id)