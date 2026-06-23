import { callApi } from './client';

export type BudgetPeriodType = 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';

export type Budget = {
	budget_id: number;
	user_id: number;
	name: string;
	period_type: BudgetPeriodType;
	start_date: string;
	end_date?: string | null;
};

export type BudgetItem = {
	budget_item_id: number;
	budget_id: number;
	category_id: number;
	planned_amount: number | string;
	rollover_enabled: boolean;
};

export function getBudgets(userId: number) {
	return callApi<Budget[]>('get_budgets', userId);
}

export function getBudget(budgetId: number) {
	return callApi<Budget | null>('get_budget', budgetId);
}

export function createBudget(payload: {
	user_id: number;
	name: string;
	period_type: BudgetPeriodType;
	start_date: string;
	end_date?: string | null;
}) {
	return callApi<{ budget_id: number }>(
		'create_budget',
		payload.user_id,
		payload.name,
		payload.period_type,
		payload.start_date,
		payload.end_date ?? null
	);
}

export function updateBudget(
	budgetId: number,
	payload: {
		name?: string | null;
		period_type?: BudgetPeriodType | null;
		start_date?: string | null;
		end_date?: string | null;
	} = {}
) {
	return callApi<void>(
		'update_budget',
		budgetId,
		payload.name ?? null,
		payload.period_type ?? null,
		payload.start_date ?? null,
		payload.end_date ?? null
	);
}

export function deleteBudget(budgetId: number) {
	return callApi<void>('delete_budget', budgetId);
}

export function getBudgetItems(budgetId: number) {
	return callApi<BudgetItem[]>('get_budget_items', budgetId);
}

export function createBudgetItem(payload: {
	budget_id: number;
	category_id: number;
	planned_amount: number | string;
	rollover_enabled?: boolean;
}) {
	return callApi<{ budget_item_id: number }>(
		'create_budget_item',
		payload.budget_id,
		payload.category_id,
		payload.planned_amount,
		payload.rollover_enabled ?? false
	);
}

export function updateBudgetItem(
	budgetItemId: number,
	payload: {
		planned_amount?: number | string | null;
		category_id?: number | null;
		rollover_enabled?: boolean | null;
	} = {}
) {
	return callApi<void>(
		'update_budget_item',
		budgetItemId,
		payload.planned_amount ?? null,
		payload.category_id ?? null,
		payload.rollover_enabled ?? null
	);
}

export function deleteBudgetItem(budgetItemId: number) {
	return callApi<void>('delete_budget_item', budgetItemId);
}
