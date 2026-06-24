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
	import AccountModal, { type AccountTypeOption } from './AccountModal.svelte';
	import ArchivedAccountsModal from './ArchivedAccountsModal.svelte';
	import EditAccountModal from './EditAccountModal.svelte';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let archivedAccounts: Account[] = $state([]);
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
	let editingAccount: Account | null = $state(null);

	let name = $state('');
	let type: AccountType = $state('checking');
	let openingBalance = $state('');
	let editName = $state('');
	let editBalance = $state('');

	const accountTypes: AccountTypeOption[] = [
		{ value: 'checking', label: 'Checking' },
		{ value: 'savings', label: 'Savings' },
		{ value: 'cash', label: 'Cash' },
		{ value: 'credit_card', label: 'Credit Card' },
		{ value: 'line_of_credit', label: 'Line of Credit' },
		{ value: 'loan', label: 'Loan' },
		{ value: 'mortgage', label: 'Mortgage' },
		{ value: 'investment', label: 'Investment' },
		{ value: 'other_asset', label: 'Other Asset' },
		{ value: 'other_liability', label: 'Other Liability' }
	];

	const TYPE_COLORS: Record<string, string> = {
		checking: '#6366f1',
		savings: '#10b981',
		cash: '#f59e0b',
		credit_card: '#f43f5e',
		line_of_credit: '#fb7185',
		loan: '#f97316',
		mortgage: '#ea580c',
		investment: '#8b5cf6',
		other_asset: '#06b6d4',
		other_liability: '#64748b'
	};

	function typeColor(t: string) {
		return TYPE_COLORS[t] ?? '#64748b';
	}

	function typeLabel(t: string) {
		return accountTypes.find((a) => a.value === t)?.label ?? t;
	}

	function fmtBalance(minor: number | undefined | null) {
		if (minor == null) return '—';
		return '₱' + (minor / 100).toLocaleString('en-PH', { minimumFractionDigits: 2 });
	}

	function accountBalance(account: Account) {
		return account.current_balance_minor ?? account.opening_balance_minor;
	}

	function openingBalanceForCurrentBalance(account: Account, currentBalance: string) {
		const desiredCurrentMinor = Math.round(Number(currentBalance || 0) * 100);
		const transactionTotalMinor = accountBalance(account) - account.opening_balance_minor;

		return ((desiredCurrentMinor - transactionTotalMinor) / 100).toFixed(2);
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

	async function loadAccounts() {
		loading = true;
		error = '';

		try {
			const [activeRows, allRows] = await Promise.all([
				getAccounts(userId),
				getAccounts(userId, false)
			]);

			accounts = activeRows;
			archivedAccounts = allRows.filter((account) => account.status === 'archived');
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
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

		if (!confirmed) {
			return;
		}

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

<div class="flex flex-col gap-8 p-8">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Manage</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight">Accounts</h1>
			<p class="text-muted mt-2 text-sm">Create and manage local accounts.</p>
		</div>

		<div class="flex flex-wrap justify-end gap-2">
			<button class="secondary-action" type="button" onclick={openArchivedModal}>
				Archived accounts ({archivedAccounts.length})
			</button>
			<button class="primary-action" type="button" onclick={openAccountModal}>Add account</button>
		</div>
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

	<div class="dashboard-card overflow-hidden">
		<div class="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-5" style="border-color: var(--app-border)">
			<div>
				<p class="text-sm font-semibold">Active accounts</p>
				<p class="text-muted mt-1 text-xs">Archived accounts are hidden from this list.</p>
			</div>

			<span class="pill">{accounts.length} active</span>
		</div>

		{#if loading}
			<p class="text-muted px-6 py-12 text-center text-sm">Loading accounts...</p>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-left text-sm">
					<thead class="text-muted text-[11px] font-bold uppercase tracking-widest">
						<tr>
							<th class="px-6 py-3">Name</th>
							<th class="px-6 py-3">Type</th>
							<th class="px-6 py-3">Balance</th>
							<th class="px-6 py-3">Status</th>
							<th class="px-6 py-3 text-right">Actions</th>
						</tr>
					</thead>

					<tbody>
						{#each accounts as account}
							<tr class="border-t" style="border-color: var(--app-border)">
								<td class="px-6 py-4 font-medium">
									{account.name}
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center gap-2">
										<span
											class="h-2 w-2 flex-shrink-0 rounded-full"
											style="background:{typeColor(account.type)}"
										></span>
										{typeLabel(account.type)}
									</span>
								</td>
								<td class="px-6 py-4 font-semibold tabular-nums">
									{fmtBalance(accountBalance(account))}
								</td>
								<td class="px-6 py-4">
									<span class="pill">{account.status}</span>
								</td>
								<td class="px-6 py-4 text-right">
									<div class="flex justify-end gap-2">
										<button
											class="secondary-action"
											type="button"
											onclick={() => openEditModal(account)}
										>
											Edit
										</button>
										<button
											class="danger-action"
											type="button"
											onclick={() => archive(account)}
										>
											Archive
										</button>
									</div>
								</td>
							</tr>
						{:else}
							<tr>
								<td class="text-muted px-6 py-12 text-center text-sm" colspan="5">
									No accounts yet. Create one to get started.
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

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
		{fmtBalance}
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
		{fmtBalance}
		{accountBalance}
		onClose={closeArchivedModal}
		onEdit={(account) => openEditModal(account, true)}
		onRestore={restore}
	/>
{/if}
