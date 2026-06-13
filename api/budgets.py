import services.budget_service as service


def get_budgets(user_id):
    return service.get_budgets(user_id)


def get_budget(budget_id):
    return service.get_budget(budget_id)


def create_budget(user_id, name, period, start_date, end_date=None):
    try:
        return service.create_budget(user_id, name, period, start_date, end_date=end_date)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_budget(budget_id, name=None, period=None, start_date=None, end_date=None):
    try:
        service.update_budget(budget_id, name=name, period=period,
                              start_date=start_date, end_date=end_date)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def delete_budget(budget_id):
    try:
        service.delete_budget(budget_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def get_budget_items(budget_id):
    return service.get_budget_items(budget_id)


def create_budget_item(budget_id, category_id, planned_amount, rollover_enabled=False):
    try:
        return service.create_budget_item(budget_id, category_id, planned_amount,
                                          rollover_enabled=rollover_enabled)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_budget_item(budget_item_id, planned_amount=None, category_id=None,
                       rollover_enabled=None):
    try:
        service.update_budget_item(budget_item_id, planned_amount=planned_amount,
                                   category_id=category_id, rollover_enabled=rollover_enabled)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def delete_budget_item(budget_item_id):
    try:
        service.delete_budget_item(budget_item_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}
