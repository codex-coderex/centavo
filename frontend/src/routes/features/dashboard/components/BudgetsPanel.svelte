<script lang="ts">
	import type { BudgetSummary } from '../utils/dashboardFormat';
	import { formatDate, formatMoney } from '../utils/dashboardFormat';

	let {
		budgets
	} = $props<{
		budgets: BudgetSummary[];
	}>();

	let expandedBudgetId: number | null = $state(null);

	$effect(() => {
		if (expandedBudgetId !== null && !budgets.some((budget: BudgetSummary) => budget.budget_id === expandedBudgetId)) {
			expandedBudgetId = budgets[0]?.budget_id ?? null;
		}

		if (expandedBudgetId === null && budgets.length > 0) {
			expandedBudgetId = budgets[0].budget_id;
		}
	});

	function progress(spent: number, planned: number) {
		if (!planned) return 0;
		return Math.min((spent / planned) * 100, 100);
	}
</script>

<div class="dashboard-card p-5">
	<div class="flex flex-wrap items-start justify-between gap-4">
		<div>
			<h2 class="text-lg font-semibold">Budgets</h2>
			<p class="text-muted mt-1 text-sm">Click a budget to see its categories.</p>
		</div>
		<a class="dashboard-link text-xs" href="/budgets">Manage</a>
	</div>

	<div class="mt-5 grid gap-3">
		{#each budgets as budget}
			{@const isExpanded = expandedBudgetId === budget.budget_id}
			{@const percent = progress(budget.spent_minor, budget.planned_minor)}
			<div class="rounded-xl border" style="border-color: var(--app-border); background: var(--app-surface-strong)">
				<button
					class="w-full p-4 text-left"
					type="button"
					onclick={() => expandedBudgetId = isExpanded ? null : budget.budget_id}
				>
					<div class="flex items-start justify-between gap-4">
						<div>
							<p class="font-semibold">{budget.name}</p>
							<p class="text-muted mt-1 text-xs">
								{formatDate(budget.start_date)} - {formatDate(budget.end_date)} · {budget.period_type}
							</p>
						</div>
						<p class="text-muted text-sm">{budget.items.length} items</p>
					</div>

					<div class="mt-4 h-2 overflow-hidden rounded-full bg-(--app-soft)">
						<div
							class={`h-full rounded-full ${percent >= 100 ? 'bg-(--app-red)' : percent >= 85 ? 'bg-(--app-gold)' : 'bg-(--app-green)'}`}
							style="width:{percent}%"
						></div>
					</div>
					<div class="mt-2 flex items-center justify-between gap-4 text-xs">
						<p><span class="font-semibold">{formatMoney(budget.spent_minor)}</span> spent</p>
						<p class="text-muted">{formatMoney(Math.max(budget.planned_minor - budget.spent_minor, 0))} remaining</p>
					</div>
				</button>

				{#if isExpanded}
					<div class="border-t p-4" style="border-color: var(--app-border)">
						<div class="grid gap-3">
							{#each budget.items as item}
								{@const itemPercent = progress(item.spent_minor, item.planned_amount_minor)}
								<div>
									<div class="flex items-center justify-between gap-4 text-sm">
										<div class="min-w-0">
											<p class="truncate font-medium">{item.category_name}</p>
											<p class="text-muted mt-0.5 text-xs">{item.group_name}</p>
										</div>
										<p class="shrink-0 text-xs">
											<span class={item.spent_minor > item.planned_amount_minor ? 'money-negative font-bold' : 'font-semibold'}>
												{formatMoney(item.spent_minor)}
											</span>
											<span class="text-muted"> / {formatMoney(item.planned_amount_minor)}</span>
										</p>
									</div>
									<div class="mt-2 h-1.5 overflow-hidden rounded-full bg-(--app-soft)">
										<div
											class={`h-full rounded-full ${itemPercent >= 100 ? 'bg-(--app-red)' : itemPercent >= 85 ? 'bg-(--app-gold)' : 'bg-(--app-green)'}`}
											style="width:{itemPercent}%"
										></div>
									</div>
								</div>
							{:else}
								<p class="text-muted text-sm">No budget items yet.</p>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{:else}
			<p class="text-muted py-8 text-center text-sm">No budgets yet.</p>
		{/each}
	</div>
</div>
