<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import type { RecurringRule } from '$lib/api/recurring';
	import PageHeader from '$lib/shared/components/PageHeader.svelte';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
	import RecurringTable from './RecurringTable.svelte';
	import RecurringToolbar from './RecurringToolbar.svelte';

	let {
		recurringRules,
		archivedCount,
		showArchived,
		accounts,
		categories,
		categoryGroups,
		loading,
		error,
		notice,
		onAdd,
		onArchived,
		onPause,
		onResume,
		onGenerate,
		onEdit,
		onDeactivate,
		onDelete
	} = $props<{
		recurringRules: RecurringRule[];
		archivedCount: number;
		showArchived: boolean;
		accounts: Account[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		loading: boolean;
		error: string;
		notice: string;
		onAdd: () => void;
		onArchived: () => void;
		onPause: (rule: RecurringRule) => void | Promise<void>;
		onResume: (rule: RecurringRule) => void | Promise<void>;
		onGenerate: (rule: RecurringRule) => void | Promise<void>;
		onEdit: (rule: RecurringRule) => void;
		onDeactivate: (rule: RecurringRule) => void | Promise<void>;
		onDelete: (rule: RecurringRule) => void | Promise<void>;
	}>();

	let activeCount = $derived(recurringRules.filter((rule: RecurringRule) => rule.status === 'active').length);
	let pausedCount = $derived(recurringRules.filter((rule: RecurringRule) => rule.status === 'paused').length);
</script>

<ToastOnChange {error} {notice} />

<section class="budget-page flex min-h-screen flex-col">
	<PageHeader eyebrow="Schedule" title="Recurring" subtitle={showArchived ? `${archivedCount} archived` : `${activeCount} active · ${pausedCount} paused`}>
		<RecurringToolbar
			{archivedCount}
			{showArchived}
			onAdd={onAdd}
			onArchived={onArchived}
		/>
	</PageHeader>

	<div class="flex flex-col gap-5 p-5">
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
			onDeactivate={onDeactivate}
			onDelete={onDelete}
		/>
	</div>
</section>
