import services.transaction_service as service
from api.responses import safe


def get_transactions_by_user(user_id):
    return safe(lambda: service.get_transactions_by_user(user_id))


def get_transactions_by_account(account_id):
    return safe(lambda: service.get_transactions_by_account(account_id))


def get_transaction(transaction_id):
    return safe(lambda: service.get_transaction(transaction_id))


def create_transaction(account_id, amount, transaction_date, category_id=None,
                       payee=None, notes=None, recurring_rule_id=None):
    return safe(lambda: service.create_transaction(
        account_id=account_id,
        amount=amount,
        transaction_date=transaction_date,
        category_id=category_id,
        payee=payee,
        notes=notes,
        recurring_rule_id=recurring_rule_id,
    ))


def create_transfer(from_account_id, to_account_id, amount, transaction_date,
                    payee="Transfer", notes=None):
    return safe(lambda: service.create_transfer(
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        amount=amount,
        transaction_date=transaction_date,
        payee=payee,
        notes=notes,
    ))


def update_transaction(transaction_id, account_id=None, amount=None,
                       transaction_date=None, category_id=None,
                       payee=None, notes=None, recurring_rule_id=None):
    return safe(lambda: service.update_transaction(
        transaction_id,
        account_id=account_id,
        amount=amount,
        transaction_date=transaction_date,
        category_id=category_id,
        payee=payee,
        notes=notes,
        recurring_rule_id=recurring_rule_id,
    ))


def delete_transaction(transaction_id):
    return safe(lambda: service.delete_transaction(transaction_id))
