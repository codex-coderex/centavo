import type { Budget, BudgetItem } from '$lib/api/budgets';
import type { Transaction } from '$lib/api/transactions';

export function spentForBudgetItem(item: BudgetItem, transactions: Transaction[]) {
	return transactions
		.filter((transaction: Transaction) => transaction.budget_item_id === item.budget_item_id)
		.reduce((total: number, transaction: Transaction) => total + Math.abs(transaction.amount_minor), 0);
}

export function plannedForBudget(items: BudgetItem[]) {
	return items.reduce((total: number, item: BudgetItem) => total + item.planned_amount_minor, 0);
}

export function spentForBudget(items: BudgetItem[], transactions: Transaction[]) {
	const itemIds = new Set(items.map((item: BudgetItem) => item.budget_item_id));

	return transactions
		.filter((transaction: Transaction) => transaction.budget_item_id != null && itemIds.has(transaction.budget_item_id))
		.reduce((total: number, transaction: Transaction) => total + Math.abs(transaction.amount_minor), 0);
}

export function budgetProgress(spentMinor: number, plannedMinor: number) {
	if (plannedMinor <= 0) return 0;
	return Math.min((spentMinor / plannedMinor) * 100, 100);
}

export function itemsForBudget(budget: Budget, items: BudgetItem[]) {
	return items.filter((item: BudgetItem) => item.budget_id === budget.budget_id);
}
