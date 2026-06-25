<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Goal, GoalAccount } from '$lib/api/goals';
	import { accountName, formatDate, formatMoney, goalAllocation } from '../utils/dashboardFormat';

	let {
		goals,
		goalAccounts,
		accounts
	} = $props<{
		goals: Goal[];
		goalAccounts: GoalAccount[];
		accounts: Account[];
	}>();

	let activeGoals = $derived(goals.filter((goal: Goal) => goal.status === 'active').slice(0, 3));

	function allocationsForGoal(goal: Goal) {
		return goalAccounts.filter((allocation: GoalAccount) => allocation.goal_id === goal.goal_id);
	}
</script>

<div class="dashboard-card p-5">
	<div class="flex items-start justify-between gap-4">
		<div>
			<h2 class="text-lg font-semibold">Goals</h2>
			<p class="text-muted mt-1 text-sm">Allocated money set aside from accounts.</p>
		</div>
		<a class="dashboard-link text-xs" href="/goals">Manage</a>
	</div>

	<div class="mt-5 grid gap-4">
		{#each activeGoals as goal}
			{@const allocated = goalAllocation(goal, goalAccounts)}
			{@const percent = goal.target_amount_minor ? Math.min((allocated / goal.target_amount_minor) * 100, 100) : 0}
			<div>
				<div class="flex items-start justify-between gap-4">
					<div class="min-w-0">
						<p class="truncate font-semibold">{goal.name}</p>
						<p class="text-muted mt-1 text-xs">Due {formatDate(goal.target_date)}</p>
					</div>
					<p class="text-right text-sm font-bold">{Math.round(percent)}%</p>
				</div>
				<div class="mt-3 h-2 overflow-hidden rounded-full bg-(--app-soft)">
					<div class="h-full rounded-full bg-(--app-green)" style="width:{percent}%"></div>
				</div>
				<div class="mt-2 flex items-center justify-between gap-4 text-xs">
					<p class="font-semibold">{formatMoney(allocated)} / <span class="text-muted">{formatMoney(goal.target_amount_minor)}</span></p>
					<p class="text-muted truncate">
						{allocationsForGoal(goal).map((allocation: GoalAccount) => accountName(accounts, allocation.account_id)).join(', ') || 'No account'}
					</p>
				</div>
			</div>
		{:else}
			<p class="text-muted py-6 text-center text-sm">No active goals yet.</p>
		{/each}
	</div>
</div>
