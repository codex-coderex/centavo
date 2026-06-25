import type { Account } from '$lib/api/accounts';
import type { Budget, BudgetItem } from '$lib/api/budgets';
import type { Category, CategoryGroup } from '$lib/api/categories';
import type { Goal, GoalAccount } from '$lib/api/goals';
import type { RecurringRule } from '$lib/api/recurring';
import type { Transaction } from '$lib/api/transactions';
import { plannedForBudgetItemWithRollover } from '../../../budgets/features/utils/budgetTotals';

export type DashboardPeriod = 'month' | 'year';

export type BudgetSummary = Budget & {
	items: BudgetItemSummary[];
	planned_minor: number;
	spent_minor: number;
};

export type BudgetItemSummary = BudgetItem & {
	category_name: string;
	group_name: string;
	group_type: string;
	spent_minor: number;
};

export function formatMoney(amountMinor: number) {
	return new Intl.NumberFormat('en-PH', {
		style: 'currency',
		currency: 'PHP'
	}).format(amountMinor / 100);
}

export function formatSignedMoney(amountMinor: number) {
	const prefix = amountMinor >= 0 ? '+' : '-';
	return `${prefix}${formatMoney(Math.abs(amountMinor))}`;
}

export function formatDate(value: string | null | undefined) {
	if (!value) return 'Ongoing';

	return new Date(value).toLocaleDateString('en-PH', {
		month: 'short',
		day: 'numeric',
		year: 'numeric'
	});
}

export function periodRange(period: DashboardPeriod, anchor = new Date()) {
	const year = anchor.getFullYear();
	const month = anchor.getMonth();
	const start = period === 'month' ? new Date(year, month, 1) : new Date(year, 0, 1);
	const end = period === 'month' ? new Date(year, month + 1, 0) : new Date(year, 11, 31);

	return {
		start: dateKey(start),
		end: dateKey(end),
		label: period === 'month'
			? anchor.toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })
			: String(year)
	};
}

export function dateKey(date: Date) {
	return date.toISOString().slice(0, 10);
}

export function inDateRange(value: string, start: string, end: string) {
	const key = value.slice(0, 10);
	return key >= start && key <= end;
}

export function categoryMaps(categories: Category[], groups: CategoryGroup[]) {
	const categoryById = new Map(categories.map((category: Category) => [category.category_id, category]));
	const groupById = new Map(groups.map((group: CategoryGroup) => [group.group_id, group]));

	return { categoryById, groupById };
}

export function accountName(accounts: Account[], accountId: number) {
	return accounts.find((account: Account) => account.account_id === accountId)?.name ?? `Account ${accountId}`;
}

export function categoryName(categories: Category[], categoryId: number) {
	return categories.find((category: Category) => category.category_id === categoryId)?.name ?? 'Uncategorized';
}

export function categoryGroupName(categories: Category[], groups: CategoryGroup[], categoryId: number) {
	const category = categories.find((row: Category) => row.category_id === categoryId);
	return groups.find((group: CategoryGroup) => group.group_id === category?.group_id)?.name ?? 'Other';
}

export function availableBalance(accounts: Account[]) {
	return accounts.reduce(
		(total: number, account: Account) =>
			total +
			(account.current_balance_minor ?? account.opening_balance_minor) -
			(account.allocated_to_goals_minor ?? 0),
		0
	);
}

export function spendingForPeriod(transactions: Transaction[], period: DashboardPeriod) {
	const range = periodRange(period);
	return transactions
		.filter((transaction: Transaction) =>
			transaction.transfer_id == null &&
			transaction.amount_minor < 0 &&
			inDateRange(transaction.transaction_date, range.start, range.end)
		)
		.reduce((total: number, transaction: Transaction) => total + Math.abs(transaction.amount_minor), 0);
}

export function spendingSeries(transactions: Transaction[], period: DashboardPeriod) {
	const range = periodRange(period);
	const points = period === 'month'
		? daysBetween(range.start, range.end).map((key: string) => ({
				key,
				label: String(new Date(`${key}T00:00:00`).getDate()),
				value: 0
			}))
		: Array.from({ length: 12 }, (_, index) => ({
				key: `${new Date().getFullYear()}-${String(index + 1).padStart(2, '0')}`,
				label: new Date(new Date().getFullYear(), index, 1).toLocaleDateString('en-PH', { month: 'short' }),
				value: 0
			}));

	for (const transaction of transactions) {
		if (
			transaction.transfer_id != null ||
			transaction.amount_minor >= 0 ||
			!inDateRange(transaction.transaction_date, range.start, range.end)
		) {
			continue;
		}

		const key = period === 'month'
			? transaction.transaction_date.slice(0, 10)
			: transaction.transaction_date.slice(0, 7);
		const point = points.find((row) => row.key === key);

		if (point) point.value += Math.abs(transaction.amount_minor);
	}

	return points;
}

export function goalAllocation(goal: Goal, allocations: GoalAccount[]) {
	return allocations
		.filter((allocation: GoalAccount) => allocation.goal_id === goal.goal_id)
		.reduce((total: number, allocation: GoalAccount) => total + allocation.allocated_amount_minor, 0);
}

export function budgetSummaries(
	budgets: Budget[],
	budgetItems: BudgetItem[],
	transactions: Transaction[],
	categories: Category[],
	groups: CategoryGroup[]
): BudgetSummary[] {
	const { categoryById, groupById } = categoryMaps(categories, groups);

	return budgets.map((budget: Budget) => {
		const items = budgetItems
			.filter((item: BudgetItem) => item.budget_id === budget.budget_id)
			.map((item: BudgetItem) => {
				const category = categoryById.get(item.category_id);
				const group = category ? groupById.get(category.group_id) : null;
				const spent = transactions
					.filter((transaction: Transaction) =>
						transaction.transfer_id == null &&
						transaction.category_id === item.category_id &&
						transaction.amount_minor < 0 &&
						inDateRange(
							transaction.transaction_date,
							budget.start_date,
							budget.end_date ?? '9999-12-31'
						)
					)
					.reduce((total: number, transaction: Transaction) => total + Math.abs(transaction.amount_minor), 0);

				return {
					...item,
					planned_amount_minor: plannedForBudgetItemWithRollover(
						item,
						budget,
						budgets,
						budgetItems,
						transactions
					),
					category_name: category?.name ?? 'Unknown category',
					group_name: group?.name ?? 'Other',
					group_type: group?.type ?? 'expense',
					spent_minor: spent
				};
			});

		return {
			...budget,
			items,
			planned_minor: items.reduce((total: number, item: BudgetItemSummary) => total + item.planned_amount_minor, 0),
			spent_minor: items.reduce((total: number, item: BudgetItemSummary) => total + item.spent_minor, 0)
		};
	});
}

export function upcomingRecurring(recurringRules: RecurringRule[]) {
	return [...recurringRules]
		.filter((rule: RecurringRule) => rule.status !== 'inactive')
		.sort((a: RecurringRule, b: RecurringRule) => a.next_due_date.localeCompare(b.next_due_date))
		.slice(0, 4);
}

function daysBetween(start: string, end: string) {
	const days: string[] = [];
	const current = new Date(`${start}T00:00:00`);
	const last = new Date(`${end}T00:00:00`);

	while (current <= last) {
		days.push(dateKey(current));
		current.setDate(current.getDate() + 1);
	}

	return days;
}
