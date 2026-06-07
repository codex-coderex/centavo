import db.queries.transactions as q


def get_transactions(account_id):
    return q.get_transactions(account_id)


def get_transaction(transaction_id):
    return q.get_transaction(transaction_id)


def create_transaction(account_id, amount, txn_date,
                       merchant=None, category_id=None,
                       note=None, goal_id=None, recurring_id=None):
    transaction_id = q.create_transaction(
        account_id, amount, txn_date,
        merchant=merchant,
        category_id=category_id,
        note=note,
        goal_id=goal_id,
        recurring_id=recurring_id,
    )
    return {"transaction_id": transaction_id}


def create_transfer(from_account_id, to_account_id, amount, txn_date, category_id):
    debit_id, credit_id = q.create_transfer(
        from_account_id, to_account_id, amount, txn_date, category_id
    )
    return {"debit_transaction_id": debit_id, "credit_transaction_id": credit_id}


def update_transaction(transaction_id, merchant=None, amount=None,
                       category_id=None, note=None, status=None,
                       needs_review=None, txn_date=None):
    # transaction_id, transfer_pair_id, and recurring_id are locked —
    # they're not accepted as parameters here at all
    kwargs = {k: v for k, v in {
        "merchant": merchant,
        "amount": amount,
        "category_id": category_id,
        "note": note,
        "status": status,
        "needs_review": needs_review,
        "txn_date": txn_date,
    }.items() if v is not None}
    q.update_transaction(transaction_id, **kwargs)


def flag_for_review(transaction_id):
    q.flag_for_review(transaction_id)
