<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { completeGoal, getGoalAccounts, getGoals, type Goal, type GoalAccount } from '$lib/api/goals';
	import GoalModals from './features/modals/GoalModals.svelte';
	import GoalsView from './features/components/GoalsView.svelte';

	const userId = 1;

	let goals: Goal[] = $state([]);
	let goalAccounts: GoalAccount[] = $state([]);
	let accounts: Account[] = $state([]);
	let editingGoal: Goal | null = $state(null);
	let fundingGoal: Goal | null = $state(null);
	let deletingGoal: Goal | null = $state(null);
	let loading = $state(true);
	let error = $state('');
	let notice = $state('');
	let showGoalModal = $state(false);
	let showFundsModal = $state(false);
	let showDeleteModal = $state(false);

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

	async function markComplete(goal: Goal) {
		error = '';
		notice = '';

		try {
			await completeGoal(goal.goal_id);
			notice = 'Goal completed.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	function openDeleteGoal(goal: Goal) {
		notice = '';
		deletingGoal = goal;
		showDeleteModal = true;
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
	onAddFunds={openAddFunds}
	onEditGoal={openEditGoal}
	onCompleteGoal={markComplete}
	onDeleteGoal={openDeleteGoal}
/>

<GoalModals
	bind:showGoalModal
	bind:showFundsModal
	bind:showDeleteModal
	bind:editingGoal
	bind:fundingGoal
	bind:deletingGoal
	{userId}
	{accounts}
	{goalAccounts}
	onRefresh={loadPage}
	onNotice={(message) => notice = message}
/>
