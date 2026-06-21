import services.account_service as service
from api.responses import safe


def get_accounts(user_id, active_only=True):
    return safe(lambda: service.get_accounts(user_id, active_only=active_only))


def get_account(account_id):
    return safe(lambda: service.get_account(account_id))


def create_account(user_id, name, type, opening_balance=0):
    return safe(lambda: service.create_account(user_id, name, type, opening_balance=opening_balance))


def update_account(account_id, name=None, type=None, opening_balance=None, status=None):
    return safe(lambda: service.update_account(
        account_id,
        name=name,
        type=type,
        opening_balance=opening_balance,
        status=status,
    ))


def archive_account(account_id):
    return safe(lambda: service.archive_account(account_id))
