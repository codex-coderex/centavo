<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import {
		deleteBudget,
		deleteBudgetItem,
		getBudget,
		getBudgetItems,
		type Budget,
		type BudgetItem
	} from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';
	import BudgetItemsTable from '../features/components/BudgetItemsTable.svelte';
	import BudgetModals from '../features/modals/BudgetModals.svelte';

	const userId = 1;

	let budget: Budget | null = $state(null);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let transactions: Transaction[] = $state([]);
	let editingBudget: Budget | null = $state(null);
	let editingBudgetItem: BudgetItem | null = $state(null);
	let loading = $state(true);
	let loadingItems = $state(false);
	let error = $state('');
	let notice = $state('');
	let showBudgetModal = $state(false);
	let showBudgetItemModal = $state(false);

	let selectedBudgetId = $derived(Number(page.params.budgetId));
	let expenseCategoryIds = $derived(
		categoryGroups
			.filter((group: CategoryGroup) => group.type === 'expense')
			.map((group: CategoryGroup) => group.group_id)
	);
	let expenseCategories = $derived(
		categories.filter(
			(category: Category) =>
				category.is_active && expenseCategoryIds.includes(category.group_id)
		)
	);

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [budgetRow, categoryRows, groupRows, transactionRows] = await Promise.all([
				getBudget(selectedBudgetId),
				getAllCategories(userId),
				getCategoryGroups(userId),
				getTransactionsByUser(userId)
			]);

			if (budgetRow === null) {
				error = 'Budget does not exist.';
				budget = null;
				budgetItems = [];
				return;
			}

			budget = budgetRow;
			categories = categoryRows;
			categoryGroups = groupRows;
			transactions = transactionRows;
			await refreshBudgetItems();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function refreshBudgetItems() {
		loadingItems = true;

		try {
			budgetItems = await getBudgetItems(selectedBudgetId);
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loadingItems = false;
		}
	}

	function openEditBudget() {
		if (!budget) return;

		notice = '';
		editingBudget = budget;
		showBudgetModal = true;
	}

	function openCreateBudgetItem() {
		if (!budget) return;

		notice = '';
		editingBudgetItem = null;
		showBudgetItemModal = true;
	}

	function openEditBudgetItem(item: BudgetItem) {
		notice = '';
		editingBudgetItem = item;
		showBudgetItemModal = true;
	}

	async function removeBudget() {
		if (!budget) return;

		const confirmed = confirm(`Delete "${budget.name}"? This will also delete its budget items.`);
		if (!confirmed) return;

		error = '';
		notice = '';

		try {
			await deleteBudget(budget.budget_id);
			await goto('/budgets');
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

<section class="budget-page flex min-h-screen flex-col gap-5 px-5 py-4">
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

	{#if loading}
		<p class="text-muted px-6 py-12 text-center text-sm">Loading budget...</p>
	{:else}
		<BudgetItemsTable
			{budget}
			items={budgetItems}
			categories={expenseCategories}
			{transactions}
			loading={loadingItems}
			onBack={() => goto('/budgets')}
			onAddItem={openCreateBudgetItem}
			onEditBudget={openEditBudget}
			onDeleteBudget={removeBudget}
			onEditItem={openEditBudgetItem}
			onDeleteItem={removeBudgetItem}
		/>
	{/if}
</section>

<BudgetModals
	bind:showBudgetModal
	bind:showBudgetItemModal
	bind:editingBudget
	bind:editingBudgetItem
	selectedBudgetId={selectedBudgetId}
	{userId}
	{categories}
	{categoryGroups}
	onRefresh={loadPage}
	onRefreshBudgetItems={refreshBudgetItems}
	onNotice={(message) => notice = message}
/>
