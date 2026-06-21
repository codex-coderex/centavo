import services.transaction_service as service
from api.responses import ok, fail


def get_transactions_by_user(user_id):
    try:
        return ok(service.get_transactions_by_user(user_id))
    except ValueError as e:
        return fail(e)


def get_transactions_by_account(account_id):
    try:
        return ok(service.get_transactions_by_account(account_id))
    except ValueError as e:
        return fail(e)


def get_transaction(transaction_id):
    try:
        return ok(service.get_transaction(transaction_id))
    except ValueError as e:
        return fail(e)


def create_transaction(account_id, amount, transaction_date, category_id=None,
                       payee=None, notes=None, recurring_rule_id=None):
    try:
        return ok(
            service.create_transaction(
                account_id=account_id,
                amount=amount,
                transaction_date=transaction_date,
                category_id=category_id,
                payee=payee,
                notes=notes,
                recurring_rule_id=recurring_rule_id,
            )
        )
    except ValueError as e:
        return fail(e)


def create_transfer(from_account_id, to_account_id, amount, transaction_date,
                    payee="Transfer", notes=None):
    try:
        return ok(
            service.create_transfer(
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                transaction_date=transaction_date,
                payee=payee,
                notes=notes,
            )
        )
    except ValueError as e:
        return fail(e)


def update_transaction(transaction_id, account_id=None, amount=None,
                       transaction_date=None, category_id=None,
                       payee=None, notes=None, recurring_rule_id=None):
    try:
        return ok(
            service.update_transaction(
                transaction_id,
                account_id=account_id,
                amount=amount,
                transaction_date=transaction_date,
                category_id=category_id,
                payee=payee,
                notes=notes,
                recurring_rule_id=recurring_rule_id,
            )
        )
    except ValueError as e:
        return fail(e)


def delete_transaction(transaction_id):
    try:
        return ok(service.delete_transaction(transaction_id))
    except ValueError as e:
        return fail(e)
