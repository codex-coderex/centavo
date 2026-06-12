from enum import StrEnum


class AccountStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class CategoryGroupType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class BudgetPeriod(StrEnum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"


class RecurringStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"


class FrequencyUnit(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class TransactionStatus(StrEnum):
    PENDING = "pending"
    CLEARED = "cleared"
    VOID = "void"


def enum_values(enum_cls) -> set[str]:
    return {member.value for member in enum_cls}


def normalize_enum_value(value: str, enum_cls, error_message: str) -> str:
    value = value.strip().lower()

    if value not in enum_values(enum_cls):
        raise ValueError(error_message)

    return value