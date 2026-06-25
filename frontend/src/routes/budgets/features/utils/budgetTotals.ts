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

export function rolloverCarryForBudgetItem(
	item: BudgetItem,
	budget: Budget,
	budgets: Budget[],
	items: BudgetItem[],
	transactions: Transaction[]
) {
	const previousBudget = [...budgets]
		.filter((row: Budget) =>
			row.budget_id !== budget.budget_id &&
			row.end_date != null &&
			row.end_date < budget.start_date
		)
		.sort((a: Budget, b: Budget) => (b.end_date ?? '').localeCompare(a.end_date ?? ''))
		.find((row: Budget) =>
			items.some((candidate: BudgetItem) =>
				candidate.budget_id === row.budget_id &&
				candidate.category_id === item.category_id &&
				candidate.rollover_enabled
			)
		);

	if (!previousBudget) return 0;

	const previousItem = items.find((candidate: BudgetItem) =>
		candidate.budget_id === previousBudget.budget_id &&
		candidate.category_id === item.category_id &&
		candidate.rollover_enabled
	);

	if (!previousItem) return 0;

	return previousItem.planned_amount_minor - spentForBudgetItem(previousItem, transactions);
}

export function plannedForBudgetItemWithRollover(
	item: BudgetItem,
	budget: Budget,
	budgets: Budget[],
	items: BudgetItem[],
	transactions: Transaction[]
) {
	return Math.max(
		0,
		item.planned_amount_minor + rolloverCarryForBudgetItem(item, budget, budgets, items, transactions)
	);
}

export function plannedForBudgetWithRollover(
	budget: Budget,
	budgets: Budget[],
	items: BudgetItem[],
	transactions: Transaction[]
) {
	return itemsForBudget(budget, items).reduce(
		(total: number, item: BudgetItem) =>
			total + plannedForBudgetItemWithRollover(item, budget, budgets, items, transactions),
		0
	);
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
