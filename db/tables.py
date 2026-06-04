from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Numeric, Boolean, DateTime, Text,
    ForeignKey
)

metadata = MetaData()

user = Table("user", metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

currency = Table("currency", metadata,
    Column("code", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("symbol", String, nullable=False),
    Column("decimal_places", Integer, nullable=False, default=2),
)

account = Table("account", metadata,
    Column("account_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("currency_code", String, ForeignKey("currency.code"), nullable=False),
    Column("name", String, nullable=False),
    Column("type", String, nullable=False),
    Column("status", String, nullable=False, default="active"),
)

category_group = Table("category_group", metadata,
    Column("group_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("type", String, nullable=False),
)

category = Table("category", metadata,
    Column("category_id", Integer, primary_key=True, autoincrement=True),
    Column("group_id", Integer, ForeignKey("category_group.group_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("color", String),
    Column("is_system", Boolean, nullable=False, default=False),
    Column("is_active", Boolean, nullable=False, default=True),
)

tag = Table("tag", metadata,
    Column("tag_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("color", String),
)

transaction = Table("transaction", metadata,
    Column("transaction_id", Integer, primary_key=True, autoincrement=True),
    Column("account_id", Integer, ForeignKey("account.account_id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id")),
    Column("recurring_id", Integer, ForeignKey("recurring.recurring_id")),
    Column("transfer_pair_id", Integer, ForeignKey("transaction.transaction_id")),
    Column("goal_id", Integer, ForeignKey("goal.goal_id")),  # ← added
    Column("merchant", String),
    Column("amount", Numeric, nullable=False),
    Column("txn_date", DateTime, nullable=False),
    Column("status", String, nullable=False, default="cleared"),
    Column("needs_review", Boolean, nullable=False, default=False),
    Column("note", Text),
    Column("updated_at", DateTime),
)

recurring = Table("recurring", metadata,
    Column("recurring_id", Integer, primary_key=True, autoincrement=True),
    Column("account_id", Integer, ForeignKey("account.account_id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id")),
    Column("merchant", String),
    Column("amount", Numeric, nullable=False),
    Column("interval", Integer, nullable=False),
    Column("frequency_unit", String, nullable=False),
    Column("next_due", DateTime, nullable=False),
    Column("end_date", DateTime),
    Column("status", String, nullable=False, default="active"),
)

budget = Table("budget", metadata,
    Column("budget_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("period", String, nullable=False),
    Column("start_date", DateTime, nullable=False),
    Column("end_date", DateTime),
)

budget_item = Table("budget_item", metadata,
    Column("budget_item_id", Integer, primary_key=True, autoincrement=True),
    Column("budget_id", Integer, ForeignKey("budget.budget_id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("planned_amount", Numeric, nullable=False),
    Column("rollover_enabled", Boolean, nullable=False, default=False),
)

goal = Table("goal", metadata,
    Column("goal_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("account_id", Integer, ForeignKey("account.account_id")),
    Column("name", String, nullable=False),
    Column("target_amount", Numeric, nullable=False),
    Column("target_date", DateTime),
    Column("status", String, nullable=False, default="active"),
)

transaction_tag = Table("transaction_tag", metadata,
    Column("transaction_id", Integer, ForeignKey("transaction.transaction_id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.tag_id"), primary_key=True),
)
