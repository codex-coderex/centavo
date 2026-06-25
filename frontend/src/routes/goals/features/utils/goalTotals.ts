import type { Account } from '$lib/api/accounts';
import type { Goal, GoalAccount } from '$lib/api/goals';

export function allocationsForGoal(goalId: number, goalAccounts: GoalAccount[]) {
	return goalAccounts.filter((row: GoalAccount) => row.goal_id === goalId);
}

export function allocatedForGoal(goalId: number, goalAccounts: GoalAccount[]) {
	return allocationsForGoal(goalId, goalAccounts).reduce(
		(total: number, row: GoalAccount) => total + row.allocated_amount_minor,
		0
	);
}

export function primaryAccountForGoal(goalId: number, goalAccounts: GoalAccount[], accounts: Account[]) {
	const allocation = allocationsForGoal(goalId, goalAccounts)[0];
	if (!allocation) return null;

	return accounts.find((account: Account) => account.account_id === allocation.account_id) ?? null;
}

export function countGoalsByStatus(goals: Goal[]) {
	return {
		active: goals.filter((goal: Goal) => goal.status === 'active').length,
		completed: goals.filter((goal: Goal) => goal.status === 'completed').length
	};
}
