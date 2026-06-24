import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';
import type { Transaction } from '$lib/api/transactions';
import { amountInputToMinor } from './transactionFormat';

export type TransactionFilters = {
	search: string;
	dateFrom: string;
	dateTo: string;
	accountIds: number[];
	types: CategoryGroupType[];
	categoryGroupIds: number[];
	categoryIds: number[];
	amountMin: string;
	amountMax: string;
};

export function categoryGroupForCategory(
	categoryId: number,
	categories: Category[],
	categoryGroups: CategoryGroup[]
) {
	const category = categories.find((row) => row.category_id === categoryId);
	return categoryGroups.find((row) => row.group_id === category?.group_id);
}

export function filterTransactions(
	transactions: Transaction[],
	filters: TransactionFilters,
	categories: Category[],
	categoryGroups: CategoryGroup[],
	accountName: (accountId: number) => string,
	categoryName: (categoryId: number) => string
) {
	const search = filters.search.trim().toLowerCase();
	const minAmount = amountInputToMinor(filters.amountMin);
	const maxAmount = amountInputToMinor(filters.amountMax);

	return transactions.filter((transaction) => {
		const group = categoryGroupForCategory(transaction.category_id, categories, categoryGroups);
		const transactionDate = transaction.transaction_date.slice(0, 10);
		const transactionAmount = Math.abs(transaction.amount_minor);

		if (filters.accountIds.length > 0 && !filters.accountIds.includes(transaction.account_id)) {
			return false;
		}

		if (filters.types.length > 0 && (!group || !filters.types.includes(group.type))) {
			return false;
		}

		if (filters.categoryGroupIds.length > 0 && (!group || !filters.categoryGroupIds.includes(group.group_id))) {
			return false;
		}

		if (filters.categoryIds.length > 0 && !filters.categoryIds.includes(transaction.category_id)) {
			return false;
		}

		if (filters.dateFrom && transactionDate < filters.dateFrom) {
			return false;
		}

		if (filters.dateTo && transactionDate > filters.dateTo) {
			return false;
		}

		if (minAmount !== null && transactionAmount < minAmount) {
			return false;
		}

		if (maxAmount !== null && transactionAmount > maxAmount) {
			return false;
		}

		if (
			search
			&& ![
				transaction.payee ?? '',
				transaction.notes ?? '',
				accountName(transaction.account_id),
				categoryName(transaction.category_id)
			].some((value) => value.toLowerCase().includes(search))
		) {
			return false;
		}

		return true;
	});
}

export function countActiveFilters(filters: TransactionFilters) {
	return (
		(filters.search.trim() ? 1 : 0)
		+ (filters.dateFrom ? 1 : 0)
		+ (filters.dateTo ? 1 : 0)
		+ filters.accountIds.length
		+ filters.types.length
		+ filters.categoryGroupIds.length
		+ filters.categoryIds.length
		+ (filters.amountMin ? 1 : 0)
		+ (filters.amountMax ? 1 : 0)
	);
}
