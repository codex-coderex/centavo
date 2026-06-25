<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { RecurringRule } from '$lib/api/recurring';
	import { formatDate, formatMoney, frequencyLabel } from '../utils/recurringFormat';

	let {
		recurringRules,
		accounts,
		categories,
		categoryGroups,
		loading,
		onPause,
		onResume,
		onGenerate,
		onEdit,
		onDeactivate,
		onDelete
	} = $props<{
		recurringRules: RecurringRule[];
		accounts: Account[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		loading: boolean;
		onPause: (rule: RecurringRule) => void | Promise<void>;
		onResume: (rule: RecurringRule) => void | Promise<void>;
		onGenerate: (rule: RecurringRule) => void | Promise<void>;
		onEdit: (rule: RecurringRule) => void;
		onDeactivate: (rule: RecurringRule) => void | Promise<void>;
		onDelete: (rule: RecurringRule) => void | Promise<void>;
	}>();

	function accountName(accountId: number) {
		return accounts.find((account: Account) => account.account_id === accountId)?.name ?? `Account ${accountId}`;
	}

	function categoryFor(categoryId: number) {
		return categories.find((category: Category) => category.category_id === categoryId);
	}

	function categoryName(categoryId: number) {
		return categoryFor(categoryId)?.name ?? `Category ${categoryId}`;
	}

	function categoryGroup(categoryId: number) {
		const category = categoryFor(categoryId);
		return categoryGroups.find((group: CategoryGroup) => group.group_id === category?.group_id);
	}

	function categoryPillClass(categoryId: number) {
		const type = categoryGroup(categoryId)?.type;

		if (type === 'income') return 'bg-emerald-100 text-emerald-700';
		return 'bg-(--app-soft) text-(--app-primary)';
	}

	type SortKey = 'name' | 'category' | 'account' | 'frequency' | 'next_due_date' | 'status' | 'amount' | 'created';
	let sortKey: SortKey = $state('created');
	let sortDirection: 'asc' | 'desc' = $state('desc');

	function sortValue(rule: RecurringRule, key: SortKey) {
		if (key === 'name') return rule.name.toLowerCase();
		if (key === 'category') return categoryName(rule.category_id).toLowerCase();
		if (key === 'account') return accountName(rule.account_id).toLowerCase();
		if (key === 'frequency') return `${rule.frequency_unit}-${rule.interval}`;
		if (key === 'next_due_date') return rule.next_due_date;
		if (key === 'status') return rule.status;
		if (key === 'amount') return rule.expected_amount_minor;
		return rule.recurring_rule_id;
	}

	function setSort(key: SortKey) {
		if (sortKey === key) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortKey = key;
			sortDirection = key === 'amount' || key === 'created' ? 'desc' : 'asc';
		}
	}

	function sortMark(key: SortKey) {
		if (sortKey !== key) return '↕';
		return sortDirection === 'asc' ? '↑' : '↓';
	}

	let sortedRules = $derived(
		[...recurringRules].sort((a: RecurringRule, b: RecurringRule) => {
			const left = sortValue(a, sortKey);
			const right = sortValue(b, sortKey);
			const result = typeof left === 'number' && typeof right === 'number'
				? left - right
				: String(left).localeCompare(String(right));

			return sortDirection === 'asc' ? result : -result;
		})
	);
</script>

<div class="overflow-hidden rounded-2xl border bg-(--app-surface)" style="border-color: var(--app-border); box-shadow: var(--shadow-soft)">
	{#if loading}
		<p class="text-muted px-6 py-12 text-center text-sm">Loading recurring rules...</p>
	{:else if recurringRules.length === 0}
		<p class="text-muted px-6 py-12 text-center text-sm">No recurring rules yet.</p>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full min-w-[980px] border-collapse text-left text-sm">
				<thead>
					<tr class="border-b text-xs font-bold uppercase tracking-widest text-muted" style="border-color: var(--app-border)">
						<th class="px-5 py-4"><button class="sortable-header" type="button" onclick={() => setSort('name')}>Merchant {sortMark('name')}</button></th>
						<th class="px-5 py-4"><button class="sortable-header" type="button" onclick={() => setSort('category')}>Category {sortMark('category')}</button></th>
						<th class="px-5 py-4"><button class="sortable-header" type="button" onclick={() => setSort('account')}>Account {sortMark('account')}</button></th>
						<th class="px-5 py-4"><button class="sortable-header" type="button" onclick={() => setSort('frequency')}>Frequency {sortMark('frequency')}</button></th>
						<th class="px-5 py-4"><button class="sortable-header" type="button" onclick={() => setSort('next_due_date')}>Next Due {sortMark('next_due_date')}</button></th>
						<th class="px-5 py-4"><button class="sortable-header" type="button" onclick={() => setSort('status')}>Status {sortMark('status')}</button></th>
						<th class="px-5 py-4 text-right"><button class="sortable-header ml-auto" type="button" onclick={() => setSort('amount')}>Amount {sortMark('amount')}</button></th>
						<th class="px-5 py-4 text-right">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each sortedRules as rule}
						<tr>
							<td class="px-5 py-4 font-semibold">
								{rule.name || 'Recurring item'}
							</td>
							<td class="px-5 py-4">
								<span class={`rounded-full px-2 py-1 text-xs font-medium ${categoryPillClass(rule.category_id)}`}>
									{categoryName(rule.category_id)}
								</span>
							</td>
							<td class="px-5 py-4 text-muted">{accountName(rule.account_id)}</td>
							<td class="px-5 py-4">{frequencyLabel(rule.interval, rule.frequency_unit)}</td>
							<td class="px-5 py-4">
								<p>{formatDate(rule.next_due_date)}</p>
								{#if rule.end_date}
									<p class="text-muted text-xs">until {formatDate(rule.end_date)}</p>
								{/if}
							</td>
							<td class="px-5 py-4">
								<span class={rule.status === 'paused'
									? 'rounded-full bg-amber-100 px-2 py-1 text-xs font-medium text-amber-700'
									: rule.status === 'active'
										? 'rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700'
										: 'rounded-full bg-(--app-soft) px-2 py-1 text-xs font-medium text-muted'}>
									{rule.status[0].toUpperCase() + rule.status.slice(1)}
								</span>
							</td>
							<td class={`px-5 py-4 text-right font-semibold ${rule.expected_amount_minor < 0 ? 'money-negative' : 'money-positive'}`}>
								{formatMoney(rule.expected_amount_minor)}
							</td>
							<td class="px-5 py-4">
								<div class="flex items-center justify-end gap-4">
									{#if rule.status === 'active'}
										<button class="transaction-row-action" type="button" onclick={() => onPause(rule)}>Pause</button>
										<button class="transaction-row-action" type="button" onclick={() => onGenerate(rule)}>Generate Now</button>
										<button class="transaction-row-action danger" type="button" onclick={() => onDeactivate(rule)}>Deactivate</button>
									{:else if rule.status === 'paused'}
										<button class="transaction-row-action" type="button" onclick={() => onResume(rule)}>Resume</button>
										<button class="transaction-row-action danger" type="button" onclick={() => onDeactivate(rule)}>Deactivate</button>
									{:else}
										<button class="transaction-row-action danger" type="button" onclick={() => onDelete(rule)}>Delete</button>
									{/if}
									{#if rule.status !== 'inactive'}
										<button class="transaction-row-action" type="button" onclick={() => onEdit(rule)}>Edit</button>
									{/if}
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
