<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getTransactionsByUser, type Transaction } from '$lib/api/transactions';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let transactions: Transaction[] = $state([]);
	let loading = $state(true);
	let error = $state('');

	function formatMoney(amountMinor: number) {
		return new Intl.NumberFormat('en-PH', {
			style: 'currency',
			currency: 'PHP'
		}).format(amountMinor / 100);
	}

	function formatDate(value: string) {
		return new Date(value).toLocaleDateString('en-PH', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function accountName(accountId: number) {
		return accounts.find((account) => account.account_id === accountId)?.name ?? `Account ${accountId}`;
	}

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [accountRows, transactionRows] = await Promise.all([
				getAccounts(userId),
				getTransactionsByUser(userId)
			]);

			accounts = accountRows;
			transactions = transactionRows;
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	onMount(loadPage);
</script>

<section>
	<div class="mb-8 flex items-start justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight text-slate-100">Transactions</h1>
			<p class="mt-2 text-sm text-slate-400">
				Read-only transaction list for now. Creation comes after categories are stable.
			</p>
		</div>

		<div class="rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-400">
			{transactions.length} transactions
		</div>
	</div>

	{#if error}
		<div class="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	<div class="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
		<div class="border-b border-slate-800 px-5 py-4">
			<h2 class="text-lg font-semibold text-slate-100">All transactions</h2>
			<p class="mt-1 text-sm text-slate-400">
				Showing transactions across active accounts.
			</p>
		</div>

		{#if loading}
			<p class="p-5 text-sm text-slate-400">Loading transactions...</p>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-left text-sm">
					<thead class="bg-slate-950/60 text-xs uppercase tracking-wide text-slate-500">
						<tr>
							<th class="px-5 py-3">Date</th>
							<th class="px-5 py-3">Merchant</th>
							<th class="px-5 py-3">Account</th>
							<th class="px-5 py-3">Status</th>
							<th class="px-5 py-3">Review</th>
							<th class="px-5 py-3 text-right">Amount</th>
						</tr>
					</thead>

					<tbody>
						{#each transactions as transaction}
							<tr class="border-t border-slate-800">
								<td class="px-5 py-4 text-slate-300">
									{formatDate(transaction.txn_date)}
								</td>

								<td class="px-5 py-4">
									<div class="font-medium text-slate-100">
										{transaction.merchant ?? 'No merchant'}
									</div>
									{#if transaction.note}
										<div class="mt-1 text-xs text-slate-500">
											{transaction.note}
										</div>
									{/if}
								</td>

								<td class="px-5 py-4 text-slate-300">
									{accountName(transaction.account_id)}
								</td>

								<td class="px-5 py-4">
									<span class="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-300">
										{transaction.status}
									</span>
								</td>

								<td class="px-5 py-4">
									{#if transaction.needs_review}
										<span class="rounded-full bg-amber-950 px-2 py-1 text-xs text-amber-300">
											Needs review
										</span>
									{:else}
										<span class="text-xs text-slate-600">—</span>
									{/if}
								</td>

								<td
									class={`px-5 py-4 text-right font-semibold ${
										transaction.amount_minor < 0 ? 'text-red-300' : 'text-emerald-300'
									}`}
								>
									{formatMoney(transaction.amount_minor)}
								</td>
							</tr>
						{:else}
							<tr>
								<td class="px-5 py-8 text-center text-sm text-slate-500" colspan="6">
									No transactions yet.
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</section>