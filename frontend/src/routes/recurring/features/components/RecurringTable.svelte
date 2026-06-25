<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { RecurringRule } from '$lib/api/recurring';
	import { formatDate, formatMoney, frequencyLabel, isRuleDue } from '../utils/recurringFormat';

	let {
		recurringRules,
		accounts,
		categories,
		categoryGroups,
		loading,
		onPause,
		onResume,
		onGenerate,
		onEdit
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
						<th class="px-5 py-4">Merchant</th>
						<th class="px-5 py-4">Category</th>
						<th class="px-5 py-4">Account</th>
						<th class="px-5 py-4">Frequency</th>
						<th class="px-5 py-4">Next Due</th>
						<th class="px-5 py-4">Status</th>
						<th class="px-5 py-4 text-right">Amount</th>
						<th class="px-5 py-4 text-right">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each recurringRules as rule}
						<tr class={isRuleDue(rule) ? 'bg-blue-50/70' : ''}>
							<td class="px-5 py-4 font-semibold">
								<div class="flex items-center gap-2">
									<span>{rule.name || 'Recurring item'}</span>
									{#if isRuleDue(rule)}
										<span class="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-bold uppercase text-blue-700">Due</span>
									{/if}
								</div>
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
									{:else if rule.status === 'paused'}
										<button class="transaction-row-action" type="button" onclick={() => onResume(rule)}>Resume</button>
									{/if}
									<button class="transaction-row-action" type="button" onclick={() => onEdit(rule)}>Edit</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
