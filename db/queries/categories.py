from sqlalchemy import select, insert, update
from db.tables import category, category_group
from db.connection import get_conn

def get_category_groups(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category_group).where(category_group.c.user_id == user_id)
        )
        return [dict(row._mapping) for row in result]

def get_categories(group_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category).where(category.c.group_id == group_id)
        )
        return [dict(row._mapping) for row in result]

def get_all_categories(user_id: int):
    with get_conn() as conn:
        result = conn.execute(
            select(category)
            .join(category_group, category.c.group_id == category_group.c.group_id)
            .where(category_group.c.user_id == user_id)
            .where(category.c.is_active == True)
        )
        return [dict(row._mapping) for row in result]

def create_category_group(user_id: int, name: str, type: str):
    with get_conn() as conn:
        result = conn.execute(
            insert(category_group).values(
                user_id=user_id,
                name=name,
                type=type
            )
        )
        return result.inserted_primary_key[0]

def create_category(group_id: int, name: str, color: str = None, is_system: bool = False):
    with get_conn() as conn:
        result = conn.execute(
            insert(category).values(
                group_id=group_id,
                name=name,
                color=color,
                is_system=is_system,
                is_active=True
            )
        )
        return result.inserted_primary_key[0]

def update_category(category_id: int, **kwargs):
    with get_conn() as conn:
        conn.execute(
            update(category)
            .where(category.c.category_id == category_id)
            .values(**kwargs)
        )

def deactivate_category(category_id: int):
    with get_conn() as conn:
        conn.execute(
            update(category)
            .where(category.c.category_id == category_id)
            .values(is_active=False)
        )