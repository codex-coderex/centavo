<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { Goal, GoalAccount } from '$lib/api/goals';
	import type { RecurringRule } from '$lib/api/recurring';
	import type { Transaction } from '$lib/api/transactions';
	import BudgetsPanel from './BudgetsPanel.svelte';
	import GoalsPanel from './GoalsPanel.svelte';
	import RecentTransactionsPanel from './RecentTransactionsPanel.svelte';
	import RecurringPanel from './RecurringPanel.svelte';
	import SpendingChart from './SpendingChart.svelte';
	import {
		availableBalance,
		budgetSummaries,
		formatMoney,
		spendingForPeriod,
		type DashboardPeriod
	} from '../utils/dashboardFormat';

	let {
		accounts,
		budgets,
		budgetItems,
		categories,
		categoryGroups,
		goals,
		goalAccounts,
		recurringRules,
		transactions,
		loading,
		error
	} = $props<{
		accounts: Account[];
		budgets: Budget[];
		budgetItems: BudgetItem[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		goals: Goal[];
		goalAccounts: GoalAccount[];
		recurringRules: RecurringRule[];
		transactions: Transaction[];
		loading: boolean;
		error: string;
	}>();

	let period: DashboardPeriod = $state('month');
	let summaries = $derived(budgetSummaries(budgets, budgetItems, transactions, categories, categoryGroups));
	let currentAvailable = $derived(availableBalance(accounts));
	let currentSpending = $derived(spendingForPeriod(transactions, period));
	let activeRecurringCount = $derived(recurringRules.filter((rule: RecurringRule) => rule.status === 'active').length);
</script>

{#if loading}
	<div class="flex h-screen items-center justify-center">
		<div class="flex flex-col items-center gap-3">
			<div class="h-6 w-6 animate-spin rounded-full border-2" style="border-color: var(--app-soft); border-top-color: var(--app-orange)"></div>
			<p class="dashboard-eyebrow text-xs uppercase tracking-widest">Loading dashboard</p>
		</div>
	</div>
{:else}
	<section class="dashboard-page flex flex-col gap-5 p-5">
		<div class="app-page-header flex flex-wrap items-end justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Overview</p>
				<h1 class="mt-1 text-3xl font-bold tracking-tight">Dashboard</h1>
				<p class="text-muted mt-2 text-sm">Spending, available cash, goals, recurring rules, transactions, and budgets in one place.</p>
			</div>
		</div>

		{#if error}
			<div class="rounded-2xl border p-4 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="grid gap-3 md:grid-cols-3">
			<div class="dashboard-card-primary p-5">
				<p class="dashboard-eyebrow text-[11px] font-bold uppercase tracking-widest">Available</p>
				<p class="money-positive mt-3 text-2xl font-bold tracking-tight">{formatMoney(currentAvailable)}</p>
				<p class="text-muted mt-1 text-xs">after goal allocations</p>
			</div>
			<div class="dashboard-card p-5">
				<p class="dashboard-eyebrow text-[11px] font-bold uppercase tracking-widest">Spending</p>
				<p class="money-negative mt-3 text-2xl font-bold tracking-tight">{formatMoney(currentSpending)}</p>
			</div>
			<div class="dashboard-card p-5">
				<p class="dashboard-eyebrow text-[11px] font-bold uppercase tracking-widest">Recurring</p>
				<p class="mt-3 text-2xl font-bold tracking-tight">{activeRecurringCount}</p>
				<p class="text-muted mt-1 text-xs">active rules</p>
			</div>
		</div>

		<div class="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.85fr)]">
			<div class="grid gap-5">
				<SpendingChart {transactions} bind:period />
				<BudgetsPanel budgets={summaries} />
			</div>

			<div class="grid content-start gap-5">
				<GoalsPanel {goals} {goalAccounts} {accounts} />
				<RecentTransactionsPanel {transactions} {categories} {categoryGroups} />
				<RecurringPanel {recurringRules} {accounts} {categories} />
			</div>
		</div>
	</section>
{/if}
