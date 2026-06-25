from datetime import datetime
from dateutil.relativedelta import relativedelta

from db.connection import get_conn

import db.queries.recurring as recurring_q
import db.queries.accounts as accounts_q
import db.queries.categories as categories_q
import db.queries.transactions as transactions_q

from utils.money import to_minor_units
from utils.enums import FrequencyUnit, RecurringStatus, normalize_enum_value
from utils.dates import parse_datetime, require_datetime


def get_recurring_rules(user_id: int):
    return recurring_q.get_recurring_rules(user_id)


def get_recurring_rule(recurring_rule_id: int):
    return recurring_q.get_recurring_rule(recurring_rule_id)


def get_due_recurring_rules(as_of=None):
    return recurring_q.get_due_recurring_rules(as_of=as_of)


def _ensure_active_account(account_id: int):
    account = accounts_q.get_account(account_id)
    if account is None:
        raise ValueError("Account does not exist")
    if account["status"] != "active":
        raise ValueError("Account is archived")
    return account


def _ensure_active_category(category_id: int):
    category = categories_q.get_category(category_id)
    if category is None:
        raise ValueError("Category does not exist")
    if not category["is_active"]:
        raise ValueError("Category is inactive")
    return category


def _validate_account_category(
    account_id: int,
    category_id: int,
    amount_minor: int,
):
    account = _ensure_active_account(account_id)
    category = _ensure_active_category(category_id)
    group = categories_q.get_category_group(category["group_id"])

    if group is None or group["user_id"] != account["user_id"]:
        raise ValueError("Category does not belong to the account owner")

    if amount_minor > 0 and group["type"] != "income":
        raise ValueError("Positive recurring amounts require an income category")

    if amount_minor < 0 and group["type"] != "expense":
        raise ValueError("Negative recurring amounts require an expense category")


def create_recurring_rule(
    account_id: int,
    category_id: int,
    name: str,
    expected_amount,
    interval: int,
    frequency_unit: str,
    start_date,
    next_due_date,
    end_date=None,
):
    name = name.strip()

    if not name:
        raise ValueError("Recurring rule name is required")

    if interval <= 0:
        raise ValueError("Interval must be greater than zero")

    frequency_unit = normalize_enum_value(
        frequency_unit,
        FrequencyUnit,
        "Invalid frequency unit",
    )

    expected_amount_minor = to_minor_units(expected_amount)

    if expected_amount_minor == 0:
        raise ValueError("Recurring amount cannot be zero")

    _validate_account_category(
        account_id,
        category_id,
        expected_amount_minor,
    )

    start_date = require_datetime(start_date, "Start date")
    next_due_date = require_datetime(next_due_date, "Next due date")
    end_date = parse_datetime(end_date, "End date")

    if next_due_date < start_date:
        raise ValueError("Next due date cannot be before start date")

    if end_date is not None and end_date < next_due_date:
        raise ValueError("End date cannot be before next due date")

    recurring_rule_id = recurring_q.create_recurring_rule(
        account_id=account_id,
        category_id=category_id,
        name=name,
        expected_amount_minor=expected_amount_minor,
        interval=interval,
        frequency_unit=frequency_unit,
        start_date=start_date,
        next_due_date=next_due_date,
        end_date=end_date,
    )

    return {"recurring_rule_id": recurring_rule_id}


def update_recurring_rule(recurring_rule_id: int, **kwargs):
    recurring = recurring_q.get_recurring_rule(recurring_rule_id)
    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    clean_values = {}

    if "account_id" in kwargs:
        clean_values["account_id"] = kwargs["account_id"]

    if "category_id" in kwargs:
        clean_values["category_id"] = kwargs["category_id"]

    if "name" in kwargs:
        name = kwargs["name"].strip()

        if not name:
            raise ValueError("Recurring rule name cannot be empty")

        clean_values["name"] = name

    if "expected_amount" in kwargs:
        expected_amount_minor = to_minor_units(kwargs["expected_amount"])

        if expected_amount_minor == 0:
            raise ValueError("Recurring amount cannot be zero")

        clean_values["expected_amount_minor"] = expected_amount_minor

    if "interval" in kwargs:
        if kwargs["interval"] <= 0:
            raise ValueError("Interval must be greater than zero")

        clean_values["interval"] = kwargs["interval"]

    if "frequency_unit" in kwargs:
        clean_values["frequency_unit"] = normalize_enum_value(
            kwargs["frequency_unit"],
            FrequencyUnit,
            "Invalid frequency unit",
        )

    if "start_date" in kwargs:
        clean_values["start_date"] = require_datetime(
            kwargs["start_date"],
            "Start date",
        )

    if "next_due_date" in kwargs:
        clean_values["next_due_date"] = require_datetime(
            kwargs["next_due_date"],
            "Next due date",
        )

    if "end_date" in kwargs:
        clean_values["end_date"] = parse_datetime(
            kwargs["end_date"],
            "End date",
        )

    if "status" in kwargs:
        clean_values["status"] = normalize_enum_value(
            kwargs["status"],
            RecurringStatus,
            "Invalid recurring status",
        )

    next_account_id = clean_values.get("account_id", recurring["account_id"])
    next_category_id = clean_values.get("category_id", recurring["category_id"])
    next_amount_minor = clean_values.get(
        "expected_amount_minor",
        recurring["expected_amount_minor"],
    )

    _validate_account_category(
        next_account_id,
        next_category_id,
        next_amount_minor,
    )

    start_date = clean_values.get("start_date", recurring["start_date"])
    next_due_date = clean_values.get("next_due_date", recurring["next_due_date"])
    end_date = clean_values.get("end_date", recurring["end_date"])

    if next_due_date < start_date:
        raise ValueError("Next due date cannot be before start date")

    if end_date is not None and end_date < next_due_date:
        raise ValueError("End date cannot be before next due date")

    if clean_values:
        recurring_q.update_recurring_rule(recurring_rule_id, **clean_values)

    return {"status": "updated"}


