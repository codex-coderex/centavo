<script lang="ts">
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Transaction } from '$lib/api/transactions';
	import { formatMoney, periodLabel } from '../utils/budgetFormat';
	import { budgetProgress, itemsForBudget, plannedForBudgetWithRollover, spentForBudget } from '../utils/budgetTotals';

	let {
		budgets,
		budgetItems,
		transactions,
		selectedBudgetId,
		loading,
		onSelect
	} = $props<{
		budgets: Budget[];
		budgetItems: BudgetItem[];
		transactions: Transaction[];
		selectedBudgetId: number | null;
		loading: boolean;
		onSelect: (budgetId: number) => void | Promise<void>;
	}>();

	function dateRange(budget: Budget) {
		const start = budget.start_date.slice(0, 10);
		const end = budget.end_date?.slice(0, 10) ?? 'ongoing';
		return `${start} - ${end}`;
	}
</script>

{#if loading}
	<p class="text-muted px-6 py-12 text-center text-sm">Loading budgets...</p>
{:else if budgets.length === 0}
	<div class="dashboard-card px-6 py-12 text-center">
		<p class="font-semibold">No budgets yet.</p>
		<p class="text-muted mt-1 text-sm">Create a budget to start planning category spending.</p>
	</div>
{:else}
	<div class="grid gap-4 lg:grid-cols-2">
		{#each budgets as budget}
			{@const items = itemsForBudget(budget, budgetItems)}
			{@const planned = plannedForBudgetWithRollover(budget, budgets, budgetItems, transactions)}
			{@const spent = spentForBudget(items, transactions)}
			<button
				class={`budget-card text-left ${selectedBudgetId === budget.budget_id ? 'selected' : ''}`}
				type="button"
				onclick={() => onSelect(budget.budget_id)}
			>
				<div class="flex items-start justify-between gap-4">
					<div class="min-w-0">
						<p class="truncate text-base font-bold">{budget.name}</p>
						<p class="text-muted mt-1 text-xs">{dateRange(budget)}</p>
					</div>

					<span class="pill shrink-0">{periodLabel(budget.period_type)}</span>
				</div>

				<div class="mt-5 flex items-baseline gap-2">
					<p class="font-bold tabular-nums">{formatMoney(spent)}</p>
					<p class="text-muted text-sm">/ {formatMoney(planned)}</p>
				</div>

				<div class="mt-4 h-1.5 overflow-hidden rounded-full bg-(--app-soft)">
					<div
						class="h-full rounded-full bg-(--app-orange)"
						style={`width: ${budgetProgress(spent, planned)}%`}
					></div>
				</div>
			</button>
		{/each}
	</div>
{/if}
