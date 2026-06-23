import api.users as users
import api.accounts as accounts
import api.budgets as budgets
import api.categories as categories
import api.goals as goals
import api.recurring as recurring
import api.tags as tags
import api.transactions as transactions


class FinanceApi:

    # Users
    def get_users(self):
        return users.get_users()

    def get_user(self, user_id):
        return users.get_user(user_id)

    def create_user(self, name):
        return users.create_user(name)

    def update_user(self, user_id, name=None):
        return users.update_user(user_id, name=name)


    # Accounts
    def get_accounts(self, user_id, active_only=True):
        return accounts.get_accounts(user_id, active_only=active_only)

    def get_account(self, account_id):
        return accounts.get_account(account_id)

    def create_account(self, user_id, name, type, opening_balance=0):
        return accounts.create_account(user_id, name, type, opening_balance=opening_balance)

    def update_account(self, account_id, name=None, type=None, opening_balance=None, status=None):
        return accounts.update_account(
            account_id,
            name=name,
            type=type,
            opening_balance=opening_balance,
            status=status,
        )

    def archive_account(self, account_id):
        return accounts.archive_account(account_id)


    # Budgets
    def get_budgets(self, user_id):
        return budgets.get_budgets(user_id)

    def get_budget(self, budget_id):
        return budgets.get_budget(budget_id)

    def create_budget(self, user_id, name, period_type, start_date, end_date=None):
        return budgets.create_budget(user_id, name, period_type, start_date, end_date=end_date)

    def update_budget(self, budget_id, name=None, period_type=None, start_date=None, end_date=None):
        return budgets.update_budget(
            budget_id,
            name=name,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
        )

    def delete_budget(self, budget_id):
        return budgets.delete_budget(budget_id)

    def get_budget_items(self, budget_id):
        return budgets.get_budget_items(budget_id)

    def create_budget_item(self, budget_id, category_id, planned_amount, rollover_enabled=False):
        return budgets.create_budget_item(
            budget_id,
            category_id,
            planned_amount,
            rollover_enabled=rollover_enabled,
        )

    def update_budget_item(self, budget_item_id, planned_amount=None, category_id=None, rollover_enabled=None):
        return budgets.update_budget_item(
            budget_item_id,
            planned_amount=planned_amount,
            category_id=category_id,
            rollover_enabled=rollover_enabled,
        )

    def delete_budget_item(self, budget_item_id):
        return budgets.delete_budget_item(budget_item_id)


    # Categories
    def get_category_groups(self, user_id):
        return categories.get_category_groups(user_id)

    def get_categories(self, group_id):
        return categories.get_categories(group_id)

    def get_all_categories(self, user_id):
        return categories.get_all_categories(user_id)

    def create_category_group(self, user_id, name, type):
        return categories.create_category_group(user_id, name, type)

    def create_category(self, group_id, name):
        return categories.create_category(group_id, name)

    def update_category_group(self, group_id, name=None, type=None, is_active=None):
        return categories.update_category_group(
            group_id,
            name=name,
            type=type,
            is_active=is_active,
        )

    def update_category(self, category_id, name=None, is_active=None):
        return categories.update_category(category_id, name=name, is_active=is_active)

    def deactivate_category(self, category_id):
        return categories.deactivate_category(category_id)

    def deactivate_category_group(self, group_id):
        return categories.deactivate_category_group(group_id)

    def remove_category(self, category_id):
        return categories.remove_category(category_id)

    def remove_category_group(self, group_id):
        return categories.remove_category_group(group_id)


    # Transactions
    def get_transactions_by_user(self, user_id):
        return transactions.get_transactions_by_user(user_id)

    def get_transactions_by_account(self, account_id):
        return transactions.get_transactions_by_account(account_id)

    def get_transaction(self, transaction_id):
        return transactions.get_transaction(transaction_id)

    def create_transaction(
        self,
        account_id,
        amount,
        transaction_date,
        category_id,
        budget_item_id=None,
        payee=None,
        notes=None,
        recurring_rule_id=None,
    ):
        return transactions.create_transaction(
            account_id=account_id,
            amount=amount,
            transaction_date=transaction_date,
            category_id=category_id,
            budget_item_id=budget_item_id,
            payee=payee,
            notes=notes,
            recurring_rule_id=recurring_rule_id,
        )

    def create_transfer(
        self,
        from_account_id,
        to_account_id,
        amount,
        transaction_date,
        category_id,
        payee="Transfer",
        notes=None,
    ):
        return transactions.create_transfer(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            transaction_date=transaction_date,
            category_id=category_id,
            payee=payee,
            notes=notes,
        )

    def update_transaction(
        self,
        transaction_id,
        account_id=None,
        amount=None,
        transaction_date=None,
        category_id=None,
        budget_item_id=None,
        payee=None,
        notes=None,
        recurring_rule_id=None,
    ):
        return transactions.update_transaction(
            transaction_id,
            account_id=account_id,
            amount=amount,
            transaction_date=transaction_date,
            category_id=category_id,
            budget_item_id=budget_item_id,
            payee=payee,
            notes=notes,
            recurring_rule_id=recurring_rule_id,
        )

    def delete_transaction(self, transaction_id):
        return transactions.delete_transaction(transaction_id)

    def update_transfer(self, transfer_id, amount=None, transaction_date=None, payee=None, notes=None):
        return transactions.update_transfer(
            transfer_id,
            amount=amount,
            transaction_date=transaction_date,
            payee=payee,
            notes=notes,
        )

    def delete_transfer(self, transfer_id):
        return transactions.delete_transfer(transfer_id)


    # Tags
    def get_tags(self, user_id):
        return tags.get_tags(user_id)

    def get_tag(self, tag_id):
        return tags.get_tag(tag_id)

    def create_tag(self, user_id, name):
        return tags.create_tag(user_id, name)

    def update_tag(self, tag_id, name=None):
        return tags.update_tag(tag_id, name=name)

    def delete_tag(self, tag_id):
        return tags.delete_tag(tag_id)

    def get_transaction_tags(self, transaction_id):
        return tags.get_transaction_tags(transaction_id)

    def add_tag_to_transaction(self, transaction_id, tag_id):
        return tags.add_tag_to_transaction(transaction_id, tag_id)

    def remove_tag_from_transaction(self, transaction_id, tag_id):
        return tags.remove_tag_from_transaction(transaction_id, tag_id)


    # Goals
    def get_goals(self, user_id):
        return goals.get_goals(user_id)

    def get_goal(self, goal_id):
        return goals.get_goal(goal_id)

    def create_goal(self, user_id, name, target_amount, target_date=None):
        return goals.create_goal(user_id, name, target_amount, target_date=target_date)

    def update_goal(self, goal_id, name=None, target_amount=None, target_date=None, status=None):
        return goals.update_goal(
            goal_id,
            name=name,
            target_amount=target_amount,
            target_date=target_date,
            status=status,
        )

    def complete_goal(self, goal_id):
        return goals.complete_goal(goal_id)

    def get_goal_accounts(self, goal_id):
        return goals.get_goal_accounts(goal_id)

    def add_account_to_goal(self, goal_id, account_id, allocated_amount=0):
        return goals.add_account_to_goal(goal_id, account_id, allocated_amount=allocated_amount)

    def update_goal_account_allocation(self, goal_id, account_id, allocated_amount):
        return goals.update_goal_account_allocation(goal_id, account_id, allocated_amount)

    def remove_account_from_goal(self, goal_id, account_id):
        return goals.remove_account_from_goal(goal_id, account_id)


    # Recurring
    def get_recurring_rules(self, user_id):
        return recurring.get_recurring_rules(user_id)

    def get_recurring_rule(self, recurring_rule_id):
        return recurring.get_recurring_rule(recurring_rule_id)

    def get_due_recurring_rules(self, as_of=None):
        return recurring.get_due_recurring_rules(as_of=as_of)

    def create_recurring_rule(
        self,
        account_id,
        category_id,
        name,
        expected_amount,
        interval,
        frequency_unit,
        start_date,
        next_due_date,
        end_date=None,
    ):
        return recurring.create_recurring_rule(
            account_id,
            category_id,
            name,
            expected_amount,
            interval,
            frequency_unit,
            start_date,
            next_due_date,
            end_date=end_date,
        )

    def update_recurring_rule(
        self,
        recurring_rule_id,
        account_id=None,
        category_id=None,
        name=None,
        expected_amount=None,
        interval=None,
        frequency_unit=None,
        start_date=None,
        next_due_date=None,
        end_date=None,
        status=None,
    ):
        return recurring.update_recurring_rule(
            recurring_rule_id,
            account_id=account_id,
            category_id=category_id,
            name=name,
            expected_amount=expected_amount,
            interval=interval,
            frequency_unit=frequency_unit,
            start_date=start_date,
            next_due_date=next_due_date,
            end_date=end_date,
            status=status,
        )

    def pause_recurring_rule(self, recurring_rule_id):
        return recurring.pause_recurring_rule(recurring_rule_id)

    def resume_recurring_rule(self, recurring_rule_id):
        return recurring.resume_recurring_rule(recurring_rule_id)

    def deactivate_recurring_rule(self, recurring_rule_id):
        return recurring.deactivate_recurring_rule(recurring_rule_id)

    def generate_transaction(self, recurring_rule_id):
        return recurring.generate_transaction(recurring_rule_id)
