<script lang="ts">
	import type { Transaction } from '$lib/api/transactions';

	let {
		transactions,
		loading,
		formatDate,
		formatGroupDate,
		formatMoney,
		accountName,
		categoryName,
		categoryGroupName,
		isTransfer,
		onEdit,
		onDelete
	} = $props<{
		transactions: Transaction[];
		loading: boolean;
		formatDate: (value: string) => string;
		formatGroupDate: (value: string) => string;
		formatMoney: (amountMinor: number) => string;
		accountName: (accountId: number) => string;
		categoryName: (categoryId: number) => string;
		categoryGroupName: (categoryId: number) => string;
		isTransfer: (transaction: Transaction) => boolean;
		onEdit: (transaction: Transaction) => void;
		onDelete: (transaction: Transaction) => void | Promise<void>;
	}>();

	let groupedTransactions = $derived(
		transactions.reduce((groups: { date: string; transactions: Transaction[] }[], transaction: Transaction) => {
			const date = transaction.transaction_date.slice(0, 10);
			const group = groups.find((row) => row.date === date);

			if (group) {
				group.transactions.push(transaction);
			} else {
				groups.push({ date, transactions: [transaction] });
			}

			return groups;
		}, [])
	);
</script>

{#if loading}
	<p class="text-muted px-6 py-12 text-center text-sm">Loading transactions...</p>
{:else}
	{#if transactions.length === 0}
		<p class="text-muted px-6 py-12 text-center text-sm">No transactions match the current filters.</p>
	{:else}
		<div class="divide-y" style="border-color: var(--app-border)">
			{#each groupedTransactions as group}
				<section>
					<div class="transaction-date-group flex items-center justify-between px-5 py-2 text-xs font-semibold text-muted">
						<span>{formatGroupDate(group.date)}</span>
						<span>
							{formatMoney(group.transactions.reduce((total: number, transaction: Transaction) => total + transaction.amount_minor, 0))}
						</span>
					</div>

					<div>
						{#each group.transactions as transaction}
							<div class="transaction-row-grid grid items-center gap-4 border-t px-5 py-4 text-sm transition-colors hover:bg-black/3" style="border-color: var(--app-border)">
								<div class="min-w-0">
									<div class="flex items-center gap-2">
										<span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-(--app-soft) text-xs">
											{isTransfer(transaction) ? '↔' : transaction.amount_minor < 0 ? '−' : '+'}
										</span>
										<div class="min-w-0">
											<p class="truncate font-semibold">{transaction.payee ?? 'No payee'}</p>
											{#if transaction.notes}
												<p class="text-muted truncate text-xs">{transaction.notes}</p>
											{/if}
										</div>
									</div>
								</div>

								<div class="min-w-0">
									<p class="truncate">{categoryName(transaction.category_id)}</p>
									<p class="text-muted truncate text-xs">{categoryGroupName(transaction.category_id)}</p>
								</div>

								<div class="min-w-0">
									<p class="truncate">{accountName(transaction.account_id)}</p>
									<p class="text-muted text-xs">{formatDate(transaction.transaction_date)}</p>
								</div>

								<div class="flex items-center justify-end gap-4">
									<p class={`whitespace-nowrap text-right font-semibold ${transaction.amount_minor < 0 ? 'money-negative' : 'money-positive'}`}>
										{formatMoney(transaction.amount_minor)}
									</p>

									<div class="flex items-center gap-2">
										<button class="transaction-row-action" type="button" onclick={() => onEdit(transaction)}>
											Edit
										</button>
										<button class="transaction-row-action danger" type="button" onclick={() => onDelete(transaction)}>
											Delete
										</button>
										<span class="text-muted text-lg leading-none">›</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/each}
		</div>
	{/if}
{/if}
