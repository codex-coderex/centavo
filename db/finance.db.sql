BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "account" (
	"account_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"type"	VARCHAR NOT NULL,
	"opening_balance_minor"	INTEGER NOT NULL DEFAULT 0,
	"created_at"	DATETIME NOT NULL,
	"status"	VARCHAR NOT NULL DEFAULT 'active',
	PRIMARY KEY("account_id"),
	CONSTRAINT "uq_account_user_name" UNIQUE("user_id","name"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id"),
	CONSTRAINT "ck_account_status" CHECK("status" IN ('active', 'archived')),
	CONSTRAINT "ck_account_type" CHECK("type" IN ('checking', 'savings', 'cash', 'credit_card', 'line_of_credit', 'loan', 'mortgage', 'investment', 'other_asset', 'other_liability'))
);
CREATE TABLE IF NOT EXISTS "budget" (
	"budget_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"period_type"	VARCHAR NOT NULL,
	"start_date"	DATETIME NOT NULL,
	"end_date"	DATETIME,
	"created_at"	DATETIME NOT NULL,
	PRIMARY KEY("budget_id"),
	CONSTRAINT "uq_budget_user_name_start_date" UNIQUE("user_id","name","start_date"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id"),
	CONSTRAINT "ck_budget_period_type" CHECK("period_type" IN ('weekly', 'monthly', 'quarterly', 'yearly', 'custom'))
);
CREATE TABLE IF NOT EXISTS "budget_item" (
	"budget_item_id"	INTEGER NOT NULL,
	"budget_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	"planned_amount_minor"	INTEGER NOT NULL,
	"rollover_enabled"	BOOLEAN NOT NULL DEFAULT 0,
	CONSTRAINT "uq_budget_item_budget_category" UNIQUE("budget_id","category_id"),
	PRIMARY KEY("budget_item_id"),
	FOREIGN KEY("budget_id") REFERENCES "budget"("budget_id") ON DELETE CASCADE,
	FOREIGN KEY("category_id") REFERENCES "category"("category_id"),
	CONSTRAINT "ck_budget_item_planned_amount_minor" CHECK("planned_amount_minor" >= 0)
);
CREATE TABLE IF NOT EXISTS "category" (
	"category_id"	INTEGER NOT NULL,
	"group_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"is_system"	BOOLEAN NOT NULL DEFAULT 0,
	"is_active"	BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY("category_id"),
	CONSTRAINT "uq_category_group_name" UNIQUE("group_id","name"),
	FOREIGN KEY("group_id") REFERENCES "category_group"("group_id")
);
CREATE TABLE IF NOT EXISTS "category_group" (
	"group_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"type"	VARCHAR NOT NULL,
	"is_system"	BOOLEAN NOT NULL DEFAULT 0,
	"is_active"	BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY("group_id"),
	CONSTRAINT "uq_category_group_user_type_name" UNIQUE("user_id","type","name"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id"),
	CONSTRAINT "ck_category_group_type" CHECK("type" IN ('income', 'expense', 'transfer'))
);
CREATE TABLE IF NOT EXISTS "goal" (
	"goal_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"target_amount_minor"	INTEGER NOT NULL,
	"target_date"	DATETIME,
	"status"	VARCHAR NOT NULL DEFAULT 'active',
	PRIMARY KEY("goal_id"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id"),
	CONSTRAINT "ck_goal_status" CHECK("status" IN ('active', 'completed')),
	CONSTRAINT "ck_goal_target_amount_minor" CHECK("target_amount_minor" > 0)
);
CREATE TABLE IF NOT EXISTS "goal_account" (
	"goal_id"	INTEGER NOT NULL,
	"account_id"	INTEGER NOT NULL,
	"allocated_amount_minor"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("goal_id","account_id"),
	FOREIGN KEY("account_id") REFERENCES "account"("account_id") ON DELETE CASCADE,
	FOREIGN KEY("goal_id") REFERENCES "goal"("goal_id") ON DELETE CASCADE,
	CONSTRAINT "ck_goal_account_allocated_amount_minor" CHECK("allocated_amount_minor" >= 0)
);
CREATE TABLE IF NOT EXISTS "recurring_rule" (
	"recurring_rule_id"	INTEGER NOT NULL,
	"account_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"expected_amount_minor"	INTEGER NOT NULL,
	"interval"	INTEGER NOT NULL,
	"frequency_unit"	VARCHAR NOT NULL,
	"start_date"	DATETIME NOT NULL,
	"next_due_date"	DATETIME NOT NULL,
	"end_date"	DATETIME,
	"status"	VARCHAR NOT NULL DEFAULT 'active',
	PRIMARY KEY("recurring_rule_id"),
	FOREIGN KEY("account_id") REFERENCES "account"("account_id"),
	FOREIGN KEY("category_id") REFERENCES "category"("category_id"),
	CONSTRAINT "ck_recurring_rule_frequency_unit" CHECK("frequency_unit" IN ('day', 'week', 'month', 'year')),
	CONSTRAINT "ck_recurring_rule_status" CHECK("status" IN ('active', 'paused', 'inactive')),
	CONSTRAINT "ck_recurring_rule_expected_amount_minor" CHECK("expected_amount_minor" <> 0),
	CONSTRAINT "ck_recurring_rule_interval" CHECK("interval" > 0)
);
CREATE TABLE IF NOT EXISTS "tag" (
	"tag_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	PRIMARY KEY("tag_id"),
	CONSTRAINT "uq_tag_user_name" UNIQUE("user_id","name"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id")
);
CREATE TABLE IF NOT EXISTS "transaction" (
	"transaction_id"	INTEGER NOT NULL,
	"account_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	"budget_item_id"	INTEGER,
	"recurring_rule_id"	INTEGER,
	"payee"	VARCHAR,
	"amount_minor"	INTEGER NOT NULL,
	"transaction_date"	DATETIME NOT NULL,
	"notes"	TEXT,
	"created_at"	DATETIME NOT NULL,
	"transfer_id"	INTEGER,
	PRIMARY KEY("transaction_id"),
	FOREIGN KEY("account_id") REFERENCES "account"("account_id"),
	FOREIGN KEY("budget_item_id") REFERENCES "budget_item"("budget_item_id") ON DELETE SET NULL,
	FOREIGN KEY("category_id") REFERENCES "category"("category_id"),
	FOREIGN KEY("recurring_rule_id") REFERENCES "recurring_rule"("recurring_rule_id") ON DELETE SET NULL,
	CONSTRAINT "ck_transaction_amount_minor" CHECK("amount_minor" <> 0)
);
CREATE TABLE IF NOT EXISTS "transaction_tag" (
	"transaction_id"	INTEGER NOT NULL,
	"tag_id"	INTEGER NOT NULL,
	PRIMARY KEY("transaction_id","tag_id"),
	FOREIGN KEY("tag_id") REFERENCES "tag"("tag_id") ON DELETE CASCADE,
	FOREIGN KEY("transaction_id") REFERENCES "transaction"("transaction_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user" (
	"user_id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	"created_at"	DATETIME NOT NULL,
	PRIMARY KEY("user_id")
);
CREATE INDEX IF NOT EXISTS "ix_account_status" ON "account" (
	"status"
);
CREATE INDEX IF NOT EXISTS "ix_account_user_id" ON "account" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "ix_budget_item_budget_id" ON "budget_item" (
	"budget_id"
);
CREATE INDEX IF NOT EXISTS "ix_budget_item_category_id" ON "budget_item" (
	"category_id"
);
CREATE INDEX IF NOT EXISTS "ix_budget_period_type" ON "budget" (
	"period_type"
);
CREATE INDEX IF NOT EXISTS "ix_budget_start_date" ON "budget" (
	"start_date"
);
CREATE INDEX IF NOT EXISTS "ix_budget_user_id" ON "budget" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "ix_category_group_id" ON "category" (
	"group_id"
);
CREATE INDEX IF NOT EXISTS "ix_category_group_is_active" ON "category_group" (
	"is_active"
);
CREATE INDEX IF NOT EXISTS "ix_category_group_type" ON "category_group" (
	"type"
);
CREATE INDEX IF NOT EXISTS "ix_category_group_user_id" ON "category_group" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "ix_category_is_active" ON "category" (
	"is_active"
);
CREATE INDEX IF NOT EXISTS "ix_goal_account_account_id" ON "goal_account" (
	"account_id"
);
CREATE INDEX IF NOT EXISTS "ix_goal_account_goal_id" ON "goal_account" (
	"goal_id"
);
CREATE INDEX IF NOT EXISTS "ix_goal_status" ON "goal" (
	"status"
);
CREATE INDEX IF NOT EXISTS "ix_goal_user_id" ON "goal" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "ix_recurring_rule_account_id" ON "recurring_rule" (
	"account_id"
);
CREATE INDEX IF NOT EXISTS "ix_recurring_rule_category_id" ON "recurring_rule" (
	"category_id"
);
CREATE INDEX IF NOT EXISTS "ix_recurring_rule_next_due_date" ON "recurring_rule" (
	"next_due_date"
);
CREATE INDEX IF NOT EXISTS "ix_recurring_rule_status" ON "recurring_rule" (
	"status"
);
CREATE INDEX IF NOT EXISTS "ix_tag_user_id" ON "tag" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_account_id" ON "transaction" (
	"account_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_budget_item_id" ON "transaction" (
	"budget_item_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_category_id" ON "transaction" (
	"category_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_recurring_rule_id" ON "transaction" (
	"recurring_rule_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_tag_tag_id" ON "transaction_tag" (
	"tag_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_tag_transaction_id" ON "transaction_tag" (
	"transaction_id"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_transaction_date" ON "transaction" (
	"transaction_date"
);
CREATE INDEX IF NOT EXISTS "ix_transaction_transfer_id" ON "transaction" (
	"transfer_id"
);
COMMIT;
