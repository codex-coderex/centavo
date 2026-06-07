import db.queries.currency as q


def get_currencies():
    return q.get_currencies()


def get_currency(code):
    return q.get_currency(code)


def create_currency(code, name, symbol, decimal_places=2):
    q.create_currency(code, name, symbol, decimal_places)
