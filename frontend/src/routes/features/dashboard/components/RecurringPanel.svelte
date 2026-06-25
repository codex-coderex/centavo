<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category } from '$lib/api/categories';
	import type { RecurringRule } from '$lib/api/recurring';
	import { accountName, categoryName, formatDate, formatMoney, upcomingRecurring } from '../utils/dashboardFormat';

	let {
		recurringRules,
		accounts,
		categories
	} = $props<{
		recurringRules: RecurringRule[];
		accounts: Account[];
		categories: Category[];
	}>();

	let upcoming = $derived(upcomingRecurring(recurringRules));
</script>

<div class="dashboard-card p-5">
	<div class="flex items-start justify-between gap-4">
		<div>
			<h2 class="text-lg font-semibold">Recurring</h2>
			<p class="text-muted mt-1 text-sm">Upcoming active and paused rules.</p>
		</div>
		<a class="dashboard-link text-xs" href="/recurring">Manage</a>
	</div>

	<div class="mt-5 grid gap-3">
		{#each upcoming as rule}
			<div class="flex items-center justify-between gap-4 rounded-xl border p-3" style="border-color: var(--app-border); background: var(--app-surface-strong)">
				<div class="min-w-0">
					<div class="flex items-center gap-2">
						<p class="truncate text-sm font-semibold">{rule.name}</p>
						<span class={rule.status === 'paused' ? 'pill muted-pill' : 'pill'}>{rule.status}</span>
					</div>
					<p class="text-muted mt-1 truncate text-xs">
						{accountName(accounts, rule.account_id)} · {categoryName(categories, rule.category_id)} · due {formatDate(rule.next_due_date)}
					</p>
				</div>
				<p class={`shrink-0 text-sm font-bold ${rule.expected_amount_minor < 0 ? 'money-negative' : 'money-positive'}`}>
					{formatMoney(rule.expected_amount_minor)}
				</p>
			</div>
		{:else}
			<p class="text-muted py-6 text-center text-sm">No recurring rules yet.</p>
		{/each}
	</div>
</div>
