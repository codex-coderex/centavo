import db.queries.budgets as budgets_q
import db.queries.categories as categories_q
import db.queries.users as users_q

from utils.money import to_minor_units
from utils.enums import BudgetPeriod, normalize_enum_value
from utils.dates import (
    calculate_period_end,
    require_datetime,
)

BUDGET_DUPLICATE_ERROR = "A budget with this name already starts on this date."
BUDGET_ITEM_DUPLICATE_ERROR = "This budget already has an item for that category."


def get_budgets(user_id: int):
    return budgets_q.get_budgets(user_id)


def get_budget(budget_id: int):
    return budgets_q.get_budget(budget_id)


def create_budget(
    user_id: int,
    name: str,
    period_type: str,
    start_date,
    end_date=None,
):
    name = name.strip()

    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    if not name:
        raise ValueError("Budget name is required")

    period_type = normalize_enum_value(
        period_type,
        BudgetPeriod,
        "Invalid budget period",
    )

    start_date = require_datetime(start_date, "Start date")

    if period_type == BudgetPeriod.CUSTOM.value:
        end_date = require_datetime(end_date, "End date")
    else:
        end_date = calculate_period_end(start_date, period_type)

    if end_date < start_date:
        raise ValueError("End date cannot be before start date")

    if budgets_q.get_budget_by_user_name_start_date(user_id, name, start_date) is not None:
        raise ValueError(BUDGET_DUPLICATE_ERROR)

    budget_id = budgets_q.create_budget(
        user_id=user_id,
        name=name,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
    )

    return {"budget_id": budget_id}


def update_budget(
    budget_id: int,
    name: str | None = None,
    period_type: str | None = None,
    start_date=None,
    end_date=None,
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

    if period_type is not None:
        kwargs["period_type"] = normalize_enum_value(
            period_type,
            BudgetPeriod,
            "Invalid budget period",
        )

    if start_date is not None:
        kwargs["start_date"] = require_datetime(
            start_date,
            "Start date",
        )

    next_period = kwargs.get(
        "period_type",
        budget["period_type"],
    )

    next_start = kwargs.get(
        "start_date",
        budget["start_date"],
    )

    if next_period == BudgetPeriod.CUSTOM.value:
        if end_date is not None:
            next_end = require_datetime(end_date, "End date")
            kwargs["end_date"] = next_end
        else:
            next_end = budget["end_date"]

        if next_end is None:
            raise ValueError("Custom budgets require an end date")
    else:
        next_end = calculate_period_end(
            next_start,
            next_period,
        )
        kwargs["end_date"] = next_end

    if next_end < next_start:
        raise ValueError("End date cannot be before start date")

    next_name = kwargs.get("name", budget["name"])

    if budgets_q.get_budget_by_user_name_start_date(
        budget["user_id"],
        next_name,
        next_start,
        exclude_budget_id=budget_id,
    ) is not None:
        raise ValueError(BUDGET_DUPLICATE_ERROR)

    if kwargs:
        budgets_q.update_budget(budget_id, **kwargs)

    return {"status": "updated"}


def delete_budget(budget_id: int):
    if budgets_q.get_budget(budget_id) is None:
        raise ValueError("Budget does not exist")

    budgets_q.delete_budget(budget_id)

    return {"status": "deleted"}


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

    group = categories_q.get_category_group(category["group_id"])

    if group is None or group["user_id"] != budget["user_id"]:
        raise ValueError("Category does not belong to the budget owner")

    if group["type"] != "expense":
        raise ValueError("Budgets can only use expense categories")

    if not category["is_active"]:
        raise ValueError("Category is inactive")

    planned_amount_minor = to_minor_units(planned_amount)

    if planned_amount_minor < 0:
        raise ValueError("Planned amount cannot be negative")

    if budgets_q.get_budget_item_by_budget_category(budget_id, category_id) is not None:
        raise ValueError(BUDGET_ITEM_DUPLICATE_ERROR)

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

    kwargs = {}

    if planned_amount is not None:
        planned_amount_minor = to_minor_units(planned_amount)

        if planned_amount_minor < 0:
            raise ValueError("Planned amount cannot be negative")

        kwargs["planned_amount_minor"] = planned_amount_minor

    if category_id is not None:
        category = categories_q.get_category(category_id)

        if category is None:
            raise ValueError("Category does not exist")

        budget = budgets_q.get_budget(budget_item["budget_id"])
        group = categories_q.get_category_group(category["group_id"])

        if (
            budget is None
            or group is None
            or group["user_id"] != budget["user_id"]
        ):
            raise ValueError("Category does not belong to the budget owner")

        if group["type"] != "expense":
            raise ValueError("Budgets can only use expense categories")

        if not category["is_active"]:
            raise ValueError("Category is inactive")

        kwargs["category_id"] = category_id

    next_category_id = kwargs.get("category_id", budget_item["category_id"])

    if budgets_q.get_budget_item_by_budget_category(
        budget_item["budget_id"],
        next_category_id,
        exclude_budget_item_id=budget_item_id,
    ) is not None:
        raise ValueError(BUDGET_ITEM_DUPLICATE_ERROR)

    if rollover_enabled is not None:
        kwargs["rollover_enabled"] = rollover_enabled

    if kwargs:
        budgets_q.update_budget_item(
            budget_item_id,
            **kwargs,
        )

    return {"status": "updated"}


def delete_budget_item(budget_item_id: int):
    if budgets_q.get_budget_item(budget_item_id) is None:
        raise ValueError("Budget item does not exist")

    budgets_q.delete_budget_item(budget_item_id)

    return {"status": "deleted"}
