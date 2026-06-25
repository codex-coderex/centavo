<script lang="ts">
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { Transaction } from '$lib/api/transactions';
	import { categoryGroupName, categoryName, formatDate, formatSignedMoney } from '../utils/dashboardFormat';

	let {
		transactions,
		categories,
		categoryGroups
	} = $props<{
		transactions: Transaction[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
	}>();

	let recentTransactions = $derived(transactions.slice(0, 6));
</script>

<div class="dashboard-card p-5">
	<div class="flex items-start justify-between gap-4">
		<div>
			<h2 class="text-lg font-semibold">Recent Transactions</h2>
			<p class="text-muted mt-1 text-sm">Latest account activity.</p>
		</div>
		<a class="dashboard-link text-xs" href="/transactions">All transactions</a>
	</div>

	<div class="mt-5 divide-y" style="border-color: var(--app-border)">
		{#each recentTransactions as transaction}
			<div class="flex items-center justify-between gap-4 py-3">
				<div class="min-w-0">
					<p class="truncate text-sm font-semibold">{transaction.payee ?? 'No payee'}</p>
					<p class="text-muted mt-1 truncate text-xs">
						{categoryName(categories, transaction.category_id)} · {categoryGroupName(categories, categoryGroups, transaction.category_id)} · {formatDate(transaction.transaction_date)}
					</p>
				</div>
				<p class={`shrink-0 text-sm font-bold tabular-nums ${transaction.amount_minor >= 0 ? 'money-positive' : 'money-negative'}`}>
					{formatSignedMoney(transaction.amount_minor)}
				</p>
			</div>
		{:else}
			<p class="text-muted py-8 text-center text-sm">No transactions yet.</p>
		{/each}
	</div>
</div>
