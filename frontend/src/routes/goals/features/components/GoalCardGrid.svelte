<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Goal, GoalAccount } from '$lib/api/goals';
	import { formatDate, formatMoney, goalProgress } from '../utils/goalFormat';
	import { allocatedForGoal, primaryAccountForGoal } from '../utils/goalTotals';

	let {
		goals,
		goalAccounts,
		accounts,
		loading,
		onAddFunds,
		onEdit,
		onComplete,
		onDelete
	} = $props<{
		goals: Goal[];
		goalAccounts: GoalAccount[];
		accounts: Account[];
		loading: boolean;
		onAddFunds: (goal: Goal) => void;
		onEdit: (goal: Goal) => void;
		onComplete: (goal: Goal) => void | Promise<void>;
		onDelete: (goal: Goal) => void;
	}>();

	let activeGoals = $derived(goals.filter((goal: Goal) => goal.status === 'active'));
	let completedGoals = $derived(goals.filter((goal: Goal) => goal.status === 'completed'));

	function accountLabel(goal: Goal) {
		return primaryAccountForGoal(goal.goal_id, goalAccounts, accounts)?.name ?? 'No linked account';
	}
</script>

{#if loading}
	<p class="text-muted px-6 py-12 text-center text-sm">Loading goals...</p>
{:else if goals.length === 0}
	<div class="dashboard-card px-6 py-12 text-center">
		<p class="text-muted mt-1 text-sm">Create a goal to reserve account funds for a target.</p>
	</div>
{:else}
	<div class="grid gap-8">
		<div class="grid gap-4 lg:grid-cols-2">
			{#each activeGoals as goal}
				{@const allocated = allocatedForGoal(goal.goal_id, goalAccounts)}
				{@const progress = goalProgress(allocated, goal.target_amount_minor)}
				<div class="budget-card">
					<div class="flex items-start justify-between gap-4">
						<div class="min-w-0">
							<p class="truncate text-base font-bold">{goal.name}</p>
							<p class="text-muted mt-1 text-xs">
								{accountLabel(goal)} · due {formatDate(goal.target_date)}
							</p>
						</div>
						<span class="pill shrink-0">{Math.round(progress)}%</span>
					</div>

					<div class="mt-5 flex items-baseline gap-2">
						<p class="font-bold tabular-nums">{formatMoney(allocated)}</p>
						<p class="text-muted text-sm">/ {formatMoney(goal.target_amount_minor)}</p>
					</div>

					<div class="mt-4 h-1.5 overflow-hidden rounded-full bg-(--app-soft)">
						<div class="h-full rounded-full bg-(--app-orange)" style={`width: ${progress}%`}></div>
					</div>

					<div class="mt-4 flex flex-wrap items-center gap-2">
						<button class="secondary-action" type="button" onclick={() => onAddFunds(goal)}>+ Add funds</button>
						<button class="transaction-row-action" type="button" onclick={() => onEdit(goal)}>Edit</button>
						<button class="transaction-row-action" type="button" onclick={() => onComplete(goal)}>Complete</button>
						<button class="transaction-row-action danger" type="button" onclick={() => onDelete(goal)}>Delete</button>
					</div>
				</div>
			{/each}
		</div>

		{#if completedGoals.length > 0}
			<section class="grid gap-4">
				<h2 class="text-sm font-semibold">Completed</h2>
				<div class="grid gap-4 lg:grid-cols-2">
					{#each completedGoals as goal}
						{@const allocated = allocatedForGoal(goal.goal_id, goalAccounts)}
						<div class="budget-card opacity-75">
							<div class="flex items-start justify-between gap-4">
								<div>
									<p class="font-bold">{goal.name}</p>
									<p class="text-muted mt-1 text-xs">{accountLabel(goal)}</p>
								</div>
								<span class="pill">Done</span>
							</div>
							<div class="mt-5 flex items-baseline gap-2">
								<p class="font-bold tabular-nums">{formatMoney(allocated)}</p>
								<p class="text-muted text-sm">/ {formatMoney(goal.target_amount_minor)}</p>
							</div>
							<div class="mt-4 flex flex-wrap items-center gap-2">
								<button class="transaction-row-action" type="button" onclick={() => onEdit(goal)}>Edit</button>
								<button class="transaction-row-action danger" type="button" onclick={() => onDelete(goal)}>Delete</button>
							</div>
						</div>
					{/each}
				</div>
			</section>
		{/if}
	</div>
{/if}
