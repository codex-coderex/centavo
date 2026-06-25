<script lang="ts">
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Transaction } from '$lib/api/transactions';
	import BudgetCardGrid from './BudgetCardGrid.svelte';
	import BudgetsToolbar from './BudgetsToolbar.svelte';

	let {
		budgets,
		budgetItems,
		transactions,
		loading,
		error,
		notice,
		onAddBudget,
		onSelectBudget
	} = $props<{
		budgets: Budget[];
		budgetItems: BudgetItem[];
		transactions: Transaction[];
		loading: boolean;
		error: string;
		notice: string;
		onAddBudget: () => void;
		onSelectBudget: (budgetId: number) => void | Promise<void>;
	}>();
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

	<BudgetCardGrid
		{budgets}
		{budgetItems}
		{transactions}
		selectedBudgetId={null}
		{loading}
		onSelect={onSelectBudget}
	/>
</section>
