from sqlalchemy import select, insert, update, delete, func
from db.tables import (
    category,
    category_group,
    transaction,
    budget_item,
    recurring_rule,
)
from db.connection import get_conn


def get_category_groups(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category_group)
            .where(category_group.c.user_id == user_id)
            .where(category_group.c.is_active.is_(True))
            .order_by(category_group.c.type, category_group.c.name)
        )
        return [dict(row._mapping) for row in result]


def get_category_group(group_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category_group).where(category_group.c.group_id == group_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def get_categories_by_group(group_id: int, active_only: bool = False):
    with get_conn() as conn:
        stmt = select(category).where(category.c.group_id == group_id)

        if active_only:
            stmt = stmt.where(category.c.is_active.is_(True))

        result = conn.execute(stmt.order_by(category.c.name))
        return [dict(row._mapping) for row in result]


def get_all_categories(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category)
            .join(category_group, category.c.group_id == category_group.c.group_id)
            .where(category_group.c.user_id == user_id)
            .where(category_group.c.is_active.is_(True))
            .where(category.c.is_active.is_(True))
            .order_by(category_group.c.type, category.c.name)
        )
        return [dict(row._mapping) for row in result]


def get_category(category_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category).where(category.c.category_id == category_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None


def create_category_group(
    user_id: int,
    name: str,
    type: str,
    is_system: bool = False,
):
    values = {
        "user_id": user_id,
        "name": name,
        "type": type,
        "is_system": is_system,
    }

    with get_conn() as conn:
        result = conn.execute(insert(category_group).values(**values))
        return result.inserted_primary_key[0]


def create_category(
    group_id: int,
    name: str,
    is_system: bool = False,
):
    values = {
        "group_id": group_id,
        "name": name,
        "is_system": is_system,
    }

    with get_conn() as conn:
        result = conn.execute(insert(category).values(**values))
        return result.inserted_primary_key[0]


def update_category_group(group_id: int, **kwargs):
    allowed = {"name", "type", "is_active"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return None

    with get_conn() as conn:
        conn.execute(
            update(category_group)
            .where(category_group.c.group_id == group_id)
            .values(**clean_values)
        )


def update_category(category_id: int, **kwargs):
    allowed = {"name", "is_active"}
    clean_values = {k: v for k, v in kwargs.items() if k in allowed}

    if not clean_values:
        return None

    with get_conn() as conn:
        conn.execute(
            update(category)
            .where(category.c.category_id == category_id)
            .values(**clean_values)
        )


def delete_category_group(group_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(category_group)
            .where(category_group.c.group_id == group_id)
        )


def delete_category(category_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(category)
            .where(category.c.category_id == category_id)
        )


def delete_categories_by_group(group_id: int):
    with get_conn() as conn:
        conn.execute(
            delete(category)
            .where(category.c.group_id == group_id)
        )


def category_has_references(category_id: int) -> bool:
    with get_conn() as conn:
        has_transaction = conn.execute(
            select(transaction.c.transaction_id)
            .where(transaction.c.category_id == category_id)
            .limit(1)
        ).first()

        if has_transaction:
            return True

        has_budget_item = conn.execute(
            select(budget_item.c.budget_item_id)
            .where(budget_item.c.category_id == category_id)
            .limit(1)
        ).first()

        if has_budget_item:
            return True

        has_recurring = conn.execute(
            select(recurring_rule.c.recurring_rule_id)
            .where(recurring_rule.c.category_id == category_id)
            .limit(1)
        ).first()

        return has_recurring is not None


def get_category_reference_counts(category_id: int):
    with get_conn() as conn:
        transaction_count = conn.execute(
            select(func.count())
            .select_from(transaction)
            .where(transaction.c.category_id == category_id)
        ).scalar_one()

        budget_item_count = conn.execute(
            select(func.count())
            .select_from(budget_item)
            .where(budget_item.c.category_id == category_id)
        ).scalar_one()

        recurring_count = conn.execute(
            select(func.count())
            .select_from(recurring_rule)
            .where(recurring_rule.c.category_id == category_id)
        ).scalar_one()

    return {
        "transactions": transaction_count,
        "budget_items": budget_item_count,
        "recurring": recurring_count,
    }


def group_has_referenced_categories(group_id: int) -> bool:
    category_ids = (
        select(category.c.category_id)
        .where(category.c.group_id == group_id)
    )

    with get_conn() as conn:
        has_transaction = conn.execute(
            select(transaction.c.transaction_id)
            .where(transaction.c.category_id.in_(category_ids))
            .limit(1)
        ).first()

        if has_transaction:
            return True

        has_budget_item = conn.execute(
            select(budget_item.c.budget_item_id)
            .where(budget_item.c.category_id.in_(category_ids))
            .limit(1)
        ).first()

        if has_budget_item:
            return True

        has_recurring = conn.execute(
            select(recurring_rule.c.recurring_rule_id)
            .where(recurring_rule.c.category_id.in_(category_ids))
            .limit(1)
        ).first()

        return has_recurring is not None
