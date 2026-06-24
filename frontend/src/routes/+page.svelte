<script lang="ts">
	import { onMount } from 'svelte';
	import { getBudgets, getBudgetItems, type Budget, type BudgetItem } from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';

	const USER_ID = 1;

	let loading = $state(true);
	let budget = $state<Budget | null>(null);
	let budgetItems = $state<BudgetItem[]>([]);
	let categories = $state<Category[]>([]);
	let categoryGroups = $state<CategoryGroup[]>([]);
	let transactions = $state<Transaction[]>([]);

	let categoryMap = $derived(Object.fromEntries(categories.map((c) => [c.category_id, c])));
	let groupMap = $derived(Object.fromEntries(categoryGroups.map((g) => [g.group_id, g])));

	let enrichedItems = $derived(
		budgetItems.map((item) => {
			const cat = categoryMap[item.category_id];
			const group = cat ? groupMap[cat.group_id] : null;
			const actual = transactions
				.filter((t) =>
					t.category_id === item.category_id &&
					t.transfer_id == null &&
					budget &&
					t.transaction_date >= budget.start_date &&
					(!budget.end_date || t.transaction_date <= budget.end_date)
				)
				.reduce((sum, t) => sum + t.amount_minor, 0);
			return {
				...item,
				catName: cat?.name ?? 'Unknown',
				groupName: group?.name ?? 'Other',
				groupType: group?.type ?? 'expense',
				actual_minor: actual,
			};
		})
	);

	let totalIncome = $derived(
		transactions
			.filter((t) => t.transfer_id == null && t.amount_minor > 0)
			.reduce((s, t) => s + t.amount_minor, 0)
	);
	let totalSpent = $derived(
		enrichedItems.filter((i) => i.groupType !== 'income').reduce((s, i) => s + Math.abs(i.actual_minor), 0)
	);
	let remaining = $derived(totalIncome - totalSpent);
	let overBudget = $derived(enrichedItems.filter((i) => Math.abs(i.actual_minor) > i.planned_amount_minor).length);
	let recentTxns = $derived(transactions.slice(0, 5));

	let spendingGroups = $derived(
		Object.entries(
			enrichedItems
				.filter((i) => i.groupType !== 'income')
				.reduce((acc, item) => {
					acc[item.groupName] = (acc[item.groupName] ?? 0) + Math.abs(item.actual_minor);
					return acc;
				}, {} as Record<string, number>)
		).filter(([, v]) => v > 0)
	);

	let chartTotal = $derived(spendingGroups.reduce((s, [, v]) => s + v, 0));

	const CHART_COLORS = ['#2f8f6b', '#5d4b8c', '#c58b35', '#bd4a3f', '#6f8f72', '#3f7f91', '#9b6a40'];

	let donutSegments = $derived((() => {
		const r = 60; const circ = 2 * Math.PI * r;
		let offset = 0;
		return spendingGroups.map(([name, total], i) => {
			const dash = chartTotal ? (total / chartTotal) * circ : 0;
			const seg = { name, total, dash, offset, color: CHART_COLORS[i % CHART_COLORS.length] };
			offset += dash;
			return seg;
		});
	})());

	let groupedItems = $derived(
		enrichedItems.reduce((acc, item) => {
			if (!acc[item.groupName]) acc[item.groupName] = [];
			acc[item.groupName].push(item);
			return acc;
		}, {} as Record<string, typeof enrichedItems>)
	);

	onMount(async () => {
		try {
			const [budgets, cats, groups, txns] = await Promise.all([
				getBudgets(USER_ID),
				getAllCategories(USER_ID),
				getCategoryGroups(USER_ID),
				getTransactionsByUser(USER_ID),
			]);
			categories = cats;
			categoryGroups = groups;
			transactions = txns;
			if (budgets.length > 0) {
				budget = budgets[0];
				budgetItems = await getBudgetItems(budget.budget_id);
			}
		} catch (err) {
			console.error(err);
		} finally {
			loading = false;
		}
	});

	function fmt(minor: number) {
		return '₱' + (Math.abs(minor) / 100).toLocaleString('en-PH', { minimumFractionDigits: 2 });
	}
	function fmtSigned(minor: number) {
		return (minor >= 0 ? '+' : '−') + '₱' + (Math.abs(minor) / 100).toLocaleString('en-PH', { minimumFractionDigits: 2 });
	}
	function pct(actual: number, planned: number) {
		if (!planned) return 0;
		return Math.min((actual / planned) * 100, 100);
	}
	function fmtDate(value?: string | null) {
		if (!value) return 'ongoing';
		return new Date(value).toLocaleDateString('en-PH', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
		});
	}
