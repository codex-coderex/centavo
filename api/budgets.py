import services.budget_service as service
from api.responses import safe


def get_budgets(user_id):
    return safe(lambda: service.get_budgets(user_id))


def get_budget(budget_id):
    return safe(lambda: service.get_budget(budget_id))


def create_budget(user_id, name, period_type, start_date, end_date=None):
    return safe(lambda: service.create_budget(user_id, name, period_type, start_date, end_date=end_date))


def update_budget(budget_id, name=None, period_type=None, start_date=None, end_date=None):
    return safe(lambda: service.update_budget(
        budget_id,
        name=name,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
    ))


def delete_budget(budget_id):
    return safe(lambda: service.delete_budget(budget_id))


def get_budget_items(budget_id):
    return safe(lambda: service.get_budget_items(budget_id))


def create_budget_item(budget_id, category_id, planned_amount, rollover_enabled=False):
    return safe(lambda: service.create_budget_item(
        budget_id,
        category_id,
        planned_amount,
        rollover_enabled=rollover_enabled,
    ))


def update_budget_item(budget_item_id, planned_amount=None, category_id=None, rollover_enabled=None):
    return safe(lambda: service.update_budget_item(
        budget_item_id,
        planned_amount=planned_amount,
        category_id=category_id,
        rollover_enabled=rollover_enabled,
    ))


def delete_budget_item(budget_item_id):
    return safe(lambda: service.delete_budget_item(budget_item_id))
