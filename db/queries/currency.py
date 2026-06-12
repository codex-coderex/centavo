from sqlalchemy import select, insert
from db.tables import currency
from db.connection import get_conn


def get_currencies():
    with get_conn() as conn:
        result = conn.execute(
            select(currency).order_by(currency.c.code)
        )
        return [dict(row._mapping) for row in result]


def get_currency(code: str):
    with get_conn() as conn:
        result = conn.execute(
            select(currency)
            .where(currency.c.code == code.upper())
        )
        row = result.first()
        return dict(row._mapping) if row else None


def seed_currency(code: str, name: str, symbol: str, decimal_places: int):
    with get_conn() as conn:
        conn.execute(
            insert(currency).values(
                code=code.upper(),
                name=name,
                symbol=symbol,
                decimal_places=decimal_places,
            )
        )