<script lang="ts">
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Transaction } from '$lib/api/transactions';
	import PageHeader from '$lib/shared/components/PageHeader.svelte';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
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

<ToastOnChange {error} {notice} />

<section class="budget-page flex min-h-screen flex-col">
	<PageHeader eyebrow="Plan" title="Budgets" subtitle={`${budgets.length} budgets`}>
		<BudgetsToolbar onAdd={onAddBudget} />
	</PageHeader>

	<div class="flex flex-col gap-5 p-5">
		<BudgetCardGrid
			{budgets}
			{budgetItems}
			{transactions}
			selectedBudgetId={null}
			{loading}
			onSelect={onSelectBudget}
		/>
	</div>
</section>
