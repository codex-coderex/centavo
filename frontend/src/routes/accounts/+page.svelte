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

	// Color accents per account type — falls back to slate for any type
	// not listed here, so it won't break if "bank"/"ewallet" end up being
	// the real values instead of "checking"/"cash".
	const TYPE_COLORS: Record<string, string> = {
		checking: '#6366f1',
		bank: '#6366f1',
		savings: '#10b981',
		cash: '#f59e0b',
		credit: '#f43f5e',
		investment: '#8b5cf6',
		loan: '#f97316',
		ewallet: '#06b6d4',
		other: '#64748b'
	};

	function typeColor(t: string) {
		return TYPE_COLORS[t] ?? '#64748b';
	}

	function typeLabel(t: string) {
		return accountTypes.find((a) => a.value === t)?.label ?? t;
	}

	// NOTE: assumes Account has a `balance_minor` field (centavos, like
	// amount_minor elsewhere in the app). If that field doesn't exist yet
	// on the type/backend, this will need a small follow-up.
	function fmtBalance(minor: number | undefined | null) {
		if (minor == null) return '—';
		return '₱' + (minor / 100).toLocaleString('en-PH', { minimumFractionDigits: 2 });
	}

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

<div class="flex flex-col gap-8 p-8">

	<!-- Header — matches Dashboard's eyebrow + title pattern -->
	<div class="flex items-end justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Manage</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-50">Accounts</h1>
			<p class="mt-2 text-sm text-slate-400">Create and manage local accounts.</p>
		</div>
		<div class="rounded-full border border-slate-800/60 bg-slate-900/80 px-3 py-1 text-xs font-medium text-slate-400">
			{accounts.length} active
		</div>
	</div>

	{#if error}
		<div class="rounded-2xl border border-red-500/30 bg-red-950/30 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-sm text-emerald-200">
			{notice}
		</div>
	{/if}

	<div class="grid gap-4 xl:grid-cols-[380px_1fr]">

		<!-- New account form -->
		<form
			class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-6"
			onsubmit={(event) => {
				event.preventDefault();
				submitAccount();
			}}
		>
			<p class="text-sm font-semibold text-slate-100">New account</p>
			<p class="mt-1 text-xs text-slate-500">
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
				class="mt-5 w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
				type="submit"
				disabled={saving}
			>
				{saving ? 'Creating...' : 'Create account'}
			</button>
		</form>

		<!-- Active accounts -->
		<div class="overflow-hidden rounded-2xl border border-slate-800/60 bg-slate-900/80">
			<div class="border-b border-slate-800/60 px-6 py-5">
				<p class="text-sm font-semibold text-slate-100">Active accounts</p>
				<p class="mt-1 text-xs text-slate-500">Archived accounts are hidden from this list.</p>
			</div>

			{#if loading}
				<p class="px-6 py-12 text-center text-sm text-slate-600">Loading accounts...</p>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full text-left text-sm">
						<thead class="text-[11px] font-bold uppercase tracking-widest text-slate-500">
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
								<tr class="border-t border-slate-800/60">
									<td class="px-6 py-4 font-medium text-slate-100">
										{account.name}
									</td>
									<td class="px-6 py-4 text-slate-300">
										<span class="inline-flex items-center gap-2">
											<span
												class="h-2 w-2 flex-shrink-0 rounded-full"
												style="background:{typeColor(account.type)}"
											></span>
											{typeLabel(account.type)}
										</span>
									</td>
									<td class="px-6 py-4 font-semibold tabular-nums text-slate-100">
										{fmtBalance(account.balance_minor)}
									</td>
									<td class="px-6 py-4">
										<span class="rounded-full bg-emerald-950 px-2 py-1 text-xs text-emerald-300">
											{account.status}
										</span>
									</td>
									<td class="px-6 py-4 text-right">
										<button
											class="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-950/40"
											type="button"
											onclick={() => archive(account)}
										>
											Archive
										</button>
									</td>
								</tr>
							{:else}
								<tr>
									<td class="px-6 py-12 text-center text-sm text-slate-600" colspan="5">
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
</div>