from datetime import date, datetime


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