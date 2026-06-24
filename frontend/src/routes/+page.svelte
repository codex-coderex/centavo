<script lang="ts">
	import { onMount } from 'svelte';
	import { getBudgets, getBudgetItems, type Budget, type BudgetItem } from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';
	import { getAccounts, type Account } from '$lib/api/accounts';

	const USER_ID = 1;

	let loading = $state(true);
	let budget = $state<Budget | null>(null);
	let budgetItems = $state<BudgetItem[]>([]);
	let categories = $state<Category[]>([]);
	let categoryGroups = $state<CategoryGroup[]>([]);
	let transactions = $state<Transaction[]>([]);
	let accounts = $state<Account[]>([]);

	let categoryMap = $derived(Object.fromEntries(categories.map((c) => [c.category_id, c])));
	let groupMap = $derived(Object.fromEntries(categoryGroups.map((g) => [g.group_id, g])));

	let enrichedItems = $derived(
		budgetItems.map((item) => {
			const cat = categoryMap[item.category_id];
			const group = cat ? groupMap[cat.group_id] : null;
			const actual = transactions
				.filter((t) =>
					t.category_id === item.category_id &&
					t.transfer_pair_id == null &&
					budget &&
					t.txn_date >= budget.start_date &&
					(!budget.end_date || t.txn_date <= budget.end_date)
				)
				.reduce((sum, t) => sum + t.amount_minor, 0);
			return {
				...item,
				catName: cat?.name ?? 'Unknown',
				catColor: cat?.color ?? '#6366f1',
				groupName: group?.name ?? 'Other',
				groupType: group?.type ?? 'expense',
				actual_minor: actual,
			};
		})
	);

	let totalIncome = $derived(
		enrichedItems.filter((i) => i.groupType === 'income').reduce((s, i) => s + Math.abs(i.actual_minor), 0)
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

	const CHART_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316'];

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
			const [budgets, cats, groups, txns, accs] = await Promise.all([
				getBudgets(USER_ID),
				getAllCategories(USER_ID),
				getCategoryGroups(USER_ID),
				getTransactionsByUser(USER_ID),
				getAccounts(USER_ID),
			]);
			categories = cats;
			categoryGroups = groups;
			transactions = txns;
			accounts = accs;
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
</script>

{#if loading}
	<div class="flex h-screen items-center justify-center">
		<div class="flex flex-col items-center gap-3">
			<div class="h-6 w-6 animate-spin rounded-full border-2 border-slate-700 border-t-indigo-400"></div>
			<p class="text-xs uppercase tracking-widest text-slate-500">Loading</p>
		</div>
	</div>

{:else}
	<div class="flex flex-col gap-8 p-8">

		<!-- Header -->
		<div class="flex items-end justify-between">
			<div>
				<p class="text-xs font-bold uppercase tracking-widest text-slate-500">Overview</p>
				<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-50">
					{budget?.name ?? 'Dashboard'}
				</h1>
			</div>
			<p class="text-xs text-slate-500">
				{#if budget}
					{budget.start_date} — {budget.end_date ?? 'ongoing'}
				{:else}
					No active budget
				{/if}
			</p>
		</div>

		<!-- Stat row -->
		<div class="grid grid-cols-4 gap-3">
			<div class="col-span-1 rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950/60 to-slate-900 p-5">
				<p class="text-[11px] font-bold uppercase tracking-widest text-indigo-400">Remaining</p>
				<p class="mt-3 text-3xl font-bold tracking-tight {remaining < 0 ? 'text-red-400' : 'text-slate-50'}">{fmt(remaining)}</p>
				<div class="mt-3 flex gap-4 text-xs">
					<span class="text-emerald-400 font-medium">↑ {fmt(totalIncome)}</span>
					<span class="text-red-400 font-medium">↓ {fmt(totalSpent)}</span>
				</div>
			</div>
			<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-5">
				<p class="text-[11px] font-bold uppercase tracking-widest text-slate-500">Income</p>
				<p class="mt-3 text-2xl font-bold tracking-tight text-emerald-400">{fmt(totalIncome)}</p>
			</div>
			<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-5">
				<p class="text-[11px] font-bold uppercase tracking-widest text-slate-500">Expenses</p>
				<p class="mt-3 text-2xl font-bold tracking-tight text-red-400">{fmt(totalSpent)}</p>
			</div>
			<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-5">
				<p class="text-[11px] font-bold uppercase tracking-widest text-slate-500">Over Budget</p>
				<p class="mt-3 text-2xl font-bold tracking-tight {overBudget > 0 ? 'text-amber-400' : 'text-slate-50'}">{overBudget}</p>
				<p class="mt-1 text-xs text-slate-600">{overBudget === 1 ? 'category' : 'categories'}</p>
			</div>
		</div>

		<!-- Middle row -->
		<div class="grid grid-cols-2 gap-4">

			<!-- Donut -->
			<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-6">
				<div class="mb-5 flex items-center justify-between">
					<p class="text-sm font-semibold text-slate-100">Spending Breakdown</p>
					<a href="/budgets" class="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">View Budget →</a>
				</div>
				<div class="flex justify-center">
					<svg viewBox="0 0 140 140" width="180" height="180">
						{#if chartTotal === 0}
							<circle cx="70" cy="70" r="60" fill="none" stroke="#1e293b" stroke-width="16" />
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
						<text x="70" y="65" text-anchor="middle" fill="#64748b" font-size="9" font-family="inherit" font-weight="600" letter-spacing="1">SPENT</text>
						<text x="70" y="82" text-anchor="middle" fill="#f1f5f9" font-size="14" font-weight="700" font-family="inherit">
							{chartTotal > 0 ? `₱${(totalSpent / 100 / 1000).toFixed(1)}k` : '₱0'}
						</text>
					</svg>
				</div>
				{#if chartTotal === 0}
					<p class="mt-2 text-center text-xs text-slate-600">No spending recorded yet</p>
				{:else}
					<div class="mt-4 flex flex-col gap-2.5">
						{#each donutSegments as seg}
							<div class="flex items-center gap-3">
								<span class="h-2 w-2 flex-shrink-0 rounded-full" style="background:{seg.color}"></span>
								<span class="flex-1 text-xs font-medium text-slate-400">{seg.name}</span>
								<span class="text-xs font-bold text-slate-200">{fmt(seg.total)}</span>
								<span class="w-12 text-right text-xs text-slate-600">
									{chartTotal ? Math.round((seg.total / chartTotal) * 100) : 0}%
								</span>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Recent transactions -->
			<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-6">
				<div class="mb-5 flex items-center justify-between">
					<p class="text-sm font-semibold text-slate-100">Recent Transactions</p>
					<a href="/transactions" class="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">See all →</a>
				</div>
				{#if recentTxns.length === 0}
					<div class="flex flex-col items-center justify-center py-10 gap-2">
						<div class="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center">
							<span class="text-slate-600 text-lg">↕</span>
						</div>
						<p class="text-sm text-slate-600">No transactions yet</p>
					</div>
				{:else}
					<div class="flex flex-col divide-y divide-slate-800/60">
						{#each recentTxns as txn}
							{@const cat = categoryMap[txn.category_id]}
							<div class="flex items-center justify-between gap-4 py-3.5">
								<div class="min-w-0">
									<p class="truncate text-sm font-semibold text-slate-100">{txn.merchant ?? 'Unknown'}</p>
									<p class="mt-0.5 text-xs text-slate-500">
										{cat?.name ?? '—'}
										<span class="mx-1 text-slate-700">·</span>
										{txn.txn_date}
									</p>
								</div>
								<span class="flex-shrink-0 text-sm font-bold tabular-nums {txn.amount_minor >= 0 ? 'text-emerald-400' : 'text-red-400'}">
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
				<p class="text-sm font-semibold text-slate-100">Budget Categories</p>
				<a href="/budgets" class="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">Manage →</a>
			</div>
			{#if enrichedItems.length === 0}
				<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-10 text-center">
					<div class="mx-auto mb-3 h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center">
						<span class="text-slate-600 text-lg">◫</span>
					</div>
					<p class="text-sm text-slate-600">No budget categories yet</p>
					<a href="/budgets" class="mt-2 inline-block text-xs text-indigo-500 hover:text-indigo-400">Set up your budget →</a>
				</div>
			{:else}
				<div class="grid grid-cols-2 gap-4">
					{#each Object.entries(groupedItems) as [groupName, items]}
						<div class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-5">
							<p class="mb-4 text-[11px] font-bold uppercase tracking-widest text-slate-500">{groupName}</p>
							<div class="flex flex-col gap-4">
								{#each items as item}
									{@const p = pct(Math.abs(item.actual_minor), item.planned_amount_minor)}
									<div>
										<div class="mb-2 flex items-center justify-between">
											<span class="text-sm text-slate-300">{item.catName}</span>
											<span class="text-xs tabular-nums">
												<span class="{Math.abs(item.actual_minor) > item.planned_amount_minor ? 'font-bold text-red-400' : 'text-slate-400'}">{fmt(item.actual_minor)}</span>
												<span class="text-slate-700"> / </span>
												<span class="text-slate-600">{fmt(item.planned_amount_minor)}</span>
											</span>
										</div>
										<div class="h-1 overflow-hidden rounded-full bg-slate-800">
											<div
												class="h-full rounded-full transition-all duration-700 {p >= 100 ? 'bg-red-500' : p >= 85 ? 'bg-amber-500' : 'bg-indigo-500'}"
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