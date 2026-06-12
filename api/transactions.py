import services.transaction_service as service


def get_transactions_by_user(user_id):
    return service.get_transactions_by_user(user_id)


def get_transactions_by_account(account_id):
    return service.get_transactions_by_account(account_id)


def get_transaction(transaction_id):
    return service.get_transaction(transaction_id)


def create_transaction(account_id, amount, txn_date, category_id,
                       merchant=None, note=None, goal_id=None, recurring_id=None):
    try:
        return service.create_transaction(
            account_id=account_id,
            amount=amount,
            txn_date=txn_date,
            category_id=category_id,
            merchant=merchant,
            note=note,
            goal_id=goal_id,
            recurring_id=recurring_id,
        )
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def create_transfer(from_account_id, to_account_id, amount, txn_date, category_id):
    try:
        return service.create_transfer(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            txn_date=txn_date,
            category_id=category_id,
        )
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_transaction(transaction_id, merchant=None, amount=None, category_id=None,
                       note=None, status=None, needs_review=None, txn_date=None):
    try:
        service.update_transaction(
            transaction_id=transaction_id,
            merchant=merchant,
            amount=amount,
            category_id=category_id,
            note=note,
            status=status,
            needs_review=needs_review,
            txn_date=txn_date,
        )
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def flag_for_review(transaction_id):
    try:
        service.flag_for_review(transaction_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}
