import services.account_service as service
from api.responses import ok, fail


def get_accounts(user_id, active_only=True):
    try:
        return ok(service.get_accounts(user_id, active_only=active_only))
    except ValueError as e:
        return fail(e)


def get_account(account_id):
    try:
        return ok(service.get_account(account_id))
    except ValueError as e:
        return fail(e)


def create_account(user_id, name, type, opening_balance=0):
    try:
        return ok(service.create_account(user_id, name, type, opening_balance=opening_balance))
    except ValueError as e:
        return fail(e)


def update_account(account_id, name=None, type=None, opening_balance=None, status=None):
    try:
        return ok(
            service.update_account(
                account_id,
                name=name,
                type=type,
                opening_balance=opening_balance,
                status=status,
            )
        )
    except ValueError as e:
        return fail(e)


def archive_account(account_id):
    try:
        return ok(service.archive_account(account_id))
    except ValueError as e:
        return fail(e)
