<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getGoalAccounts, getGoals, type Goal, type GoalAccount } from '$lib/api/goals';
	import GoalModals from './features/modals/GoalModals.svelte';
	import ArchivedGoalsModal from './features/modals/ArchivedGoalsModal.svelte';
	import GoalsView from './features/components/GoalsView.svelte';

	const userId = 1;

	let goals: Goal[] = $state([]);
	let goalAccounts: GoalAccount[] = $state([]);
	let accounts: Account[] = $state([]);
	let editingGoal: Goal | null = $state(null);
	let fundingGoal: Goal | null = $state(null);
	let deletingGoal: Goal | null = $state(null);
	let completingGoal: Goal | null = $state(null);
	let loading = $state(true);
	let error = $state('');
	let notice = $state('');
	let showGoalModal = $state(false);
	let showFundsModal = $state(false);
	let showDeleteModal = $state(false);
	let showCompleteModal = $state(false);
	let showArchivedModal = $state(false);

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [goalRows, accountRows] = await Promise.all([
				getGoals(userId),
				getAccounts(userId)
			]);

			goals = goalRows;
			accounts = accountRows;
			goalAccounts = (await Promise.all(
				goalRows.map((goal: Goal) => getGoalAccounts(goal.goal_id))
			)).flat();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function openCreateGoal() {
		notice = '';
		editingGoal = null;
		showGoalModal = true;
	}

	function openEditGoal(goal: Goal) {
		notice = '';
		editingGoal = goal;
		showGoalModal = true;
	}

	function openAddFunds(goal: Goal) {
		notice = '';
		fundingGoal = goal;
		showFundsModal = true;
	}

	function openCompleteGoal(goal: Goal) {
		notice = '';
		completingGoal = goal;
		showCompleteModal = true;
	}

	function openDeleteGoal(goal: Goal) {
		notice = '';
		deletingGoal = goal;
		showDeleteModal = true;
	}

	function openArchivedGoals() {
		showArchivedModal = true;
	}

	function closeArchivedGoals() {
		showArchivedModal = false;
	}

	onMount(loadPage);
</script>

<GoalsView
	{goals}
	{goalAccounts}
	{accounts}
	{loading}
	{error}
	{notice}
	onAddGoal={openCreateGoal}
	onArchivedGoals={openArchivedGoals}
	onAddFunds={openAddFunds}
	onEditGoal={openEditGoal}
	onCompleteGoal={openCompleteGoal}
	onDeleteGoal={openDeleteGoal}
/>

<GoalModals
	bind:showGoalModal
	bind:showFundsModal
	bind:showDeleteModal
	bind:showCompleteModal
	bind:editingGoal
	bind:fundingGoal
	bind:deletingGoal
	bind:completingGoal
	{userId}
	{accounts}
	{goalAccounts}
	onRefresh={loadPage}
	onNotice={(message) => notice = message}
/>

{#if showArchivedModal}
	<ArchivedGoalsModal
		goals={goals.filter((goal: Goal) => goal.status === 'completed')}
		{goalAccounts}
		{accounts}
		onClose={closeArchivedGoals}
	/>
{/if}
