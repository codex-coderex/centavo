<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Goal, GoalAccount } from '$lib/api/goals';
	import { countGoalsByStatus } from '../utils/goalTotals';
	import GoalCardGrid from './GoalCardGrid.svelte';
	import GoalsToolbar from './GoalsToolbar.svelte';

	let {
		goals,
		goalAccounts,
		accounts,
		loading,
		error,
		notice,
		onAddGoal,
		onAddFunds,
		onEditGoal,
		onCompleteGoal,
		onDeleteGoal
	} = $props<{
		goals: Goal[];
		goalAccounts: GoalAccount[];
		accounts: Account[];
		loading: boolean;
		error: string;
		notice: string;
		onAddGoal: () => void;
		onAddFunds: (goal: Goal) => void;
		onEditGoal: (goal: Goal) => void;
		onCompleteGoal: (goal: Goal) => void | Promise<void>;
		onDeleteGoal: (goal: Goal) => void;
	}>();

	let goalCounts = $derived(countGoalsByStatus(goals));
</script>

<section class="budget-page flex min-h-screen flex-col gap-5 px-5 py-4">
	<div class="app-page-header flex flex-wrap items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight">Goals</h1>
			<p class="text-muted mt-1 text-sm">
				{goalCounts.active} active · {goalCounts.completed} completed
			</p>
		</div>

		<GoalsToolbar onAdd={onAddGoal} />
	</div>

	{#if error}
		<div class="rounded-2xl border p-4 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="rounded-2xl border p-4 text-sm money-positive" style="border-color: rgba(47, 143, 107, 0.3); background: rgba(47, 143, 107, 0.08)">
			{notice}
		</div>
	{/if}

	<GoalCardGrid
		{goals}
		{goalAccounts}
		{accounts}
		{loading}
		onAddFunds={onAddFunds}
		onEdit={onEditGoal}
		onComplete={onCompleteGoal}
		onDelete={onDeleteGoal}
	/>
</section>
