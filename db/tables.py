from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Text,
    ForeignKey, CheckConstraint, Index
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
    CheckConstraint("decimal_places >= 0", name="ck_currency_decimal_places"),
)

account = Table("account", metadata,
    Column("account_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("currency_code", String, ForeignKey("currency.code"), nullable=False),
    Column("name", String, nullable=False),
    Column("type", String, nullable=False),
    Column("status", String, nullable=False, default="active"),
    CheckConstraint("status IN ('active','archived')", name="ck_account_status"),
)

category_group = Table("category_group", metadata,
    Column("group_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("type", String, nullable=False),
    CheckConstraint("type IN ('income','expense')", name="ck_category_group_type"),
)

category = Table("category", metadata,
    Column("category_id", Integer, primary_key=True, autoincrement=True),
    Column("group_id", Integer, ForeignKey("category_group.group_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("color", String),
    Column("is_system", Boolean, nullable=False, default=False),
    Column("is_active", Boolean, nullable=False, default=True),
)

recurring = Table("recurring", metadata,
    Column("recurring_id", Integer, primary_key=True, autoincrement=True),
    Column("account_id", Integer, ForeignKey("account.account_id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("merchant", String),
    Column("amount_minor", Integer, nullable=False),
    Column("interval", Integer, nullable=False),
    Column("frequency_unit", String, nullable=False),
    Column("next_due", DateTime, nullable=False),
    Column("end_date", DateTime),
    Column("status", String, nullable=False, default="active"),
    CheckConstraint("amount_minor <> 0", name="ck_recurring_amount_minor"),
    CheckConstraint("interval > 0", name="ck_recurring_interval"),
    CheckConstraint(
        "frequency_unit IN ('day','week','month','year')",
        name="ck_recurring_frequency_unit",
    ),
    CheckConstraint(
        "status IN ('active','paused','inactive')",
        name="ck_recurring_status",
    ),
)

budget = Table("budget", metadata,
    Column("budget_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("period", String, nullable=False),
    Column("start_date", DateTime, nullable=False),
    Column("end_date", DateTime),
    CheckConstraint(
        "period IN ('weekly','monthly','quarterly','yearly','custom')",
        name="ck_budget_period",
    ),
)

budget_item = Table("budget_item", metadata,
    Column("budget_item_id", Integer, primary_key=True, autoincrement=True),
    Column("budget_id", Integer, ForeignKey("budget.budget_id", ondelete="CASCADE"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("planned_amount_minor", Integer, nullable=False),
    Column("rollover_enabled", Boolean, nullable=False, default=False),
    CheckConstraint("planned_amount_minor >= 0", name="ck_budget_item_planned_amount_minor"),
)

goal = Table("goal", metadata,
    Column("goal_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("account_id", Integer, ForeignKey("account.account_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("target_amount_minor", Integer, nullable=False),
    Column("target_date", DateTime),
    Column("status", String, nullable=False, default="active"),
    CheckConstraint("target_amount_minor > 0", name="ck_goal_target_amount_minor"),
    CheckConstraint("status IN ('active','completed')", name="ck_goal_status"),
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
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("recurring_id", Integer, ForeignKey("recurring.recurring_id")),
    Column("transfer_pair_id", Integer, ForeignKey("transaction.transaction_id")),
    Column("goal_id", Integer, ForeignKey("goal.goal_id")),
    Column("merchant", String),
    Column("amount_minor", Integer, nullable=False),
    Column("txn_date", DateTime, nullable=False),
    Column("status", String, nullable=False, default="cleared"),
    Column("needs_review", Boolean, nullable=False, default=False),
    Column("note", Text),
    Column("updated_at", DateTime),
    CheckConstraint("amount_minor <> 0", name="ck_transaction_amount_minor"),
    CheckConstraint(
        "status IN ('pending','cleared','void')",
        name="ck_transaction_status",
    ),
)

transaction_tag = Table("transaction_tag", metadata,
    Column(
        "transaction_id",
        Integer,
        ForeignKey("transaction.transaction_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tag.tag_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

Index("ix_account_user_id", account.c.user_id)
Index("ix_account_currency_code", account.c.currency_code)

Index("ix_category_group_user_id", category_group.c.user_id)

Index("ix_category_group_id", category.c.group_id)
Index("ix_category_is_active", category.c.is_active)

Index("ix_recurring_account_id", recurring.c.account_id)
Index("ix_recurring_category_id", recurring.c.category_id)
Index("ix_recurring_next_due", recurring.c.next_due)
Index("ix_recurring_status", recurring.c.status)

Index("ix_budget_user_id", budget.c.user_id)
Index("ix_budget_start_date", budget.c.start_date)

Index("ix_budget_item_budget_id", budget_item.c.budget_id)
Index("ix_budget_item_category_id", budget_item.c.category_id)

Index("ix_goal_user_id", goal.c.user_id)
Index("ix_goal_account_id", goal.c.account_id)

Index("ix_tag_user_id", tag.c.user_id)

Index("ix_transaction_account_id", transaction.c.account_id)
Index("ix_transaction_category_id", transaction.c.category_id)
Index("ix_transaction_recurring_id", transaction.c.recurring_id)
Index("ix_transaction_goal_id", transaction.c.goal_id)
Index("ix_transaction_txn_date", transaction.c.txn_date)
Index("ix_transaction_status", transaction.c.status)

Index("ix_transaction_tag_transaction_id", transaction_tag.c.transaction_id)
Index("ix_transaction_tag_tag_id", transaction_tag.c.tag_id)