from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import traceback


def serialize(value):
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {key: serialize(inner_value) for key, inner_value in value.items()}

    if isinstance(value, list):
        return [serialize(item) for item in value]

    if isinstance(value, tuple):
        return [serialize(item) for item in value]

    return value


def ok(data=None):
    return {"ok": True, "data": serialize(data)}


def fail(error):
    return {"ok": False, "error": str(error)}


def safe(fn):
    try:
        return ok(fn())
    except Exception as e:
        traceback.print_exc()
        return fail(e)
