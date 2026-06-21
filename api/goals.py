import services.goal_service as service
from api.responses import ok, fail


def get_goals(user_id):
    try:
        return ok(service.get_goals(user_id))
    except ValueError as e:
        return fail(e)


def get_goal(goal_id):
    try:
        return ok(service.get_goal(goal_id))
    except ValueError as e:
        return fail(e)


def create_goal(user_id, name, target_amount, target_date=None):
    try:
        return ok(service.create_goal(user_id, name, target_amount, target_date=target_date))
    except ValueError as e:
        return fail(e)


def update_goal(goal_id, name=None, target_amount=None, target_date=None, status=None):
    try:
        return ok(
            service.update_goal(
                goal_id,
                name=name,
                target_amount=target_amount,
                target_date=target_date,
                status=status,
            )
        )
    except ValueError as e:
        return fail(e)


def complete_goal(goal_id):
    try:
        return ok(service.complete_goal(goal_id))
    except ValueError as e:
        return fail(e)


def get_goal_accounts(goal_id):
    try:
        return ok(service.get_goal_accounts(goal_id))
    except ValueError as e:
        return fail(e)


def add_account_to_goal(goal_id, account_id, allocated_amount=0):
    try:
        return ok(service.add_account_to_goal(goal_id, account_id, allocated_amount=allocated_amount))
    except ValueError as e:
        return fail(e)


def update_goal_account_allocation(goal_id, account_id, allocated_amount):
    try:
        return ok(service.update_goal_account_allocation(goal_id, account_id, allocated_amount))
    except ValueError as e:
        return fail(e)


def remove_account_from_goal(goal_id, account_id):
    try:
        return ok(service.remove_account_from_goal(goal_id, account_id))
    except ValueError as e:
        return fail(e)
