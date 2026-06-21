<script lang="ts">
	import { onMount } from 'svelte';
	import {
		archiveAccount,
		createAccount,
		getAccounts,
		type Account
	} from '$lib/api/accounts';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let notice = $state('');

	let name = $state('');
	let type = $state('checking');

	const accountTypes = [
		{ value: 'checking', label: 'Checking' },
		{ value: 'savings', label: 'Savings' },
		{ value: 'cash', label: 'Cash' },
		{ value: 'credit', label: 'Credit Card' },
		{ value: 'investment', label: 'Investment' },
		{ value: 'loan', label: 'Loan' },
		{ value: 'other', label: 'Other' }
	];

	async function loadAccounts() {
		loading = true;
		error = '';
		notice = '';

		try {
			accounts = await getAccounts(userId);
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function submitAccount() {
		error = '';
		notice = '';

		if (!name.trim()) {
			error = 'Account name is required.';
			return;
		}

		saving = true;

		try {
			await createAccount({
				user_id: userId,
				name: name.trim(),
				type
			});

			name = '';
			type = 'checking';
			notice = 'Account created.';
			await loadAccounts();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
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

	onMount(loadAccounts);
</script>

<section>
	<div class="mb-8 flex items-start justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight text-slate-100">Accounts</h1>
			<p class="mt-2 text-sm text-slate-400">
				Create and manage local accounts.
			</p>
		</div>

		<div class="rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-400">
			{accounts.length} active
		</div>
	</div>

	{#if error}
		<div class="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="mb-4 rounded-xl border border-emerald-500/40 bg-emerald-950/40 p-4 text-sm text-emerald-200">
			{notice}
		</div>
	{/if}

	<div class="grid gap-6 xl:grid-cols-[380px_1fr]">
		<form
			class="rounded-xl border border-slate-800 bg-slate-900 p-5"
			onsubmit={(event) => {
				event.preventDefault();
				submitAccount();
			}}
		>
			<h2 class="text-lg font-semibold text-slate-100">New account</h2>
			<p class="mt-1 text-sm text-slate-400">
				Add cash, bank, credit, loan, or investment accounts.
			</p>

			<label class="mt-5 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Account name</span>
				<input
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
					bind:value={name}
					placeholder="Checking, Cash, Savings"
				/>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Account type</span>
				<select
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
					bind:value={type}
				>
					{#each accountTypes as accountType}
						<option value={accountType.value}>{accountType.label}</option>
					{/each}
				</select>
			</label>

			<button
				class="mt-5 w-full rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
				type="submit"
				disabled={saving}
			>
				{saving ? 'Creating...' : 'Create account'}
			</button>
		</form>

		<div class="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
			<div class="border-b border-slate-800 px-5 py-4">
				<h2 class="text-lg font-semibold text-slate-100">Active accounts</h2>
				<p class="mt-1 text-sm text-slate-400">
					Archived accounts are hidden from this list.
				</p>
			</div>

			{#if loading}
				<p class="p-5 text-sm text-slate-400">Loading accounts...</p>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full text-left text-sm">
						<thead class="bg-slate-950/60 text-xs uppercase tracking-wide text-slate-500">
							<tr>
								<th class="px-5 py-3">Name</th>
								<th class="px-5 py-3">Type</th>
								<th class="px-5 py-3">Status</th>
								<th class="px-5 py-3 text-right">Actions</th>
							</tr>
						</thead>

						<tbody>
							{#each accounts as account}
								<tr class="border-t border-slate-800">
									<td class="px-5 py-4 font-medium text-slate-100">
										{account.name}
									</td>
									<td class="px-5 py-4 text-slate-300">
										{account.type}
									</td>
									<td class="px-5 py-4">
										<span class="rounded-full bg-emerald-950 px-2 py-1 text-xs text-emerald-300">
											{account.status}
										</span>
									</td>
									<td class="px-5 py-4 text-right">
										<button
											class="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs font-medium text-red-300 hover:bg-red-950/40"
											type="button"
											onclick={() => archive(account)}
										>
											Archive
										</button>
									</td>
								</tr>
							{:else}
								<tr>
									<td class="px-5 py-8 text-center text-sm text-slate-500" colspan="4">
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
</section>