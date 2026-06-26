SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS account (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        opening_balance_minor INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        CONSTRAINT ck_account_status CHECK (status IN ('active','archived')),
        CONSTRAINT ck_account_type CHECK (
            type IN (
                'checking','savings','cash','credit_card','line_of_credit','loan',
                'mortgage','investment','other_asset','other_liability'
            )
        )
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS category_group (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        is_system INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        CONSTRAINT ck_category_group_type CHECK (type IN ('income','expense','transfer')),
        CONSTRAINT uq_category_group_user_type_name UNIQUE (user_id, type, name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        is_system INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (group_id) REFERENCES category_group(group_id),
        CONSTRAINT uq_category_group_name UNIQUE (group_id, name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS budget (
        budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        period_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        CONSTRAINT ck_budget_period_type CHECK (
            period_type IN ('weekly','monthly','quarterly','yearly','custom')
        ),
        CONSTRAINT uq_budget_user_name_start_date UNIQUE (user_id, name, start_date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS budget_item (
        budget_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        budget_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        planned_amount_minor INTEGER NOT NULL,
        rollover_enabled INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (budget_id) REFERENCES budget(budget_id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES category(category_id),
        CONSTRAINT ck_budget_item_planned_amount_minor CHECK (planned_amount_minor >= 0),
        CONSTRAINT uq_budget_item_budget_category UNIQUE (budget_id, category_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS recurring_rule (
        recurring_rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        expected_amount_minor INTEGER NOT NULL,
        interval INTEGER NOT NULL,
        frequency_unit TEXT NOT NULL,
        start_date TEXT NOT NULL,
        next_due_date TEXT NOT NULL,
        end_date TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        FOREIGN KEY (account_id) REFERENCES account(account_id),
        FOREIGN KEY (category_id) REFERENCES category(category_id),
        CONSTRAINT ck_recurring_rule_expected_amount_minor CHECK (expected_amount_minor <> 0),
        CONSTRAINT ck_recurring_rule_interval CHECK (interval > 0),
        CONSTRAINT ck_recurring_rule_frequency_unit CHECK (frequency_unit IN ('day','week','month','year')),
        CONSTRAINT ck_recurring_rule_status CHECK (status IN ('active','paused','inactive'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS goal (
        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        target_amount_minor INTEGER NOT NULL,
        target_date TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        CONSTRAINT ck_goal_target_amount_minor CHECK (target_amount_minor > 0),
        CONSTRAINT ck_goal_status CHECK (status IN ('active','completed'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS goal_account (
        goal_id INTEGER NOT NULL,
        account_id INTEGER NOT NULL,
        allocated_amount_minor INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (goal_id, account_id),
        FOREIGN KEY (goal_id) REFERENCES goal(goal_id) ON DELETE CASCADE,
        FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE,
        CONSTRAINT ck_goal_account_allocated_amount_minor CHECK (allocated_amount_minor >= 0)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tag (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        CONSTRAINT uq_tag_user_name UNIQUE (user_id, name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS "transaction" (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        budget_item_id INTEGER,
        recurring_rule_id INTEGER,
        payee TEXT,
        amount_minor INTEGER NOT NULL,
        transaction_date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL,
        transfer_id INTEGER,
        FOREIGN KEY (account_id) REFERENCES account(account_id),
        FOREIGN KEY (category_id) REFERENCES category(category_id),
        FOREIGN KEY (budget_item_id) REFERENCES budget_item(budget_item_id) ON DELETE SET NULL,
        FOREIGN KEY (recurring_rule_id) REFERENCES recurring_rule(recurring_rule_id) ON DELETE SET NULL,
        CONSTRAINT ck_transaction_amount_minor CHECK (amount_minor <> 0)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transaction_tag (
        transaction_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (transaction_id, tag_id),
        FOREIGN KEY (transaction_id) REFERENCES "transaction"(transaction_id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE
    )
    """,
]

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS ix_account_user_id ON account(user_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_account_active_user_name ON account(user_id, name) WHERE status = 'active'",
    "CREATE INDEX IF NOT EXISTS ix_category_group_user_id ON category_group(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_category_group_id ON category(group_id)",
    "CREATE INDEX IF NOT EXISTS ix_budget_user_id ON budget(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_budget_user_start_date ON budget(user_id, start_date)",
    "CREATE INDEX IF NOT EXISTS ix_budget_item_budget_id ON budget_item(budget_id)",
    "CREATE INDEX IF NOT EXISTS ix_budget_item_category_id ON budget_item(category_id)",
    "CREATE INDEX IF NOT EXISTS ix_recurring_rule_account_id ON recurring_rule(account_id)",
    "CREATE INDEX IF NOT EXISTS ix_recurring_rule_category_id ON recurring_rule(category_id)",
    "CREATE INDEX IF NOT EXISTS ix_recurring_rule_status_next_due_date ON recurring_rule(status, next_due_date)",
    "CREATE INDEX IF NOT EXISTS ix_goal_user_id ON goal(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_goal_account_account_id ON goal_account(account_id)",
    "CREATE INDEX IF NOT EXISTS ix_tag_user_id ON tag(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_transaction_account_date ON \"transaction\"(account_id, transaction_date)",
    "CREATE INDEX IF NOT EXISTS ix_transaction_category_id ON \"transaction\"(category_id)",
    "CREATE INDEX IF NOT EXISTS ix_transaction_budget_item_id ON \"transaction\"(budget_item_id)",
    "CREATE INDEX IF NOT EXISTS ix_transaction_recurring_rule_id ON \"transaction\"(recurring_rule_id)",
    "CREATE INDEX IF NOT EXISTS ix_transaction_transfer_id ON \"transaction\"(transfer_id)",
    "CREATE INDEX IF NOT EXISTS ix_transaction_tag_tag_id ON transaction_tag(tag_id)",
]


def initialize_schema(conn):
    for statement in SCHEMA_STATEMENTS:
        conn.execute(statement)

    for statement in INDEX_STATEMENTS:
        conn.execute(statement)
