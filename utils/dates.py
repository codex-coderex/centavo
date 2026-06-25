from calendar import monthrange
from datetime import date, datetime, timedelta


def parse_datetime(value, field_name: str):
    if value is None or value == "":
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid date")

    raise ValueError(f"{field_name} must be a valid date")


def require_datetime(value, field_name: str):
    parsed = parse_datetime(value, field_name)

    if parsed is None:
        raise ValueError(f"{field_name} is required")

    return parsed


def calculate_period_end(start_date: datetime, period_type: str):
    if period_type == "weekly":
        return start_date + timedelta(days=6)

    if period_type == "monthly":
        last_day = monthrange(start_date.year, start_date.month)[1]
        return start_date.replace(day=last_day)

    if period_type == "quarterly":
        quarter_end_month = ((start_date.month - 1) // 3 + 1) * 3
        last_day = monthrange(start_date.year, quarter_end_month)[1]

        return start_date.replace(
            month=quarter_end_month,
            day=last_day,
        )

    if period_type == "yearly":
        return start_date.replace(month=12, day=31)

    raise ValueError("Invalid budget period")