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
    <div class="mb-10 flex items-start justify-between gap-4">
        <div>
            <p class="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-500">Records</p>
            <h1 class="text-3xl font-bold tracking-tight text-slate-100">Transactions</h1>
            <p class="mt-2 text-sm text-slate-400">
                Read-only transaction list for now. Creation comes after categories are stable.
            </p>
        </div>

        <div class="rounded-full border border-slate-800 bg-slate-900/50 px-3 py-1.5 text-xs font-medium text-slate-400">
            {transactions.length} transactions
        </div>
    </div>

    {#if error}
        <div class="mb-8 rounded-xl border border-red-500/20 bg-[#2a0e14] p-4 text-sm text-red-200">
            {error}
        </div>
    {/if}

    <div class="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
        <div class="px-6 pb-2 pt-6">
            <h2 class="text-base font-semibold text-slate-100">All transactions</h2>
            <p class="mt-1 text-sm text-slate-400">
                Showing transactions across active accounts.
            </p>
        </div>

        {#if loading}
            <p class="px-6 pb-6 pt-4 text-sm text-slate-400">Loading transactions...</p>
        {:else}
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                    <thead class="text-xs uppercase tracking-wider text-slate-500">
                        <tr>
                            <th class="px-6 py-4 font-medium">Date</th>
                            <th class="px-6 py-4 font-medium">Merchant</th>
                            <th class="px-6 py-4 font-medium">Account</th>
                            <th class="px-6 py-4 font-medium">Status</th>
                            <th class="px-6 py-4 font-medium">Review</th>
                            <th class="px-6 py-4 text-right font-medium">Amount</th>
                        </tr>
                    </thead>

                    <tbody>
                        {#each transactions as transaction}
                            <tr class="border-t border-slate-800/50 transition-colors hover:bg-slate-800/20">
                                <td class="px-6 py-4 text-slate-300">
                                    {formatDate(transaction.txn_date)}
                                </td>

                                <td class="px-6 py-4">
                                    <div class="font-medium text-slate-100">
                                        {transaction.merchant ?? 'No merchant'}
                                    </div>
                                    {#if transaction.note}
                                        <div class="mt-1 text-xs text-slate-500">
                                            {transaction.note}
                                        </div>
                                    {/if}
                                </td>

                                <td class="px-6 py-4 text-slate-300">
                                    {accountName(transaction.account_id)}
                                </td>

                                <td class="px-6 py-4">
                                    <span class="rounded-full bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-300">
                                        {transaction.status}
                                    </span>
                                </td>

                                <td class="px-6 py-4">
                                    {#if transaction.needs_review}
                                        <span class="rounded-full border border-amber-900/50 bg-amber-950/60 px-2.5 py-1 text-xs font-medium text-amber-300">
                                            Needs review
                                        </span>
                                    {:else}
                                        <span class="text-xs text-slate-600">—</span>
                                    {/if}
                                </td>

                                <td
                                    class={`px-6 py-4 text-right font-semibold ${
                                        transaction.amount_minor < 0 ? 'text-red-400' : 'text-emerald-400'
                                    }`}
                                >
                                    {formatMoney(transaction.amount_minor)}
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td class="px-6 py-12 text-center text-sm text-slate-500" colspan="6">
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