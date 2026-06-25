<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import {
		getBudgetItems,
		getBudgets,
		type Budget,
		type BudgetItem
	} from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';
	import BudgetsView from './features/components/BudgetsView.svelte';
	import BudgetModals from './features/modals/BudgetModals.svelte';

	const userId = 1;

	let budgets: Budget[] = $state([]);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let transactions: Transaction[] = $state([]);
	let selectedBudgetId: number | null = $state(null);
	let editingBudget: Budget | null = $state(null);
	let loading = $state(true);
	let error = $state('');
	let notice = $state('');
	let showBudgetModal = $state(false);

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [budgetRows, categoryRows, groupRows, transactionRows] = await Promise.all([
				getBudgets(userId),
				getAllCategories(userId),
				getCategoryGroups(userId),
				getTransactionsByUser(userId)
			]);

			budgets = budgetRows;
			budgetItems = (await Promise.all(
				budgetRows.map((budget: Budget) => getBudgetItems(budget.budget_id))
			)).flat();
			categories = categoryRows;
			categoryGroups = groupRows;
			transactions = transactionRows;

			if (selectedBudgetId !== null && !budgetRows.some((budget: Budget) => budget.budget_id === selectedBudgetId)) {
				selectedBudgetId = null;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function openCreateBudget() {
		notice = '';
		editingBudget = null;
		showBudgetModal = true;
	}

	function openBudgetDetail(budgetId: number) {
		goto(`/budgets/${budgetId}`);
	}

	onMount(loadPage);
</script>

<BudgetsView
	{budgets}
	{budgetItems}
	{transactions}
	{loading}
	{error}
	{notice}
	onAddBudget={openCreateBudget}
	onSelectBudget={openBudgetDetail}
/>

<BudgetModals
	bind:showBudgetModal
	showBudgetItemModal={false}
	bind:editingBudget
	editingBudgetItem={null}
	bind:selectedBudgetId
	{userId}
	{categories}
	{categoryGroups}
	onRefresh={loadPage}
	onRefreshBudgetItems={async () => {}}
	onNotice={(message) => notice = message}
/>
