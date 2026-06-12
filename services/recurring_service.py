from datetime import datetime
from dateutil.relativedelta import relativedelta

import db.queries.recurring as recurring_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q
import db.queries.transactions as transactions_q
from utils.money import to_minor_units
from utils.enums import FrequencyUnit, RecurringStatus


def get_recurring(user_id: int):
    return recurring_q.get_recurring(user_id)


def get_recurring_by_id(recurring_id: int):
    return recurring_q.get_recurring_by_id(recurring_id)


def get_due_recurring():
    return recurring_q.get_due_recurring()


def create_recurring(
    account_id: int,
    amount,
    interval: int,
    frequency_unit: str,
    next_due: str,
    category_id: int,
    merchant: str | None = None,
    end_date: str | None = None,
    decimal_places: int = 2,
):
    frequency_unit = frequency_unit.strip().lower()

    if accounts_q.get_account(account_id) is None:
        raise ValueError("Account does not exist")

    if categories_q.get_category(category_id) is None:
        raise ValueError("Category does not exist")

    if interval <= 0:
        raise ValueError("Interval must be greater than zero")

    if frequency_unit not in FrequencyUnit:
        raise ValueError("Invalid frequency unit")

    recurring_id = recurring_q.create_recurring(
        account_id=account_id,
        amount_minor=to_minor_units(amount, decimal_places),
        interval=interval,
        frequency_unit=frequency_unit,
        next_due=next_due,
        category_id=category_id,
        merchant=merchant,
        end_date=end_date,
    )

    return {"recurring_id": recurring_id}


def update_recurring(recurring_id: int, **kwargs):
    if "amount" in kwargs:
        decimal_places = kwargs.pop("decimal_places", 2)
        kwargs["amount_minor"] = to_minor_units(kwargs.pop("amount"), decimal_places)

    if "frequency_unit" in kwargs:
        kwargs["frequency_unit"] = kwargs["frequency_unit"].strip().lower()
        if kwargs["frequency_unit"] not in FrequencyUnit:
            raise ValueError("Invalid frequency unit")

    if "status" in kwargs and kwargs["status"] not in RecurringStatus:
        raise ValueError("Invalid recurring status")

    if kwargs:
        recurring_q.update_recurring(recurring_id, **kwargs)


def pause_recurring(recurring_id: int):
    recurring_q.pause_recurring(recurring_id)


def resume_recurring(recurring_id: int):
    recurring_q.resume_recurring(recurring_id)


def deactivate_recurring(recurring_id: int):
    recurring_q.deactivate_recurring(recurring_id)


def generate_transaction(recurring_id: int):
    recurring = recurring_q.get_recurring_by_id(recurring_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    if recurring["status"] != RecurringStatus.ACTIVE:
        raise ValueError("Recurring rule is not active")

    transaction_id = transactions_q.create_transaction(
        account_id=recurring["account_id"],
        amount_minor=recurring["amount_minor"],
        txn_date=datetime.now(),
        category_id=recurring["category_id"],
        merchant=recurring["merchant"],
        recurring_id=recurring_id,
    )

    next_due = calculate_next_due(
        recurring["next_due"],
        recurring["interval"],
        recurring["frequency_unit"],
    )

    end_date = recurring["end_date"]

    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    if end_date and next_due > end_date:
        recurring_q.deactivate_recurring(recurring_id)
    else:
        recurring_q.update_recurring(recurring_id, next_due=next_due)

    return {"transaction_id": transaction_id}


def calculate_next_due(current_due, interval: int, frequency_unit: str):
    if isinstance(current_due, str):
        current_due = datetime.fromisoformat(current_due)

    match frequency_unit:
        case FrequencyUnit.DAY:
            return current_due + relativedelta(days=interval)
        case FrequencyUnit.WEEK:
            return current_due + relativedelta(weeks=interval)
        case FrequencyUnit.MONTH:
            return current_due + relativedelta(months=interval)
        case FrequencyUnit.YEAR:
            return current_due + relativedelta(years=interval)
        case _:
            raise ValueError("Invalid frequency unit")