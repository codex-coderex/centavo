from datetime import datetime
from dateutil.relativedelta import relativedelta

import db.queries.recurring as recurring_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q
import db.queries.transactions as transactions_q

from services.currency_service import get_account_decimal_places
from utils.money import to_minor_units
from utils.enums import FrequencyUnit, RecurringStatus, normalize_enum_value


def get_recurring(user_id: int):
    return recurring_q.get_recurring(user_id)


def get_recurring_by_id(recurring_id: int):
    return recurring_q.get_recurring_by_id(recurring_id)


def get_due_recurring():
    return recurring_q.get_due_recurring()


def _ensure_account_exists(account_id: int):
    account = accounts_q.get_account(account_id)

    if account is None:
        raise ValueError("Account does not exist")

    return account


def _ensure_active_category_exists(category_id: int):
    category = categories_q.get_category(category_id)

    if category is None:
        raise ValueError("Category does not exist")

    if not category["is_active"]:
        raise ValueError("Category is inactive")

    return category


def create_recurring(
    account_id: int,
    amount,
    interval: int,
    frequency_unit: str,
    next_due: str,
    category_id: int,
    merchant: str | None = None,
    end_date: str | None = None,
):
    _ensure_account_exists(account_id)
    _ensure_active_category_exists(category_id)

    if interval <= 0:
        raise ValueError("Interval must be greater than zero")

    frequency_unit = normalize_enum_value(
        frequency_unit,
        FrequencyUnit,
        "Invalid frequency unit",
    )

    decimal_places = get_account_decimal_places(account_id)
    amount_minor = to_minor_units(amount, decimal_places)

    if amount_minor == 0:
        raise ValueError("Recurring amount cannot be zero")

    recurring_id = recurring_q.create_recurring(
        account_id=account_id,
        amount_minor=amount_minor,
        interval=interval,
        frequency_unit=frequency_unit,
        next_due=next_due,
        category_id=category_id,
        merchant=merchant,
        end_date=end_date,
    )

    return {"recurring_id": recurring_id}


def update_recurring(recurring_id: int, **kwargs):
    recurring = recurring_q.get_recurring_by_id(recurring_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    clean_values = {}

    if "account_id" in kwargs:
        account_id = kwargs["account_id"]
        _ensure_account_exists(account_id)
        clean_values["account_id"] = account_id

    if "category_id" in kwargs:
        category_id = kwargs["category_id"]
        _ensure_active_category_exists(category_id)
        clean_values["category_id"] = category_id

    if "amount" in kwargs:
        account_id_for_currency = clean_values.get(
            "account_id",
            recurring["account_id"],
        )
        decimal_places = get_account_decimal_places(account_id_for_currency)
        amount_minor = to_minor_units(kwargs["amount"], decimal_places)

        if amount_minor == 0:
            raise ValueError("Recurring amount cannot be zero")

        clean_values["amount_minor"] = amount_minor

    if "interval" in kwargs:
        interval = kwargs["interval"]
        if interval <= 0:
            raise ValueError("Interval must be greater than zero")
        clean_values["interval"] = interval

    if "frequency_unit" in kwargs:
        clean_values["frequency_unit"] = normalize_enum_value(
            kwargs["frequency_unit"],
            FrequencyUnit,
            "Invalid frequency unit",
        )

    if "next_due" in kwargs:
        clean_values["next_due"] = kwargs["next_due"]

    if "merchant" in kwargs:
        clean_values["merchant"] = kwargs["merchant"]

    if "end_date" in kwargs:
        clean_values["end_date"] = kwargs["end_date"]

    if "status" in kwargs:
        clean_values["status"] = normalize_enum_value(
            kwargs["status"],
            RecurringStatus,
            "Invalid recurring status",
        )

    if clean_values:
        recurring_q.update_recurring(recurring_id, **clean_values)


def pause_recurring(recurring_id: int):
    recurring = recurring_q.get_recurring_by_id(recurring_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    recurring_q.pause_recurring(recurring_id)


def resume_recurring(recurring_id: int):
    recurring = recurring_q.get_recurring_by_id(recurring_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    recurring_q.resume_recurring(recurring_id)


def deactivate_recurring(recurring_id: int):
    recurring = recurring_q.get_recurring_by_id(recurring_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    recurring_q.deactivate_recurring(recurring_id)


def generate_transaction(recurring_id: int):
    recurring = recurring_q.get_recurring_by_id(recurring_id)

    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    if recurring["status"] != RecurringStatus.ACTIVE:
        raise ValueError("Recurring rule is not active")

    category = categories_q.get_category(recurring["category_id"])
    if category is None:
        raise ValueError("Recurring category does not exist")

    if not category["is_active"]:
        raise ValueError("Recurring category is inactive")

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

    frequency_unit = normalize_enum_value(
        frequency_unit,
        FrequencyUnit,
        "Invalid frequency unit",
    )

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