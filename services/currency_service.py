import db.queries.currency as currency_q


def get_currencies():
    return currency_q.get_currencies()


def get_currency(code: str):
    code = code.strip().upper()

    if not code:
        raise ValueError("Currency code is required")

    currency = currency_q.get_currency(code)

    if currency is None:
        raise ValueError("Currency does not exist")

    return currency


def get_currency_decimal_places(code: str) -> int:
    currency = get_currency(code)
    return currency["decimal_places"]