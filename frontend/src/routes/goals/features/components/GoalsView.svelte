<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Goal, GoalAccount } from '$lib/api/goals';
	import PageHeader from '$lib/shared/components/PageHeader.svelte';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
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

<ToastOnChange {error} {notice} />

<section class="budget-page flex min-h-screen flex-col">
	<PageHeader eyebrow="Reserve" title="Goals" subtitle={`${goalCounts.active} active · ${goalCounts.completed} completed`}>
		<GoalsToolbar onAdd={onAddGoal} />
	</PageHeader>

	<div class="flex flex-col gap-5 p-5">
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
	</div>
</section>
