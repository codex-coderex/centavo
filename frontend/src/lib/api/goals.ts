import { callApi } from './client';

export type GoalStatus = 'active' | 'completed';

export type Goal = {
	goal_id: number;
	user_id: number;
	name: string;
	target_amount_minor: number;
	target_date?: string | null;
	status: GoalStatus;
};

export type GoalAccount = {
	goal_id: number;
	account_id: number;
	allocated_amount_minor: number;
};

export function getGoals(userId: number) {
	return callApi<Goal[]>('get_goals', userId);
}

export function getGoal(goalId: number) {
	return callApi<Goal | null>('get_goal', goalId);
}

export function createGoal(payload: {
	user_id: number;
	name: string;
	target_amount: number | string;
	target_date?: string | null;
}) {
	return callApi<{ goal_id: number }>(
		'create_goal',
		payload.user_id,
		payload.name,
		payload.target_amount,
		payload.target_date ?? null
	);
}

export function updateGoal(
	goalId: number,
	payload: {
		name?: string | null;
		target_amount?: number | string | null;
		target_date?: string | null;
		status?: GoalStatus | null;
	} = {}
) {
	return callApi<{ status: string }>(
		'update_goal',
		goalId,
		payload.name ?? null,
		payload.target_amount ?? null,
		payload.target_date ?? null,
		payload.status ?? null
	);
}

export function completeGoal(goalId: number) {
	return callApi<{ status: string }>('complete_goal', goalId);
}

export function getGoalAccounts(goalId: number) {
	return callApi<GoalAccount[]>('get_goal_accounts', goalId);
}

export function addAccountToGoal(payload: {
	goal_id: number;
	account_id: number;
	allocated_amount?: number | string;
}) {
	return callApi<{ status: string }>(
		'add_account_to_goal',
		payload.goal_id,
		payload.account_id,
		payload.allocated_amount ?? 0
	);
}

export function updateGoalAccountAllocation(payload: {
	goal_id: number;
	account_id: number;
	allocated_amount: number | string;
}) {
	return callApi<{ status: string }>(
		'update_goal_account_allocation',
		payload.goal_id,
		payload.account_id,
		payload.allocated_amount
	);
}

export function removeAccountFromGoal(goalId: number, accountId: number) {
	return callApi<{ status: string }>('remove_account_from_goal', goalId, accountId);
}
