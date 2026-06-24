from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Text,
    ForeignKey, CheckConstraint, Index,
    UniqueConstraint, text,
)

metadata = MetaData()


user = Table("user", metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
)


account = Table("account", metadata,
    Column("account_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("type", String, nullable=False),
    Column("opening_balance_minor", Integer, nullable=False, server_default=text("0")),
    Column("created_at", DateTime, nullable=False),
    Column("status", String, nullable=False, server_default=text("'active'")),
    CheckConstraint("status IN ('active','archived')", name="ck_account_status"),
    CheckConstraint(
        "type IN ('checking','savings','cash','credit_card','line_of_credit','loan','mortgage','investment','other_asset','other_liability')",
        name="ck_account_type",
    ),
)


category_group = Table("category_group", metadata,
    Column("group_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("type", String, nullable=False),
    Column("is_system", Boolean, nullable=False, server_default=text("0")),
    Column("is_active", Boolean, nullable=False, server_default=text("1")),
    CheckConstraint("type IN ('income','expense','transfer')", name="ck_category_group_type"),
    UniqueConstraint("user_id", "type", "name", name="uq_category_group_user_type_name"),
)


category = Table("category", metadata,
    Column("category_id", Integer, primary_key=True, autoincrement=True),
    Column("group_id", Integer, ForeignKey("category_group.group_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("is_system", Boolean, nullable=False, server_default=text("0")),
    Column("is_active", Boolean, nullable=False, server_default=text("1")),
    UniqueConstraint("group_id", "name", name="uq_category_group_name"),
)


budget = Table("budget", metadata,
    Column("budget_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("period_type", String, nullable=False),
    Column("start_date", DateTime, nullable=False),
    Column("end_date", DateTime),
    Column("created_at", DateTime, nullable=False),
    CheckConstraint(
        "period_type IN ('weekly','monthly','quarterly','yearly','custom')",
        name="ck_budget_period_type",
    ),
    UniqueConstraint("user_id", "name", "start_date", name="uq_budget_user_name_start_date"),
)


budget_item = Table("budget_item", metadata,
    Column("budget_item_id", Integer, primary_key=True, autoincrement=True),
    Column("budget_id", Integer, ForeignKey("budget.budget_id", ondelete="CASCADE"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("planned_amount_minor", Integer, nullable=False),
    Column("rollover_enabled", Boolean, nullable=False, server_default=text("0")),
    CheckConstraint("planned_amount_minor >= 0", name="ck_budget_item_planned_amount_minor"),
    UniqueConstraint("budget_id", "category_id", name="uq_budget_item_budget_category"),
)


recurring_rule = Table("recurring_rule", metadata,
    Column("recurring_rule_id", Integer, primary_key=True, autoincrement=True),
    Column("account_id", Integer, ForeignKey("account.account_id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("expected_amount_minor", Integer, nullable=False),
    Column("interval", Integer, nullable=False),
    Column("frequency_unit", String, nullable=False),
    Column("start_date", DateTime, nullable=False),
    Column("next_due_date", DateTime, nullable=False),
    Column("end_date", DateTime),
    Column("status", String, nullable=False, server_default=text("'active'")),
    CheckConstraint("expected_amount_minor <> 0", name="ck_recurring_rule_expected_amount_minor"),
    CheckConstraint("interval > 0", name="ck_recurring_rule_interval"),
    CheckConstraint(
        "frequency_unit IN ('day','week','month','year')",
        name="ck_recurring_rule_frequency_unit",
    ),
    CheckConstraint(
        "status IN ('active','paused','inactive')",
        name="ck_recurring_rule_status",
    ),
)


goal = Table("goal", metadata,
    Column("goal_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    Column("target_amount_minor", Integer, nullable=False),
    Column("target_date", DateTime),
    Column("status", String, nullable=False, server_default=text("'active'")),
    CheckConstraint("target_amount_minor > 0", name="ck_goal_target_amount_minor"),
    CheckConstraint("status IN ('active','completed')", name="ck_goal_status"),
)


goal_account = Table("goal_account", metadata,
    Column(
        "goal_id",
        Integer,
        ForeignKey("goal.goal_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "account_id",
        Integer,
        ForeignKey("account.account_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("allocated_amount_minor", Integer, nullable=False, server_default=text("0")),
    CheckConstraint(
        "allocated_amount_minor >= 0",
        name="ck_goal_account_allocated_amount_minor",
    ),
)


tag = Table("tag", metadata,
    Column("tag_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("name", String, nullable=False),
    UniqueConstraint("user_id", "name", name="uq_tag_user_name"),
)


transaction = Table("transaction", metadata,
    Column("transaction_id", Integer, primary_key=True, autoincrement=True),
    Column("account_id", Integer, ForeignKey("account.account_id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.category_id"), nullable=False),
    Column("budget_item_id", Integer, ForeignKey("budget_item.budget_item_id", ondelete="SET NULL"), nullable=True),
    Column("recurring_rule_id", Integer, ForeignKey("recurring_rule.recurring_rule_id", ondelete="SET NULL"), nullable=True),
    Column("payee", String),
    Column("amount_minor", Integer, nullable=False),
    Column("transaction_date", DateTime, nullable=False),
    Column("notes", Text),
    Column("created_at", DateTime, nullable=False),
    Column("transfer_id", Integer),
    CheckConstraint("amount_minor <> 0", name="ck_transaction_amount_minor"),
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
Index("ix_account_status", account.c.status)
Index(
    "uq_account_active_user_name",
    account.c.user_id,
    account.c.name,
    unique=True,
    sqlite_where=account.c.status == "active",
)

Index("ix_category_group_user_id", category_group.c.user_id)
Index("ix_category_group_type", category_group.c.type)
Index("ix_category_group_is_active", category_group.c.is_active)

Index("ix_category_group_id", category.c.group_id)
Index("ix_category_is_active", category.c.is_active)

Index("ix_budget_user_id", budget.c.user_id)
Index("ix_budget_start_date", budget.c.start_date)
Index("ix_budget_period_type", budget.c.period_type)

Index("ix_budget_item_budget_id", budget_item.c.budget_id)
Index("ix_budget_item_category_id", budget_item.c.category_id)

Index("ix_recurring_rule_account_id", recurring_rule.c.account_id)
Index("ix_recurring_rule_category_id", recurring_rule.c.category_id)
Index("ix_recurring_rule_next_due_date", recurring_rule.c.next_due_date)
Index("ix_recurring_rule_status", recurring_rule.c.status)

Index("ix_goal_user_id", goal.c.user_id)
Index("ix_goal_status", goal.c.status)

Index("ix_goal_account_goal_id", goal_account.c.goal_id)
Index("ix_goal_account_account_id", goal_account.c.account_id)

Index("ix_tag_user_id", tag.c.user_id)

Index("ix_transaction_account_id", transaction.c.account_id)
Index("ix_transaction_category_id", transaction.c.category_id)
Index("ix_transaction_budget_item_id", transaction.c.budget_item_id)
Index("ix_transaction_recurring_rule_id", transaction.c.recurring_rule_id)
Index("ix_transaction_transfer_id", transaction.c.transfer_id)
Index("ix_transaction_transaction_date", transaction.c.transaction_date)

Index("ix_transaction_tag_transaction_id", transaction_tag.c.transaction_id)
Index("ix_transaction_tag_tag_id", transaction_tag.c.tag_id)
