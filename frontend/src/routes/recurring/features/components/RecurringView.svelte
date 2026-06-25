<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { RecurringRule } from '$lib/api/recurring';
	import RecurringTable from './RecurringTable.svelte';
	import RecurringToolbar from './RecurringToolbar.svelte';

	let {
		recurringRules,
		accounts,
		categories,
		categoryGroups,
		loading,
		error,
		notice,
		onAdd,
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
		error: string;
		notice: string;
		onAdd: () => void;
		onPause: (rule: RecurringRule) => void | Promise<void>;
		onResume: (rule: RecurringRule) => void | Promise<void>;
		onGenerate: (rule: RecurringRule) => void | Promise<void>;
		onEdit: (rule: RecurringRule) => void;
	}>();

	let activeCount = $derived(recurringRules.filter((rule: RecurringRule) => rule.status === 'active').length);
	let pausedCount = $derived(recurringRules.filter((rule: RecurringRule) => rule.status === 'paused').length);
</script>

<section class="budget-page flex min-h-screen flex-col gap-5 px-5 py-4">
	<div class="app-page-header flex flex-wrap items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight">Recurring</h1>
			<p class="text-muted mt-1 text-sm">{activeCount} active · {pausedCount} paused</p>
		</div>

		<RecurringToolbar onAdd={onAdd} />
	</div>

	{#if error}
		<div class="rounded-2xl border p-4 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="rounded-2xl border p-4 text-sm money-positive" style="border-color: rgba(47, 143, 107, 0.3); background: rgba(47, 143, 107, 0.08)">
			{notice}
		</div>
	{/if}

	<RecurringTable
		{recurringRules}
		{accounts}
		{categories}
		{categoryGroups}
		{loading}
		onPause={onPause}
		onResume={onResume}
		onGenerate={onGenerate}
		onEdit={onEdit}
	/>
</section>