def pause_recurring_rule(recurring_rule_id: int):
    if recurring_q.get_recurring_rule(recurring_rule_id) is None:
        raise ValueError("Recurring rule does not exist")

    recurring_q.update_recurring_rule(
        recurring_rule_id,
        status=RecurringStatus.PAUSED.value,
    )

    return {"status": "paused"}


def resume_recurring_rule(recurring_rule_id: int):
    if recurring_q.get_recurring_rule(recurring_rule_id) is None:
        raise ValueError("Recurring rule does not exist")

    recurring_q.update_recurring_rule(
        recurring_rule_id,
        status=RecurringStatus.ACTIVE.value,
    )

    return {"status": "active"}


def deactivate_recurring_rule(recurring_rule_id: int):
    if recurring_q.get_recurring_rule(recurring_rule_id) is None:
        raise ValueError("Recurring rule does not exist")

    recurring_q.update_recurring_rule(
        recurring_rule_id,
        status=RecurringStatus.INACTIVE.value,
    )

    return {"status": "inactive"}


def _generate_transaction_for_rule(
    recurring_rule_id: int,
    transaction_date,
    advance_next_due: bool,
):
    recurring = recurring_q.get_recurring_rule(recurring_rule_id)
    if recurring is None:
        raise ValueError("Recurring rule does not exist")
    if recurring["status"] != RecurringStatus.ACTIVE.value:
        raise ValueError("Recurring rule is not active")

    _validate_account_category(
        recurring["account_id"],
        recurring["category_id"],
        recurring["expected_amount_minor"],
    )

    with get_conn() as conn:
        transaction_id = transactions_q.create_transaction_with_conn(
            conn=conn,
            account_id=recurring["account_id"],
            amount_minor=recurring["expected_amount_minor"],
            transaction_date=transaction_date,
            category_id=recurring["category_id"],
            payee=recurring["name"],
            notes=None,
            recurring_rule_id=recurring_rule_id,
            transfer_id=None,
        )

        if advance_next_due:
            next_due_date = calculate_next_due(
                recurring["next_due_date"],
                recurring["interval"],
                recurring["frequency_unit"],
            )

            end_date = recurring["end_date"]

            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date)

            if end_date is not None and next_due_date > end_date:
                recurring_q.update_recurring_rule_with_conn(
                    conn,
                    recurring_rule_id,
                    status=RecurringStatus.INACTIVE.value,
                )
            else:
                recurring_q.update_recurring_rule_with_conn(
                    conn,
                    recurring_rule_id,
                    next_due_date=next_due_date,
                )

    return {"transaction_id": transaction_id}


def generate_transaction(recurring_rule_id: int):
    return _generate_transaction_for_rule(
        recurring_rule_id=recurring_rule_id,
        transaction_date=datetime.now().date().isoformat(),
        advance_next_due=False,
    )


def generate_due_transaction(recurring_rule_id: int):
    recurring = recurring_q.get_recurring_rule(recurring_rule_id)
    if recurring is None:
        raise ValueError("Recurring rule does not exist")

    return _generate_transaction_for_rule(
        recurring_rule_id=recurring_rule_id,
        transaction_date=recurring["next_due_date"],
        advance_next_due=True,
    )


def calculate_next_due(current_due, interval: int, frequency_unit: str):
    if isinstance(current_due, str):
        current_due = datetime.fromisoformat(current_due)

    frequency_unit = normalize_enum_value(
        frequency_unit,
        FrequencyUnit,
        "Invalid frequency unit",
    )

    match frequency_unit:
        case "day":
            return current_due + relativedelta(days=interval)
        case "week":
            return current_due + relativedelta(weeks=interval)
        case "month":
            return current_due + relativedelta(months=interval)
        case "year":
            return current_due + relativedelta(years=interval)
        case _:
            raise ValueError("Invalid frequency unit")
