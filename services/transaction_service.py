from db.connection import get_conn

import db.queries.transactions as transactions_q
import db.queries.accounts as accounts_q
import db.queries.budgets as budgets_q
import db.queries.categories as categories_q
import db.queries.recurring as recurring_q

from utils.money import to_minor_units
from utils.dates import require_datetime


def get_transactions_by_user(user_id: int):
    return transactions_q.get_transactions_by_user(user_id)


def get_transactions_by_account(account_id: int):
    return transactions_q.get_transactions_by_account(account_id)


def get_transaction(transaction_id: int):
    return transactions_q.get_transaction(transaction_id)


def _get_account(account_id: int):
    account = accounts_q.get_account(account_id)

    if account is None:
        raise ValueError("Account does not exist")

    return account


def _ensure_active_account(account_id: int):
    account = _get_account(account_id)

    if account["status"] != "active":
        raise ValueError("Account is archived")

    return account


def _ensure_active_category(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if not category["is_active"]:
        raise ValueError("Category is inactive")

    group = categories_q.get_category_group(category["group_id"])

    if group is None or not group["is_active"]:
        raise ValueError("Category group is inactive")

    return category, group


def _validate_account_category(
    account_id: int,
    category_id: int,
    amount_minor: int,
    expected_type: str | None = None,
):
    account = _ensure_active_account(account_id)
    category, group = _ensure_active_category(category_id)

    if group["user_id"] != account["user_id"]:
        raise ValueError("Category does not belong to the account owner")

    if expected_type is not None:
        if group["type"] != expected_type:
            raise ValueError(f"Transaction requires a {expected_type} category")
    elif amount_minor > 0 and group["type"] != "income":
        raise ValueError("Positive transactions require an income category")
    elif amount_minor < 0 and group["type"] != "expense":
        raise ValueError("Negative transactions require an expense category")

    return account, category


def _validate_budget_item(
    budget_item_id: int | None,
    account,
    category_id: int,
    transaction_date,
):
    if budget_item_id is None:
        return

    budget_item = budgets_q.get_budget_item(budget_item_id)

    if budget_item is None:
        raise ValueError("Budget item does not exist")

    if budget_item["category_id"] != category_id:
        raise ValueError("Budget item does not match the transaction category")

    budget = budgets_q.get_budget(budget_item["budget_id"])

    if budget is None or budget["user_id"] != account["user_id"]:
        raise ValueError("Budget item does not belong to the account owner")

    if transaction_date < budget["start_date"]:
        raise ValueError("Transaction date is outside the budget period")

    if (
        budget["end_date"] is not None
        and transaction_date > budget["end_date"]
    ):
        raise ValueError("Transaction date is outside the budget period")


def _validate_recurring_rule(
    recurring_rule_id: int | None,
    account_id: int,
    category_id: int,
):
    if recurring_rule_id is None:
        return

    recurring = recurring_q.get_recurring_rule(recurring_rule_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    if (
        recurring["account_id"] != account_id
        or recurring["category_id"] != category_id
    ):
        raise ValueError(
            "Recurring rule does not match the transaction account and category"
        )


def create_transaction(
    account_id: int,
    amount,
    transaction_date,
    category_id: int,
    budget_item_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
):
    amount_minor = to_minor_units(amount)

    if amount_minor == 0:
        raise ValueError("Transaction amount cannot be zero")

    transaction_date = require_datetime(
        transaction_date,
        "Transaction date",
    )

    account, _ = _validate_account_category(
        account_id,
        category_id,
        amount_minor,
    )

    _validate_budget_item(
        budget_item_id,
        account,
        category_id,
        transaction_date,
    )

    _validate_recurring_rule(
        recurring_rule_id,
        account_id,
        category_id,
    )

    transaction_id = transactions_q.create_transaction(
        account_id=account_id,
        amount_minor=amount_minor,
        transaction_date=transaction_date,
        category_id=category_id,
        budget_item_id=budget_item_id,
        payee=payee,
        notes=notes,
        recurring_rule_id=recurring_rule_id,
        transfer_id=None,
    )

    return {"transaction_id": transaction_id}


def create_transfer(
    from_account_id: int,
    to_account_id: int,
    amount,
    transaction_date,
    category_id: int,
    payee: str | None = "Transfer",
    notes: str | None = None,
):
    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer to the same account")

    from_account = _ensure_active_account(from_account_id)
    to_account = _ensure_active_account(to_account_id)

    if from_account["user_id"] != to_account["user_id"]:
        raise ValueError(
            "Cannot transfer between accounts owned by different users"
        )

    amount_minor = to_minor_units(amount)

    if amount_minor <= 0:
        raise ValueError("Transfer amount must be greater than zero")

    transaction_date = require_datetime(
        transaction_date,
        "Transaction date",
    )

    _validate_account_category(
        from_account_id,
        category_id,
        -amount_minor,
        expected_type="transfer",
    )

    with get_conn() as conn:
        debit_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=from_account_id,
            amount_minor=-amount_minor,
            transaction_date=transaction_date,
            category_id=category_id,
            budget_item_id=None,
            payee=payee,
            notes=notes,
            recurring_rule_id=None,
            transfer_id=None,
        )

        credit_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=to_account_id,
            amount_minor=amount_minor,
            transaction_date=transaction_date,
            category_id=category_id,
            budget_item_id=None,
            payee=payee,
            notes=notes,
            recurring_rule_id=None,
            transfer_id=debit_id,
        )

        transactions_q.update_transaction_with_conn(
            conn,
            debit_id,
            transfer_id=debit_id,
        )

    return {
        "transfer_id": debit_id,
        "debit_transaction_id": debit_id,
        "credit_transaction_id": credit_id,
    }


