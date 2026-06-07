import db.queries.accounts as q


def get_accounts(user_id):
    return q.get_accounts(user_id)


def get_account(account_id):
    return q.get_account(account_id)


def create_account(user_id, name, type, currency_code):
    account_id = q.create_account(user_id, name, type, currency_code)
    return {"account_id": account_id}


def update_account(account_id, name=None, type=None, currency_code=None, status=None):
    kwargs = {k: v for k, v in {
        "name": name,
        "type": type,
        "currency_code": currency_code,
        "status": status,
    }.items() if v is not None}
    q.update_account(account_id, **kwargs)


def archive_account(account_id):
    q.archive_account(account_id)
