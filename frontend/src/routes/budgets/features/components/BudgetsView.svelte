<script lang="ts">
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { Transaction } from '$lib/api/transactions';
	import { itemsForBudget } from '../utils/budgetTotals';
	import BudgetCardGrid from './BudgetCardGrid.svelte';
	import BudgetItemsTable from './BudgetItemsTable.svelte';
	import BudgetsToolbar from './BudgetsToolbar.svelte';

	let {
		budgets,
		budgetItems,
		categories,
		categoryGroups,
		transactions,
		selectedBudgetId = $bindable(),
		loading,
		loadingItems,
		error,
		notice,
		onAddBudget,
		onEditBudget,
		onDeleteBudget,
		onAddItem,
		onEditItem,
		onDeleteItem
	} = $props<{
		budgets: Budget[];
		budgetItems: BudgetItem[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		transactions: Transaction[];
		selectedBudgetId: number | null;
		loading: boolean;
		loadingItems: boolean;
		error: string;
		notice: string;
		onAddBudget: () => void;
		onEditBudget: (budget: Budget) => void;
		onDeleteBudget: (budget: Budget) => void | Promise<void>;
		onAddItem: () => void;
		onEditItem: (item: BudgetItem) => void;
		onDeleteItem: (item: BudgetItem) => void | Promise<void>;
	}>();

	let selectedBudget = $derived(
		budgets.find((budget: Budget) => budget.budget_id === selectedBudgetId) ?? null
	);
	let selectedBudgetItems = $derived(
		selectedBudget ? itemsForBudget(selectedBudget, budgetItems) : []
	);
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
</script>

<section class="budget-page flex min-h-screen flex-col gap-5 px-5 py-4">
	<div class="app-page-header flex flex-wrap items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight">Budgets</h1>
			<p class="text-muted mt-1 text-sm">{budgets.length} budgets</p>
		</div>

		<BudgetsToolbar onAdd={onAddBudget} />
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

	{#if selectedBudget}
		<BudgetItemsTable
			budget={selectedBudget}
			items={selectedBudgetItems}
			categories={expenseCategories}
			{transactions}
			loading={loadingItems}
			onBack={() => selectedBudgetId = null}
			onAddItem={onAddItem}
			onEditBudget={() => onEditBudget(selectedBudget)}
			onDeleteBudget={() => onDeleteBudget(selectedBudget)}
			onEditItem={onEditItem}
			onDeleteItem={onDeleteItem}
		/>
	{:else}
		<BudgetCardGrid
			{budgets}
			{budgetItems}
			{transactions}
			{selectedBudgetId}
			{loading}
			onSelect={(budgetId) => selectedBudgetId = budgetId}
		/>
	{/if}
</section>