</script>

{#if loading}
	<div class="flex h-screen items-center justify-center">
		<div class="flex flex-col items-center gap-3">
			<div class="h-6 w-6 animate-spin rounded-full border-2" style="border-color: var(--app-soft); border-top-color: var(--app-green)"></div>
			<p class="dashboard-eyebrow text-xs uppercase tracking-widest">Loading</p>
		</div>
	</div>

{:else}
	<div class="dashboard-page flex flex-col gap-8 p-8">

		<!-- Header -->
		<div class="flex items-end justify-between">
			<div>
				<p class="dashboard-eyebrow text-xs font-bold uppercase tracking-widest">Overview</p>
				<h1 class="mt-1 text-3xl font-bold tracking-tight">
					{budget?.name ?? 'Dashboard'}
				</h1>
			</div>
			<p class="text-muted text-xs">
				{#if budget}
					{fmtDate(budget.start_date)} — {fmtDate(budget.end_date)}
				{:else}
					No active budget
				{/if}
			</p>
		</div>

		<!-- Stat row -->
		<div class="grid grid-cols-4 gap-3">
			<div class="dashboard-card-primary col-span-1 p-5">
				<p class="text-[11px] font-bold uppercase tracking-widest" style="color: var(--app-green)">Remaining</p>
				<p class="mt-3 text-3xl font-bold tracking-tight {remaining < 0 ? 'money-negative' : ''}">{fmt(remaining)}</p>
				<div class="mt-3 flex gap-4 text-xs">
					<span class="money-positive font-medium">↑ {fmt(totalIncome)}</span>
					<span class="money-negative font-medium">↓ {fmt(totalSpent)}</span>
				</div>
			</div>
			<div class="dashboard-card p-5">
				<p class="dashboard-eyebrow text-[11px] font-bold uppercase tracking-widest">Income</p>
				<p class="money-positive mt-3 text-2xl font-bold tracking-tight">{fmt(totalIncome)}</p>
			</div>
			<div class="dashboard-card p-5">
				<p class="dashboard-eyebrow text-[11px] font-bold uppercase tracking-widest">Expenses</p>
				<p class="money-negative mt-3 text-2xl font-bold tracking-tight">{fmt(totalSpent)}</p>
			</div>
			<div class="dashboard-card p-5">
				<p class="dashboard-eyebrow text-[11px] font-bold uppercase tracking-widest">Over Budget</p>
				<p class="mt-3 text-2xl font-bold tracking-tight {overBudget > 0 ? 'money-warn' : ''}">{overBudget}</p>
				<p class="text-muted mt-1 text-xs">{overBudget === 1 ? 'category' : 'categories'}</p>
			</div>
		</div>

		<!-- Middle row -->
		<div class="grid grid-cols-2 gap-4">

			<!-- Donut -->
			<div class="dashboard-card p-6">
				<div class="mb-5 flex items-center justify-between">
					<p class="text-sm font-semibold">Spending Breakdown</p>
					<a href="/budgets" class="dashboard-link text-xs">View Budget →</a>
				</div>
				<div class="flex justify-center">
					<svg viewBox="0 0 140 140" width="180" height="180">
						{#if chartTotal === 0}
							<circle cx="70" cy="70" r="60" fill="none" stroke="#efe5d8" stroke-width="16" />
						{:else}
							{#each donutSegments as seg}
								<circle
									cx="70" cy="70" r="60"
									fill="none"
									stroke={seg.color}
									stroke-width="16"
									stroke-dasharray="{seg.dash} {2 * Math.PI * 60 - seg.dash}"
									stroke-dashoffset={-(seg.offset - 2 * Math.PI * 60 * 0.25)}
								/>
							{/each}
						{/if}
						<text x="70" y="65" text-anchor="middle" fill="#7e7265" font-size="9" font-family="inherit" font-weight="600" letter-spacing="1">SPENT</text>
						<text x="70" y="82" text-anchor="middle" fill="#2f2a24" font-size="14" font-weight="700" font-family="inherit">
							{chartTotal > 0 ? `₱${(totalSpent / 100 / 1000).toFixed(1)}k` : '₱0'}
						</text>
					</svg>
				</div>
				{#if chartTotal === 0}
					<p class="text-muted mt-2 text-center text-xs">No spending recorded yet</p>
				{:else}
					<div class="mt-4 flex flex-col gap-2.5">
						{#each donutSegments as seg}
							<div class="flex items-center gap-3">
								<span class="h-2 w-2 shrink-0 rounded-full" style="background:{seg.color}"></span>
								<span class="text-muted flex-1 text-xs font-medium">{seg.name}</span>
								<span class="text-xs font-bold">{fmt(seg.total)}</span>
								<span class="text-muted w-12 text-right text-xs">
									{chartTotal ? Math.round((seg.total / chartTotal) * 100) : 0}%
								</span>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Recent transactions -->
			<div class="dashboard-card p-6">
				<div class="mb-5 flex items-center justify-between">
					<p class="text-sm font-semibold">Recent Transactions</p>
					<a href="/transactions" class="dashboard-link text-xs">See all →</a>
				</div>
				{#if recentTxns.length === 0}
					<div class="flex flex-col items-center justify-center py-10 gap-2">
						<div class="flex h-10 w-10 items-center justify-center rounded-full" style="background: var(--app-soft)">
							<span class="text-muted text-lg">↕</span>
						</div>
						<p class="text-muted text-sm">No transactions yet</p>
					</div>
				{:else}
					<div class="flex flex-col divide-y" style="border-color: var(--app-border)">
						{#each recentTxns as txn}
							{@const cat = categoryMap[txn.category_id]}
							<div class="flex items-center justify-between gap-4 py-3.5">
								<div class="min-w-0">
									<p class="truncate text-sm font-semibold">{txn.payee ?? 'Unknown'}</p>
									<p class="text-muted mt-0.5 text-xs">
										{cat?.name ?? '—'}
										<span class="mx-1">·</span>
										{fmtDate(txn.transaction_date)}
									</p>
								</div>
								<span class="shrink-0 text-sm font-bold tabular-nums {txn.amount_minor >= 0 ? 'money-positive' : 'money-negative'}">
									{fmtSigned(txn.amount_minor)}
								</span>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Budget categories -->
		<div>
			<div class="mb-4 flex items-center justify-between">
				<p class="text-sm font-semibold">Budget Categories</p>
				<a href="/budgets" class="dashboard-link text-xs">Manage →</a>
			</div>
			{#if enrichedItems.length === 0}
				<div class="dashboard-card p-10 text-center">
					<div class="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full" style="background: var(--app-soft)">
						<span class="text-muted text-lg">◫</span>
					</div>
					<p class="text-muted text-sm">No budget categories yet</p>
					<a href="/budgets" class="dashboard-link mt-2 inline-block text-xs">Set up your budget →</a>
				</div>
			{:else}
				<div class="grid grid-cols-2 gap-4">
					{#each Object.entries(groupedItems) as [groupName, items]}
						<div class="dashboard-card p-5">
							<p class="dashboard-eyebrow mb-4 text-[11px] font-bold uppercase tracking-widest">{groupName}</p>
							<div class="flex flex-col gap-4">
								{#each items as item}
									{@const p = pct(Math.abs(item.actual_minor), item.planned_amount_minor)}
									<div>
										<div class="mb-2 flex items-center justify-between">
											<span class="text-sm">{item.catName}</span>
											<span class="text-xs tabular-nums">
												<span class="{Math.abs(item.actual_minor) > item.planned_amount_minor ? 'money-negative font-bold' : 'text-muted'}">{fmt(item.actual_minor)}</span>
												<span class="text-muted"> / </span>
												<span class="text-muted">{fmt(item.planned_amount_minor)}</span>
											</span>
										</div>
										<div class="h-1 overflow-hidden rounded-full" style="background: var(--app-soft)">
											<div
												class="h-full rounded-full transition-all duration-700 {p >= 100 ? 'bg-(--app-red)' : p >= 85 ? 'bg-(--app-gold)' : 'bg-(--app-green)'}"
												style="width:{p}%"
											></div>
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

	</div>
{/if}
