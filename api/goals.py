import services.goal_service as service


def get_goals(user_id):
    return service.get_goals(user_id)


def get_goal(goal_id):
    return service.get_goal(goal_id)


def create_goal(user_id, name, target_amount, account_id, target_date=None):
    try:
        return service.create_goal(user_id, name, target_amount,
                                   account_id=account_id, target_date=target_date)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_goal(goal_id, name=None, target_amount=None, target_date=None, status=None):
    try:
        service.update_goal(goal_id, name=name, target_amount=target_amount,
                            target_date=target_date, status=status)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def complete_goal(goal_id):
    try:
        service.complete_goal(goal_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def fund_goal(goal_id, amount, txn_date, category_id):
    try:
        return service.fund_goal(goal_id, amount=amount,
                                 txn_date=txn_date, category_id=category_id)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
