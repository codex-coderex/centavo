from sqlalchemy import select, insert, update
from db.tables import transaction
from db.connection import get_conn
from datetime import datetime

def get_transactions(account_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction).where(transaction.c.account_id == account_id)
            .order_by(transaction.c.txn_date.desc())
        )
        return [dict(row._mapping) for row in result]

def get_transaction(transaction_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(transaction).where(transaction.c.transaction_id == transaction_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None

def create_transaction(account_id: int, amount: float, txn_date: str,
                        merchant: str = None, category_id: int = None,
                        note: str = None, goal_id: int = None,
                        recurring_id: int = None):
    with get_conn() as conn:
        result = conn.execute(
            insert(transaction).values(
                account_id=account_id,
                amount=amount,
                txn_date=txn_date,
                merchant=merchant,
                category_id=category_id,
                note=note,
                goal_id=goal_id,
                recurring_id=recurring_id,
                status="cleared",
                needs_review=False,
                updated_at=datetime.now()
            )
        )
        return result.inserted_primary_key[0]

def create_transfer(from_account_id: int, to_account_id: int,
                    amount: float, txn_date: str):
    with get_conn() as conn:
        # debit side
        debit = conn.execute(
            insert(transaction).values(
                account_id=from_account_id,
                amount=-amount,
                txn_date=txn_date,
                status="cleared",
                needs_review=False,
                updated_at=datetime.now()
            )
        )
        debit_id = debit.inserted_primary_key[0]

        # credit side
        credit = conn.execute(
            insert(transaction).values(
                account_id=to_account_id,
                amount=amount,
                txn_date=txn_date,
                transfer_pair_id=debit_id,
                status="cleared",
                needs_review=False,
                updated_at=datetime.now()
            )
        )
        credit_id = credit.inserted_primary_key[0]

        # link debit back to credit
        conn.execute(
            update(transaction)
            .where(transaction.c.transaction_id == debit_id)
            .values(transfer_pair_id=credit_id)
        )

        return debit_id, credit_id

def update_transaction(transaction_id: int, **kwargs):
    kwargs["updated_at"] = datetime.now()
    with get_conn() as conn:
        conn.execute(
            update(transaction)
            .where(transaction.c.transaction_id == transaction_id)
            .values(**kwargs)
        )

def flag_for_review(transaction_id: int):
    with get_conn() as conn:
        conn.execute(
            update(transaction)
            .where(transaction.c.transaction_id == transaction_id)
            .values(needs_review=True, updated_at=datetime.now())
        )