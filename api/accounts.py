import services.account_service as service


def get_accounts(user_id):
    return service.get_accounts(user_id)


def get_account(account_id):
    return service.get_account(account_id)


def create_account(user_id, name, type):
    return service.create_account(user_id, name, type)


def update_account(account_id, name=None, type=None, status=None):
    try:
        service.update_account(account_id, name=name, type=type, status=status)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def archive_account(account_id):
    try:
        service.archive_account(account_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}
