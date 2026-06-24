<script lang="ts">
	import { onMount } from 'svelte';
	import {
		deleteBudget,
		deleteBudgetItem,
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
	let editingBudgetItem: BudgetItem | null = $state(null);
	let loading = $state(true);
	let loadingItems = $state(false);
	let error = $state('');
	let notice = $state('');
	let showBudgetModal = $state(false);
	let showBudgetItemModal = $state(false);

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

	async function refreshBudgetItems() {
		if (selectedBudgetId === null) return;

		loadingItems = true;

		try {
			const rows = await getBudgetItems(selectedBudgetId);
			budgetItems = [
				...budgetItems.filter((item: BudgetItem) => item.budget_id !== selectedBudgetId),
				...rows
			];
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loadingItems = false;
		}
	}

	function openCreateBudget() {
		notice = '';
		editingBudget = null;
		showBudgetModal = true;
	}

	function openEditBudget(budget: Budget) {
		notice = '';
		editingBudget = budget;
		showBudgetModal = true;
	}

	function openCreateBudgetItem() {
		if (selectedBudgetId === null) return;

		notice = '';
		editingBudgetItem = null;
		showBudgetItemModal = true;
	}

	function openEditBudgetItem(item: BudgetItem) {
		notice = '';
		editingBudgetItem = item;
		showBudgetItemModal = true;
	}

	async function removeBudget(budget: Budget) {
		const confirmed = confirm(`Delete "${budget.name}"? This will also delete its budget items.`);
		if (!confirmed) return;

		error = '';
		notice = '';

		try {
			await deleteBudget(budget.budget_id);
			notice = 'Budget deleted.';
			selectedBudgetId = null;
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function removeBudgetItem(item: BudgetItem) {
		const category = categories.find((row: Category) => row.category_id === item.category_id);
		const confirmed = confirm(`Remove budget item for "${category?.name ?? `Category ${item.category_id}`}"?`);
		if (!confirmed) return;

		error = '';
		notice = '';

		try {
			await deleteBudgetItem(item.budget_item_id);
			notice = 'Budget item removed.';
			await refreshBudgetItems();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadPage);
</script>

<BudgetsView
	{budgets}
	{budgetItems}
	{categories}
	{categoryGroups}
	{transactions}
	bind:selectedBudgetId
	{loading}
	{loadingItems}
	{error}
	{notice}
	onAddBudget={openCreateBudget}
	onEditBudget={openEditBudget}
	onDeleteBudget={removeBudget}
	onAddItem={openCreateBudgetItem}
	onEditItem={openEditBudgetItem}
	onDeleteItem={removeBudgetItem}
/>

<BudgetModals
	bind:showBudgetModal
	bind:showBudgetItemModal
	bind:editingBudget
	bind:editingBudgetItem
	bind:selectedBudgetId
	{userId}
	{categories}
	{categoryGroups}
	onRefresh={loadPage}
	onRefreshBudgetItems={refreshBudgetItems}
	onNotice={(message) => notice = message}
/>
