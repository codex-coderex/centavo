import services.budget_service as service
from api.responses import ok, fail


def get_budgets(user_id):
    try:
        return ok(service.get_budgets(user_id))
    except ValueError as e:
        return fail(e)


def get_budget(budget_id):
    try:
        return ok(service.get_budget(budget_id))
    except ValueError as e:
        return fail(e)


def create_budget(user_id, name, period_type, start_date, end_date=None):
    try:
        return ok(service.create_budget(user_id, name, period_type, start_date, end_date=end_date))
    except ValueError as e:
        return fail(e)


def update_budget(budget_id, name=None, period_type=None, start_date=None, end_date=None):
    try:
        return ok(
            service.update_budget(
                budget_id,
                name=name,
                period_type=period_type,
                start_date=start_date,
                end_date=end_date,
            )
        )
    except ValueError as e:
        return fail(e)


def delete_budget(budget_id):
    try:
        return ok(service.delete_budget(budget_id))
    except ValueError as e:
        return fail(e)


def get_budget_items(budget_id):
    try:
        return ok(service.get_budget_items(budget_id))
    except ValueError as e:
        return fail(e)


def create_budget_item(budget_id, category_id, planned_amount, rollover_enabled=False):
    try:
        return ok(
            service.create_budget_item(
                budget_id,
                category_id,
                planned_amount,
                rollover_enabled=rollover_enabled,
            )
        )
    except ValueError as e:
        return fail(e)


def update_budget_item(budget_item_id, planned_amount=None, category_id=None, rollover_enabled=None):
    try:
        return ok(
            service.update_budget_item(
                budget_item_id,
                planned_amount=planned_amount,
                category_id=category_id,
                rollover_enabled=rollover_enabled,
            )
        )
    except ValueError as e:
        return fail(e)


def delete_budget_item(budget_item_id):
    try:
        return ok(service.delete_budget_item(budget_item_id))
    except ValueError as e:
        return fail(e)
