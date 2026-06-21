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


class AccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    LINE_OF_CREDIT = "line_of_credit"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    INVESTMENT = "investment"
    OTHER_ASSET = "other_asset"
    OTHER_LIABILITY = "other_liability"


def enum_values(enum_cls) -> set[str]:
    return {member.value for member in enum_cls}


def normalize_enum_value(value, enum_cls, error_message: str) -> str:
    if value is None:
        raise ValueError(error_message)

    normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")

    if normalized not in enum_values(enum_cls):
        raise ValueError(error_message)

    return normalized