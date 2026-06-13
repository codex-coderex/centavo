import db.queries.budgets as budgets_q
import db.queries.categories as categories_q

from services.currency_service import get_user_decimal_places
from utils.money import to_minor_units
from utils.enums import BudgetPeriod, normalize_enum_value


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

    if not name:
        raise ValueError("Budget name is required")

    period = normalize_enum_value(
        period,
        BudgetPeriod,
        "Invalid budget period",
    )

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
    budget = budgets_q.get_budget(budget_id)

    if budget is None:
        raise ValueError("Budget does not exist")

    kwargs = {}

    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Budget name cannot be empty")
        kwargs["name"] = name

    if period is not None:
        kwargs["period"] = normalize_enum_value(
            period,
            BudgetPeriod,
            "Invalid budget period",
        )

    if start_date is not None:
        kwargs["start_date"] = start_date

    if end_date is not None:
        kwargs["end_date"] = end_date

    if kwargs:
        budgets_q.update_budget(budget_id, **kwargs)


def delete_budget(budget_id: int):
    if budgets_q.get_budget(budget_id) is None:
        raise ValueError("Budget does not exist")

    budgets_q.delete_budget(budget_id)


def get_budget_items(budget_id: int):
    return budgets_q.get_budget_items(budget_id)


def create_budget_item(
    budget_id: int,
    category_id: int,
    planned_amount,
    rollover_enabled: bool = False,
):
    budget = budgets_q.get_budget(budget_id)

    if budget is None:
        raise ValueError("Budget does not exist")

    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if not category["is_active"]:
        raise ValueError("Category is inactive")

    decimal_places = get_user_decimal_places(budget["user_id"])
    planned_amount_minor = to_minor_units(planned_amount, decimal_places)

    if planned_amount_minor < 0:
        raise ValueError("Planned amount cannot be negative")

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
    category_id: int | None = None,
    rollover_enabled: bool | None = None,
):
    budget_item = budgets_q.get_budget_item(budget_item_id)

    if budget_item is None:
        raise ValueError("Budget item does not exist")

    budget = budgets_q.get_budget(budget_item["budget_id"])

    if budget is None:
        raise ValueError("Budget does not exist")

    kwargs = {}

    if planned_amount is not None:
        decimal_places = get_user_decimal_places(budget["user_id"])
        planned_amount_minor = to_minor_units(planned_amount, decimal_places)

        if planned_amount_minor < 0:
            raise ValueError("Planned amount cannot be negative")

        kwargs["planned_amount_minor"] = planned_amount_minor

    if category_id is not None:
        category = categories_q.get_category(category_id)

        if category is None:
            raise ValueError("Category does not exist")

        if not category["is_active"]:
            raise ValueError("Category is inactive")

        kwargs["category_id"] = category_id

    if rollover_enabled is not None:
        kwargs["rollover_enabled"] = rollover_enabled

    if kwargs:
        budgets_q.update_budget_item(budget_item_id, **kwargs)


def delete_budget_item(budget_item_id: int):
    if budgets_q.get_budget_item(budget_item_id) is None:
        raise ValueError("Budget item does not exist")

    budgets_q.delete_budget_item(budget_item_id)