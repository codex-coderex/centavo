import { callApi } from './client';

export type GoalStatus = 'active' | 'completed';

export type Goal = {
	goal_id: number;
	user_id: number;
	account_id: number;
	name: string;
	target_amount_minor: number;
	target_date?: string | null;
	status: GoalStatus;
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
	account_id: number;
	target_date?: string | null;
}) {
	return callApi<{ goal_id: number }>(
		'create_goal',
		payload.user_id,
		payload.name,
		payload.target_amount,
		payload.account_id,
		payload.target_date ?? null
	);
}

export function updateGoal(
	goalId: number,
	payload: {
		name?: string | null;
		target_amount?: number | string | null;
		account_id?: number | null;
		target_date?: string | null;
		status?: GoalStatus | null;
	} = {}
) {
	return callApi<void>(
		'update_goal',
		goalId,
		payload.name ?? null,
		payload.target_amount ?? null,
		payload.account_id ?? null,
		payload.target_date ?? null,
		payload.status ?? null
	);
}

export function completeGoal(goalId: number) {
	return callApi<void>('complete_goal', goalId);
}