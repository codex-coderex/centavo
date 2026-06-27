<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import ConfirmActionModal from '$lib/shared/components/ConfirmActionModal.svelte';
	import PageHeader from '$lib/shared/components/PageHeader.svelte';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
	import {
		deleteBudget,
		deleteBudgetItem,
		getBudget,
		getBudgetItems,
		getBudgets,
		type Budget,
		type BudgetItem
	} from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';
	import BudgetItemsTable from '../features/components/BudgetItemsTable.svelte';
	import BudgetModals from '../features/modals/BudgetModals.svelte';
	import { periodLabel } from '../features/utils/budgetFormat';

	const userId = 1;

	let budget: Budget | null = $state(null);
	let allBudgets: Budget[] = $state([]);
	let allBudgetItems: BudgetItem[] = $state([]);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let transactions: Transaction[] = $state([]);
	let editingBudget: Budget | null = $state(null);
	let editingBudgetItem: BudgetItem | null = $state(null);
	let deletingBudget: Budget | null = $state(null);
	let deletingBudgetItem: BudgetItem | null = $state(null);
	let loading = $state(true);
	let loadingItems = $state(false);
	let error = $state('');
	let notice = $state('');
	let actionError = $state('');
	let actionSaving = $state(false);
	let showBudgetModal = $state(false);
	let showBudgetItemModal = $state(false);
	let showDeleteBudgetModal = $state(false);
	let showDeleteBudgetItemModal = $state(false);

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
			const [budgetRow, budgetRows, categoryRows, groupRows, transactionRows] = await Promise.all([
				getBudget(selectedBudgetId),
				getBudgets(userId),
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
			allBudgets = budgetRows;
			allBudgetItems = (await Promise.all(
				budgetRows.map((row: Budget) => getBudgetItems(row.budget_id))
			)).flat();
			budgetItems = allBudgetItems.filter((item: BudgetItem) => item.budget_id === selectedBudgetId);
			categories = categoryRows;
			categoryGroups = groupRows;
			transactions = transactionRows;
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
			if (allBudgets.length > 0) {
				allBudgetItems = (await Promise.all(
					allBudgets.map((row: Budget) => getBudgetItems(row.budget_id))
				)).flat();
			} else {
				allBudgetItems = budgetItems;
			}
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

	function openDeleteBudget() {
		if (!budget) return;

		actionError = '';
		notice = '';
		deletingBudget = budget;
		showDeleteBudgetModal = true;
	}

	function closeDeleteBudget() {
		showDeleteBudgetModal = false;
		deletingBudget = null;
		actionError = '';
		actionSaving = false;
	}

	async function confirmDeleteBudget() {
		if (!deletingBudget) return;

		actionError = '';
		notice = '';
		actionSaving = true;

		try {
			await deleteBudget(deletingBudget.budget_id);
			await goto('/budgets');
		} catch (err) {
			actionError = err instanceof Error ? err.message : String(err);
		} finally {
			actionSaving = false;
		}
	}

	function openDeleteBudgetItem(item: BudgetItem) {
		actionError = '';
		notice = '';
		deletingBudgetItem = item;
		showDeleteBudgetItemModal = true;
	}

	function closeDeleteBudgetItem() {
		showDeleteBudgetItemModal = false;
		deletingBudgetItem = null;
		actionError = '';
		actionSaving = false;
	}

	async function confirmDeleteBudgetItem() {
		if (!deletingBudgetItem) return;

		actionError = '';
		notice = '';
		actionSaving = true;

		try {
			await deleteBudgetItem(deletingBudgetItem.budget_item_id);
			notice = 'Budget item removed.';
			closeDeleteBudgetItem();
			await refreshBudgetItems();
		} catch (err) {
			actionError = err instanceof Error ? err.message : String(err);
		} finally {
			actionSaving = false;
		}
	}

	onMount(loadPage);
</script>

<ToastOnChange {error} {notice} />

<section class="budget-page flex min-h-screen flex-col">
	{#if budget}
		<PageHeader
			eyebrow="Budget"
			title={budget.name}
			subtitle={`${budget.start_date.slice(0, 10)} - ${budget.end_date?.slice(0, 10) ?? 'ongoing'} · ${periodLabel(budget.period_type).toLowerCase()}`}
		>
			<button class="secondary-action" type="button" onclick={() => goto('/budgets')}>All budgets</button>
			<button class="secondary-action" type="button" onclick={openEditBudget}>Edit</button>
			<button class="danger-action" type="button" onclick={openDeleteBudget}>Delete</button>
			<button class="primary-action" type="button" onclick={openCreateBudgetItem}>+ Add item</button>
		</PageHeader>
	{:else}
		<PageHeader eyebrow="Budget" title="Budget" subtitle="Loading budget..." />
	{/if}

	<div class="flex flex-col gap-5 p-5">
		{#if loading}
			<p class="text-muted px-6 py-12 text-center text-sm">Loading budget...</p>
		{:else}
			<BudgetItemsTable
				{budget}
				items={budgetItems}
				{allBudgets}
				{allBudgetItems}
				categories={expenseCategories}
				{transactions}
				loading={loadingItems}
				onEditItem={openEditBudgetItem}
				onDeleteItem={openDeleteBudgetItem}
			/>
		{/if}
	</div>
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

{#if showDeleteBudgetModal && deletingBudget}
	<ConfirmActionModal
		eyebrow="Delete budget"
		title={deletingBudget.name}
		message="This will delete the budget."
		detail="All budget items under this budget will also be removed. This action cannot be undone."
		confirmLabel="Delete budget"
		savingLabel="Deleting..."
		saving={actionSaving}
		error={actionError}
		onClose={closeDeleteBudget}
		onConfirm={confirmDeleteBudget}
	/>
{/if}

{#if showDeleteBudgetItemModal && deletingBudgetItem}
	{@const category = categories.find((row: Category) => row.category_id === deletingBudgetItem.category_id)}
	<ConfirmActionModal
		eyebrow="Remove budget item"
		title={category?.name ?? `Category ${deletingBudgetItem.category_id}`}
		message="This will remove the budget item."
		detail="The planned amount for this category will be removed from the budget. Existing transactions are not deleted."
		confirmLabel="Remove item"
		savingLabel="Removing..."
		saving={actionSaving}
		error={actionError}
		onClose={closeDeleteBudgetItem}
		onConfirm={confirmDeleteBudgetItem}
	/>
{/if}
