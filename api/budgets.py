import db.queries.budgets as q


def get_budgets(user_id):
    return q.get_budgets(user_id)


def get_budget(budget_id):
    return q.get_budget(budget_id)


def create_budget(user_id, name, period, start_date, end_date=None):
    budget_id = q.create_budget(user_id, name, period, start_date, end_date)
    return {"budget_id": budget_id}


def update_budget(budget_id, name=None, period=None, start_date=None, end_date=None):
    kwargs = {k: v for k, v in {
        "name": name,
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
    }.items() if v is not None}
    q.update_budget(budget_id, **kwargs)


def delete_budget(budget_id):
    q.delete_budget(budget_id)


def get_budget_items(budget_id):
    return q.get_budget_items(budget_id)


def create_budget_item(budget_id, category_id, planned_amount, rollover_enabled=False):
    budget_item_id = q.create_budget_item(
        budget_id, category_id, planned_amount, rollover_enabled
    )
    return {"budget_item_id": budget_item_id}


def update_budget_item(budget_item_id, planned_amount=None, rollover_enabled=None):
    kwargs = {k: v for k, v in {
        "planned_amount": planned_amount,
        "rollover_enabled": rollover_enabled,
    }.items() if v is not None}
    q.update_budget_item(budget_item_id, **kwargs)


def delete_budget_item(budget_item_id):
    q.delete_budget_item(budget_item_id)