def update_transaction(
    transaction_id: int,
    account_id: int | None = None,
    amount=None,
    transaction_date=None,
    category_id: int | None = None,
    budget_item_id: int | None = None,
    payee: str | None = None,
    notes: str | None = None,
    recurring_rule_id: int | None = None,
):
    transaction = transactions_q.get_transaction(transaction_id)

    if transaction is None:
        raise ValueError("Transaction does not exist")

    if transaction["transfer_id"] is not None:
        raise ValueError("Transfer transactions must be updated as a pair")

    kwargs = {}

    if account_id is not None:
        kwargs["account_id"] = account_id

    if amount is not None:
        amount_minor = to_minor_units(amount)

        if amount_minor == 0:
            raise ValueError("Transaction amount cannot be zero")

        kwargs["amount_minor"] = amount_minor

    if transaction_date is not None:
        kwargs["transaction_date"] = require_datetime(
            transaction_date,
            "Transaction date",
        )

    if category_id is not None:
        kwargs["category_id"] = category_id

    if budget_item_id is not None:
        kwargs["budget_item_id"] = budget_item_id

    if payee is not None:
        kwargs["payee"] = payee

    if notes is not None:
        kwargs["notes"] = notes

    if recurring_rule_id is not None:
        kwargs["recurring_rule_id"] = recurring_rule_id

    next_account_id = kwargs.get("account_id", transaction["account_id"])
    next_category_id = kwargs.get("category_id", transaction["category_id"])
    next_amount_minor = kwargs.get("amount_minor", transaction["amount_minor"])
    next_transaction_date = kwargs.get(
        "transaction_date",
        transaction["transaction_date"],
    )
    next_budget_item_id = kwargs.get(
        "budget_item_id",
        transaction["budget_item_id"],
    )
    next_recurring_rule_id = kwargs.get(
        "recurring_rule_id",
        transaction["recurring_rule_id"],
    )

    account, _ = _validate_account_category(
        next_account_id,
        next_category_id,
        next_amount_minor,
    )

    _validate_budget_item(
        next_budget_item_id,
        account,
        next_category_id,
        next_transaction_date,
    )

    _validate_recurring_rule(
        next_recurring_rule_id,
        next_account_id,
        next_category_id,
    )

    if kwargs:
        transactions_q.update_transaction(transaction_id, **kwargs)

    return {"status": "updated"}


def delete_transaction(transaction_id: int):
    transaction = transactions_q.get_transaction(transaction_id)

    if transaction is None:
        raise ValueError("Transaction does not exist")

    if transaction["transfer_id"] is not None:
        raise ValueError("Transfer transactions must be deleted as a pair")

    transactions_q.delete_transaction(transaction_id)

    return {"status": "deleted"}


def update_transfer(
    transfer_id: int,
    amount=None,
    transaction_date=None,
    payee: str | None = None,
    notes: str | None = None,
):
    transactions = transactions_q.get_transactions_by_transfer(
        transfer_id
    )

    if len(transactions) != 2:
        raise ValueError("Transfer pair does not exist")

    debit_transaction = next(
        (
            transaction
            for transaction in transactions
            if transaction["amount_minor"] < 0
        ),
        None,
    )

    credit_transaction = next(
        (
            transaction
            for transaction in transactions
            if transaction["amount_minor"] > 0
        ),
        None,
    )

    if debit_transaction is None or credit_transaction is None:
        raise ValueError("Invalid transfer pair")

    debit_values = {}
    credit_values = {}

    if amount is not None:
        amount_minor = to_minor_units(amount)

        if amount_minor <= 0:
            raise ValueError("Transfer amount must be greater than zero")

        debit_values["amount_minor"] = -amount_minor
        credit_values["amount_minor"] = amount_minor

    if transaction_date is not None:
        transaction_date = require_datetime(
            transaction_date,
            "Transaction date",
        )

        debit_values["transaction_date"] = transaction_date
        credit_values["transaction_date"] = transaction_date

    if payee is not None:
        debit_values["payee"] = payee
        credit_values["payee"] = payee

    if notes is not None:
        debit_values["notes"] = notes
        credit_values["notes"] = notes

    if debit_values:
        with get_conn() as conn:
            transactions_q.update_transaction_with_conn(
                conn,
                debit_transaction["transaction_id"],
                **debit_values,
            )

            transactions_q.update_transaction_with_conn(
                conn,
                credit_transaction["transaction_id"],
                **credit_values,
            )

    return {"status": "updated"}


def delete_transfer(transfer_id: int):
    transactions = transactions_q.get_transactions_by_transfer(
        transfer_id
    )

    if len(transactions) != 2:
        raise ValueError("Transfer pair does not exist")

    with get_conn() as conn:
        transactions_q.delete_transactions_by_transfer_with_conn(
            conn,
            transfer_id,
        )

    return {"status": "deleted"}
