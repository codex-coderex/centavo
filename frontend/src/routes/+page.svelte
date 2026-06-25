<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getBudgetItems, getBudgets, type Budget, type BudgetItem } from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import { getGoalAccounts, getGoals, type Goal, type GoalAccount } from '$lib/api/goals';
	import { getRecurringRules, type RecurringRule } from '$lib/api/recurring';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';
	import DashboardView from './features/dashboard/components/DashboardView.svelte';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let budgets: Budget[] = $state([]);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let goals: Goal[] = $state([]);
	let goalAccounts: GoalAccount[] = $state([]);
	let recurringRules: RecurringRule[] = $state([]);
	let transactions: Transaction[] = $state([]);
	let loading = $state(true);
	let error = $state('');

	async function loadDashboard() {
		loading = true;
		error = '';

		try {
			const [
				accountRows,
				budgetRows,
				categoryRows,
				groupRows,
				goalRows,
				recurringRows,
				transactionRows
			] = await Promise.all([
				getAccounts(userId),
				getBudgets(userId),
				getAllCategories(userId),
				getCategoryGroups(userId),
				getGoals(userId),
				getRecurringRules(userId),
				getTransactionsByUser(userId)
			]);

			accounts = accountRows;
			budgets = budgetRows;
			categories = categoryRows;
			categoryGroups = groupRows;
			goals = goalRows;
			recurringRules = recurringRows;
			transactions = transactionRows;

			budgetItems = (await Promise.all(
				budgetRows.map((budget: Budget) => getBudgetItems(budget.budget_id))
			)).flat();

			goalAccounts = (await Promise.all(
				goalRows.map((goal: Goal) => getGoalAccounts(goal.goal_id))
			)).flat();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	onMount(loadDashboard);
</script>

<DashboardView
	{accounts}
	{budgets}
	{budgetItems}
	{categories}
	{categoryGroups}
	{goals}
	{goalAccounts}
	{recurringRules}
	{transactions}
	{loading}
	{error}
/>
