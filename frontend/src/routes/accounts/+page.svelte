<script lang="ts">
	import { onMount } from 'svelte';
	import {
		archiveAccount,
		createAccount,
		getAccounts,
		updateAccount,
		type Account,
		type AccountType
	} from '$lib/api/accounts';
	import AccountsView from './features/components/AccountsView.svelte';
	import AccountModal from './features/modals/AccountModal.svelte';
	import ArchivedAccountsModal from './features/modals/ArchivedAccountsModal.svelte';
	import EditAccountModal from './features/modals/EditAccountModal.svelte';
	import {
		accountBalance,
		accountTypes,
		formatBalance,
		openingBalanceForCurrentBalance,
		typeLabel
	} from './features/utils/accountFormat';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let archivedAccounts: Account[] = $state([]);
	let editingAccount: Account | null = $state(null);
	let loading = $state(true);
	let saving = $state(false);
	let restoringId: number | null = $state(null);
	let error = $state('');
	let modalError = $state('');
	let editModalError = $state('');
	let archivedModalError = $state('');
	let notice = $state('');
	let showAccountModal = $state(false);
	let showEditModal = $state(false);
	let showArchivedModal = $state(false);
	let editReturnToArchived = $state(false);

	let name = $state('');
	let type: AccountType = $state('checking');
	let openingBalance = $state('');
	let editName = $state('');
	let editBalance = $state('');

	async function loadAccounts() {
		loading = true;
		error = '';

		try {
			const [activeRows, allRows] = await Promise.all([
				getAccounts(userId),
				getAccounts(userId, false)
			]);

			accounts = activeRows;
			archivedAccounts = allRows.filter((account: Account) => account.status === 'archived');
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function resetAccountModal() {
		name = '';
		type = 'checking';
		openingBalance = '';
		modalError = '';
	}

	function openAccountModal() {
		error = '';
		notice = '';
		resetAccountModal();
		showAccountModal = true;
	}

	function closeAccountModal() {
		showAccountModal = false;
		modalError = '';
		saving = false;
	}

	function openEditModal(account: Account, returnToArchived = false) {
		error = '';
		notice = '';
		editModalError = '';
		editReturnToArchived = returnToArchived;
		editingAccount = account;
		editName = account.name;
		editBalance = (accountBalance(account) / 100).toFixed(2);
		showArchivedModal = false;
		showEditModal = true;
	}

	function closeEditModal() {
		showEditModal = false;
		editModalError = '';
		editingAccount = null;
		saving = false;

		if (editReturnToArchived) {
			showArchivedModal = true;
			editReturnToArchived = false;
		}
	}

	function openArchivedModal() {
		archivedModalError = '';
		showArchivedModal = true;
	}

	function closeArchivedModal() {
		showArchivedModal = false;
		archivedModalError = '';
		restoringId = null;
	}

	async function submitAccount() {
		modalError = '';
		notice = '';

		if (!name.trim()) {
			modalError = 'Account name is required.';
			return;
		}

		saving = true;

		try {
			await createAccount({
				user_id: userId,
				name: name.trim(),
				type,
				opening_balance: openingBalance || 0
			});

			notice = 'Account created.';
			closeAccountModal();
			await loadAccounts();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function submitEditAccount() {
		editModalError = '';
		notice = '';

		if (editingAccount === null) {
			editModalError = 'Account does not exist.';
			return;
		}

		if (!editName.trim()) {
			editModalError = 'Account name is required.';
			return;
		}

		saving = true;

		try {
			await updateAccount(editingAccount.account_id, {
				name: editName.trim(),
				opening_balance: openingBalanceForCurrentBalance(editingAccount, editBalance)
			});

			notice = 'Account updated.';
			closeEditModal();
			await loadAccounts();
		} catch (err) {
			editModalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function archive(account: Account) {
		const confirmed = confirm(`Archive "${account.name}"?`);

		if (!confirmed) return;

		error = '';
		notice = '';

		try {
			await archiveAccount(account.account_id);
			notice = 'Account archived.';
			await loadAccounts();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function restore(account: Account) {
		archivedModalError = '';
		notice = '';
		restoringId = account.account_id;

		try {
			await updateAccount(account.account_id, { status: 'active' });
			notice = 'Account enabled.';
			await loadAccounts();
		} catch (err) {
			archivedModalError = err instanceof Error ? err.message : String(err);
		} finally {
			restoringId = null;
		}
	}

	onMount(loadAccounts);
</script>

<AccountsView
	{accounts}
	{archivedAccounts}
	{loading}
	{error}
	{notice}
	onAdd={openAccountModal}
	onArchived={openArchivedModal}
	onEdit={openEditModal}
	onArchive={archive}
/>

{#if showAccountModal}
	<AccountModal
		bind:name
		bind:type
		bind:openingBalance
		{accountTypes}
		error={modalError}
		{saving}
		onClose={closeAccountModal}
		onSubmit={submitAccount}
	/>
{/if}

{#if showEditModal && editingAccount}
	<EditAccountModal
		account={editingAccount}
		bind:name={editName}
		bind:balance={editBalance}
		error={editModalError}
		{saving}
		fmtBalance={formatBalance}
		{accountBalance}
		onClose={closeEditModal}
		onSubmit={submitEditAccount}
	/>
{/if}

{#if showArchivedModal}
	<ArchivedAccountsModal
		accounts={archivedAccounts}
		error={archivedModalError}
		{restoringId}
		{typeLabel}
		fmtBalance={formatBalance}
		{accountBalance}
		onClose={closeArchivedModal}
		onEdit={(account) => openEditModal(account, true)}
		onRestore={restore}
	/>
{/if}
