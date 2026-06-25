<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import PageHeader from '$lib/shared/components/PageHeader.svelte';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
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

<ToastOnChange {error} {notice} />

<section class="flex min-h-screen flex-col">
	<PageHeader eyebrow="Manage" title="Accounts" subtitle="Create and manage local accounts.">
		<AccountsToolbar
			archivedCount={archivedAccounts.length}
			onAdd={onAdd}
			onArchived={onArchived}
		/>
	</PageHeader>

	<div class="flex flex-col gap-5 p-5">
		<AccountsTable
			{accounts}
			{loading}
			onEdit={onEdit}
			onArchive={onArchive}
		/>
	</div>
</section>
