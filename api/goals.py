import services.goal_service as service
from api.responses import safe


def get_goals(user_id):
    return safe(lambda: service.get_goals(user_id))


def get_goal(goal_id):
    return safe(lambda: service.get_goal(goal_id))


def create_goal(user_id, name, target_amount, target_date=None):
    return safe(lambda: service.create_goal(user_id, name, target_amount, target_date=target_date))


def update_goal(goal_id, name=None, target_amount=None, target_date=None, status=None):
    return safe(lambda: service.update_goal(
        goal_id,
        name=name,
        target_amount=target_amount,
        target_date=target_date,
        status=status,
    ))


def complete_goal(goal_id):
    return safe(lambda: service.complete_goal(goal_id))


def get_goal_accounts(goal_id):
    return safe(lambda: service.get_goal_accounts(goal_id))


def add_account_to_goal(goal_id, account_id, allocated_amount=0):
    return safe(lambda: service.add_account_to_goal(goal_id, account_id, allocated_amount=allocated_amount))


def update_goal_account_allocation(goal_id, account_id, allocated_amount):
    return safe(lambda: service.update_goal_account_allocation(goal_id, account_id, allocated_amount))


def remove_account_from_goal(goal_id, account_id):
    return safe(lambda: service.remove_account_from_goal(goal_id, account_id))
