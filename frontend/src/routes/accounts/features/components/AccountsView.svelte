<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import AccountsTable from './AccountsTable.svelte';
	import AccountsToolbar from './AccountsToolbar.svelte';

	let {
		accounts,
		archivedAccounts,
		loading,
		error,
		notice,
		onAdd,
		onArchived,
		onEdit,
		onArchive
	} = $props<{
		accounts: Account[];
		archivedAccounts: Account[];
		loading: boolean;
		error: string;
		notice: string;
		onAdd: () => void;
		onArchived: () => void;
		onEdit: (account: Account) => void;
		onArchive: (account: Account) => void | Promise<void>;
	}>();
</script>

<section class="flex flex-col gap-8 p-8">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Manage</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight">Accounts</h1>
			<p class="text-muted mt-2 text-sm">Create and manage local accounts.</p>
		</div>

		<AccountsToolbar
			archivedCount={archivedAccounts.length}
			onAdd={onAdd}
			onArchived={onArchived}
		/>
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

	<AccountsTable
		{accounts}
		{loading}
		onEdit={onEdit}
		onArchive={onArchive}
	/>
</section>
