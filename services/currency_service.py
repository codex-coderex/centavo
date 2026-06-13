import db.queries.currency as currency_q
import db.queries.users as users_q
import db.queries.accounts as accounts_q


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


def get_user_currency(user_id: int):
    user = users_q.get_user(user_id)

    if user is None:
        raise ValueError("User does not exist")

    return get_currency(user["currency_code"])


def get_user_decimal_places(user_id: int) -> int:
    currency = get_user_currency(user_id)
    return currency["decimal_places"]


def get_account_decimal_places(account_id: int) -> int:
    account = accounts_q.get_account(account_id)

    if account is None:
        raise ValueError("Account does not exist")

    return get_user_decimal_places(account["user_id"])


def ensure_currency_exists(code: str) -> str:
    currency = get_currency(code)
    return currency["code"]