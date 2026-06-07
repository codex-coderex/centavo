import db.queries.goals as q


def get_goals(user_id):
    return q.get_goals(user_id)


def get_goal(goal_id):
    return q.get_goal(goal_id)


def create_goal(user_id, name, target_amount, target_date=None, account_id=None):
    goal_id = q.create_goal(user_id, name, target_amount, target_date, account_id)
    return {"goal_id": goal_id}


def update_goal(goal_id, name=None, target_amount=None, target_date=None,
                account_id=None, status=None):
    kwargs = {k: v for k, v in {
        "name": name,
        "target_amount": target_amount,
        "target_date": target_date,
        "account_id": account_id,
        "status": status,
    }.items() if v is not None}
    q.update_goal(goal_id, **kwargs)


def complete_goal(goal_id):
    q.complete_goal(goal_id)


def fund_goal(goal_id, account_id, amount, txn_date, category_id):
    q.fund_goal(goal_id, account_id, amount, txn_date, category_id)
