<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createBudget,
		createBudgetItem,
		deleteBudget,
		deleteBudgetItem,
		getBudgetItems,
		getBudgets,
		type Budget,
		type BudgetItem,
		type BudgetPeriod
	} from '$lib/api/budgets';
	import { getAllCategories, type Category } from '$lib/api/categories';

	const userId = 1;

	let budgets: Budget[] = $state([]);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);

	let selectedBudgetId: number | null = $state(null);
	let loading = $state(true);
	let loadingItems = $state(false);
	let saving = $state(false);
	let error = $state('');
	let notice = $state('');

	let name = $state('');
	let period: BudgetPeriod = $state('monthly');
	let startDate = $state(new Date().toISOString().slice(0, 10));
	let endDate = $state('');

	let itemCategoryId: number | null = $state(null);
	let plannedAmount = $state('');

	const periods: { value: BudgetPeriod; label: string }[] = [
		{ value: 'weekly', label: 'Weekly' },
		{ value: 'monthly', label: 'Monthly' },
		{ value: 'quarterly', label: 'Quarterly' },
		{ value: 'yearly', label: 'Yearly' },
		{ value: 'custom', label: 'Custom' }
	];

	let selectedBudget = $derived(
		budgets.find((budget) => budget.budget_id === selectedBudgetId) ?? null
	);

	function formatMoney(amountMinor: number) {
		return new Intl.NumberFormat('en-PH', {
			style: 'currency',
			currency: 'PHP'
		}).format(amountMinor / 100);
	}

	function categoryName(categoryId: number) {
		return categories.find((category) => category.category_id === categoryId)?.name ?? `Category ${categoryId}`;
	}

	function formatDate(value: string | null | undefined) {
		if (!value) return '—';

		return new Date(value).toLocaleDateString('en-PH', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	async function loadBudgets() {
		loading = true;
		error = '';
		notice = '';

		try {
			const [budgetRows, categoryRows] = await Promise.all([
				getBudgets(userId),
				getAllCategories(userId)
			]);

			budgets = budgetRows;
			categories = categoryRows;

			if (selectedBudgetId === null && budgetRows.length > 0) {
				selectedBudgetId = budgetRows[0].budget_id;
				await loadBudgetItems(selectedBudgetId);
			} else if (selectedBudgetId !== null) {
				await loadBudgetItems(selectedBudgetId);
			}

			if (itemCategoryId === null && categoryRows.length > 0) {
				itemCategoryId = categoryRows[0].category_id;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function loadBudgetItems(budgetId: number) {
		loadingItems = true;

		try {
			budgetItems = await getBudgetItems(budgetId);
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loadingItems = false;
		}
	}

	async function selectBudget(budgetId: number) {
		selectedBudgetId = budgetId;
		error = '';
		notice = '';
		await loadBudgetItems(budgetId);
	}

	async function submitBudget() {
		error = '';
		notice = '';

		if (!name.trim()) {
			error = 'Budget name is required.';
			return;
		}

		if (!startDate) {
			error = 'Start date is required.';
			return;
		}

		saving = true;

		try {
			const result = await createBudget({
				user_id: userId,
				name: name.trim(),
				period,
				start_date: startDate,
				end_date: endDate || null
			});

			name = '';
			period = 'monthly';
			startDate = new Date().toISOString().slice(0, 10);
			endDate = '';

			selectedBudgetId = result.budget_id;
			notice = 'Budget created.';
			await loadBudgets();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function removeBudget(budget: Budget) {
		if (!confirm(`Delete "${budget.name}"? This will also delete its budget items.`)) {
			return;
		}

		error = '';
		notice = '';

		try {
			await deleteBudget(budget.budget_id);
			notice = 'Budget deleted.';

			if (selectedBudgetId === budget.budget_id) {
				selectedBudgetId = null;
				budgetItems = [];
			}

			await loadBudgets();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function submitBudgetItem() {
		error = '';
		notice = '';

		if (selectedBudgetId === null) {
			error = 'Select a budget first.';
			return;
		}

		if (itemCategoryId === null) {
			error = 'Select a category first.';
			return;
		}

		if (!plannedAmount.trim()) {
			error = 'Planned amount is required.';
			return;
		}

		try {
			await createBudgetItem({
				budget_id: selectedBudgetId,
				category_id: itemCategoryId,
				planned_amount: plannedAmount
			});

			plannedAmount = '';
			notice = 'Budget item created.';
			await loadBudgetItems(selectedBudgetId);
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function removeBudgetItem(item: BudgetItem) {
		if (!confirm(`Remove budget item for "${categoryName(item.category_id)}"?`)) {
			return;
		}

		error = '';
		notice = '';

		try {
			await deleteBudgetItem(item.budget_item_id);
			notice = 'Budget item deleted.';

			if (selectedBudgetId !== null) {
				await loadBudgetItems(selectedBudgetId);
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadBudgets);
</script>

<div class="flex flex-col gap-8 p-8">

	<div class="flex items-end justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Plan</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-50">Budgets</h1>
			<p class="mt-2 text-sm text-slate-400">Plan spending by category. This is still an integration stand-in.</p>
		</div>
		<div class="rounded-full border border-slate-800/60 bg-slate-900/80 px-3 py-1 text-xs font-medium text-slate-400">
			{budgets.length} budgets
		</div>
	</div>

	{#if error}
		<div class="rounded-2xl border border-red-500/30 bg-red-950/30 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-sm text-emerald-200">
			{notice}
		</div>
	{/if}

	<div class="grid gap-4 xl:grid-cols-[380px_1fr]">
		
		<div class="flex flex-col gap-4">
			
			<form
				class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-6"
				onsubmit={(event) => {
					event.preventDefault();
					submitBudget();
				}}
			>
				<p class="text-sm font-semibold text-slate-100">New budget</p>
				<p class="mt-1 text-xs text-slate-500">
					Create a dated budget window.
				</p>

				<label class="mt-5 grid gap-2">
					<span class="text-sm font-medium text-slate-300">Budget name</span>
					<input
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
						bind:value={name}
						placeholder="March 2026 Budget"
					/>
				</label>

				<label class="mt-4 grid gap-2">
					<span class="text-sm font-medium text-slate-300">Period</span>
					<select
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
						bind:value={period}
					>
						{#each periods as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</label>

				<div class="mt-4 grid gap-4 sm:grid-cols-2">
					<label class="grid gap-2">
						<span class="text-sm font-medium text-slate-300">Start date</span>
						<input
							class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
							type="date"
							bind:value={startDate}
						/>
					</label>

					<label class="grid gap-2">
						<span class="text-sm font-medium text-slate-300">End date</span>
						<input
							class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
							type="date"
							bind:value={endDate}
						/>
					</label>
				</div>

				<button
					class="mt-5 w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
					type="submit"
					disabled={saving}
				>
					{saving ? 'Creating...' : 'Create budget'}
				</button>
			</form>

			<form
				class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-6"
				onsubmit={(event) => {
					event.preventDefault();
					submitBudgetItem();
				}}
			>
				<p class="text-sm font-semibold text-slate-100">New budget item</p>
				<p class="mt-1 text-xs text-slate-500">
					Add a planned category amount to the selected budget.
				</p>

				<label class="mt-5 grid gap-2">
					<span class="text-sm font-medium text-slate-300">Category</span>
					<select
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
						bind:value={itemCategoryId}
					>
						{#each categories as category}
							<option value={category.category_id}>{category.name}</option>
						{/each}
					</select>
				</label>

				<label class="mt-4 grid gap-2">
					<span class="text-sm font-medium text-slate-300">Planned amount</span>
					<input
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
						bind:value={plannedAmount}
						placeholder="8000"
					/>
				</label>

				<button
					class="mt-5 w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
					type="submit"
					disabled={selectedBudgetId === null || categories.length === 0}
				>
					Add budget item
				</button>
			</form>
		</div>

		<div class="flex flex-col gap-4">
			
			<div class="overflow-hidden rounded-2xl border border-slate-800/60 bg-slate-900/80">
				<div class="border-b border-slate-800/60 px-6 py-5">
					<p class="text-sm font-semibold text-slate-100">Budgets</p>
					<p class="mt-1 text-xs text-slate-500">
						Select a budget to view its items.
					</p>
				</div>

				{#if loading}
					<p class="px-6 py-12 text-center text-sm text-slate-600">Loading budgets...</p>
				{:else}
					<div class="divide-y divide-slate-800/60">
						{#each budgets as budget}
							<div
								class={`flex items-center justify-between gap-4 px-6 py-4 ${
									selectedBudgetId === budget.budget_id ? 'bg-slate-800/30' : ''
								}`}
							>
								<button
									class="text-left"
									type="button"
									onclick={() => selectBudget(budget.budget_id)}
								>
									<p class="font-medium text-slate-100">{budget.name}</p>
									<p class="mt-1 text-xs text-slate-400">
										{budget.period} · {formatDate(budget.start_date)} to {formatDate(budget.end_date)}
									</p>
								</button>

								<button
									class="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-950/40"
									type="button"
									onclick={() => removeBudget(budget)}
								>
									Delete
								</button>
							</div>
						{:else}
							<p class="px-6 py-12 text-center text-sm text-slate-600">No budgets yet.</p>
						{/each}
					</div>
				{/if}
			</div>

			<div class="overflow-hidden rounded-2xl border border-slate-800/60 bg-slate-900/80">
				<div class="border-b border-slate-800/60 px-6 py-5">
					<p class="text-sm font-semibold text-slate-100">
						{selectedBudget ? selectedBudget.name : 'Budget items'}
					</p>
					<p class="mt-1 text-xs text-slate-500">
						Planned category amounts.
					</p>
				</div>

				{#if selectedBudgetId === null}
					<p class="px-6 py-12 text-center text-sm text-slate-600">Select a budget first.</p>
				{:else if loadingItems}
					<p class="px-6 py-12 text-center text-sm text-slate-600">Loading budget items...</p>
				{:else}
					<div class="overflow-x-auto">
						<table class="w-full text-left text-sm">
							<thead class="text-[11px] font-bold uppercase tracking-widest text-slate-500">
								<tr>
									<th class="px-6 py-3">Category</th>
									<th class="px-6 py-3">Rollover</th>
									<th class="px-6 py-3 text-right">Planned</th>
									<th class="px-6 py-3 text-right">Actions</th>
								</tr>
							</thead>

							<tbody>
								{#each budgetItems as item}
									<tr class="border-t border-slate-800/60">
										<td class="px-6 py-4 font-medium text-slate-100">
											{categoryName(item.category_id)}
										</td>
										<td class="px-6 py-4 text-slate-300">
											{item.rollover_enabled ? 'Yes' : 'No'}
										</td>
										<td class="px-6 py-4 text-right font-semibold tabular-nums text-slate-100">
											{formatMoney(item.planned_amount_minor)}
										</td>
										<td class="px-6 py-4 text-right">
											<button
												class="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-950/40"
												type="button"
												onclick={() => removeBudgetItem(item)}
											>
												Delete
											</button>
										</td>
									</tr>
								{:else}
									<tr>
										<td class="px-6 py-12 text-center text-sm text-slate-600" colspan="4">
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
	</div>
</div>