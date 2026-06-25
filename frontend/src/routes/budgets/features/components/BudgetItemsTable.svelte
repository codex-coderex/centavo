<script lang="ts">
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Category } from '$lib/api/categories';
	import type { Transaction } from '$lib/api/transactions';
	import { formatMoney } from '../utils/budgetFormat';
	import {
		budgetProgress,
		plannedForBudgetItemWithRollover,
		plannedForBudgetWithRollover,
		rolloverCarryForBudgetItem,
		spentForBudget,
		spentForBudgetItem
	} from '../utils/budgetTotals';

	let {
		budget,
		items,
		allBudgets,
		allBudgetItems,
		categories,
		transactions,
		loading,
		onEditItem,
		onDeleteItem
	} = $props<{
		budget: Budget | null;
		items: BudgetItem[];
		allBudgets: Budget[];
		allBudgetItems: BudgetItem[];
		categories: Category[];
		transactions: Transaction[];
		loading: boolean;
		onEditItem: (item: BudgetItem) => void;
		onDeleteItem: (item: BudgetItem) => void | Promise<void>;
	}>();

	let planned = $derived(
		budget
			? plannedForBudgetWithRollover(budget, allBudgets, allBudgetItems, transactions)
			: 0
	);
	let spent = $derived(spentForBudget(items, transactions));

	function categoryName(categoryId: number) {
		return categories.find((category: Category) => category.category_id === categoryId)?.name ?? `Category ${categoryId}`;
	}
</script>

{#if budget}
	<div class="grid gap-5">
		<div class="transaction-table-card overflow-hidden">
			{#if loading}
				<p class="text-muted px-6 py-12 text-center text-sm">Loading budget items...</p>
			{:else}
				<div class="border-b px-5 py-4" style="border-color: var(--app-border)">
					<div class="flex flex-wrap items-center justify-between gap-3">
						<p class="text-sm font-semibold">{formatMoney(spent)} spent of {formatMoney(planned)}</p>
						<p class="text-muted text-xs">{items.length} budget items</p>
					</div>
					<div class="mt-3 h-1.5 overflow-hidden rounded-full bg-(--app-soft)">
						<div
							class="h-full rounded-full bg-(--app-orange)"
							style={`width: ${budgetProgress(spent, planned)}%`}
						></div>
					</div>
				</div>

				<div class="overflow-x-auto">
					<table class="w-full text-left text-sm">
						<thead class="text-muted text-[11px] font-bold uppercase tracking-widest">
							<tr>
								<th class="px-5 py-3">Category</th>
								<th class="px-5 py-3">Rollover</th>
								<th class="px-5 py-3 text-right">Spent / Planned</th>
								<th class="px-5 py-3">Progress</th>
								<th class="px-5 py-3 text-right">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each items as item}
								{@const itemSpent = spentForBudgetItem(item, transactions)}
								{@const itemPlanned = plannedForBudgetItemWithRollover(item, budget, allBudgets, allBudgetItems, transactions)}
								{@const itemCarry = rolloverCarryForBudgetItem(item, budget, allBudgets, allBudgetItems, transactions)}
								<tr class="border-t" style="border-color: var(--app-border)">
									<td class="px-5 py-4">
										<span class="pill">{categoryName(item.category_id)}</span>
									</td>
									<td class="px-5 py-4">
										<span class={`pill ${item.rollover_enabled ? '' : 'muted-pill'}`}>
											{item.rollover_enabled ? 'Enabled' : 'Off'}
										</span>
									</td>
									<td class="px-5 py-4 text-right tabular-nums">
										<span class="font-semibold">{formatMoney(itemSpent)}</span>
										<span class="text-muted"> / {formatMoney(itemPlanned)}</span>
										{#if itemCarry !== 0}
											<p class="text-muted mt-1 text-xs">
												{itemCarry > 0 ? '+' : '-'}{formatMoney(Math.abs(itemCarry))} rollover
											</p>
										{/if}
									</td>
									<td class="px-5 py-4">
										<div class="h-1.5 min-w-32 overflow-hidden rounded-full bg-(--app-soft)">
											<div
												class="h-full rounded-full bg-(--app-orange)"
												style={`width: ${budgetProgress(itemSpent, itemPlanned)}%`}
											></div>
										</div>
									</td>
									<td class="px-5 py-4 text-right">
										<div class="flex justify-end gap-3">
											<button class="transaction-row-action" type="button" onclick={() => onEditItem(item)}>Edit</button>
											<button class="transaction-row-action danger" type="button" onclick={() => onDeleteItem(item)}>Remove</button>
										</div>
									</td>
								</tr>
							{:else}
								<tr>
									<td class="text-muted px-5 py-12 text-center text-sm" colspan="5">
										No budget items yet.
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	</div>
{/if}
