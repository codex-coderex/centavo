<script lang="ts">
	import type { Transaction } from '$lib/api/transactions';

	let {
		transactions,
		loading,
		formatDate,
		formatMoney,
		accountName,
		categoryName,
		isTransfer,
		onEdit,
		onDelete
	} = $props<{
		transactions: Transaction[];
		loading: boolean;
		formatDate: (value: string) => string;
		formatMoney: (amountMinor: number) => string;
		accountName: (accountId: number) => string;
		categoryName: (categoryId: number) => string;
		isTransfer: (transaction: Transaction) => boolean;
		onEdit: (transaction: Transaction) => void;
		onDelete: (transaction: Transaction) => void | Promise<void>;
	}>();
</script>

{#if loading}
	<p class="text-muted px-6 py-12 text-center text-sm">Loading transactions...</p>
{:else}
	<div class="overflow-x-auto">
		<table class="w-full text-left text-sm">
			<thead class="text-muted text-xs uppercase tracking-wider">
				<tr>
					<th class="px-6 py-4 font-medium">Date</th>
					<th class="px-6 py-4 font-medium">Payee</th>
					<th class="px-6 py-4 font-medium">Category</th>
					<th class="px-6 py-4 font-medium">Account</th>
					<th class="px-6 py-4 text-right font-medium">Amount</th>
					<th class="px-6 py-4 text-right font-medium">Actions</th>
				</tr>
			</thead>

			<tbody>
				{#each transactions as transaction}
					<tr class="border-t transition-colors hover:bg-black/[0.02]" style="border-color: var(--app-border)">
						<td class="px-6 py-4">
							{formatDate(transaction.transaction_date)}
						</td>

						<td class="px-6 py-4">
							<div class="font-medium">
								{transaction.payee ?? 'No payee'}
							</div>
							{#if transaction.notes}
								<div class="text-muted mt-1 text-xs">
									{transaction.notes}
								</div>
							{/if}
							{#if isTransfer(transaction)}
								<span class="pill mt-2 inline-flex">transfer</span>
							{/if}
						</td>

						<td class="px-6 py-4">
							{categoryName(transaction.category_id)}
						</td>

						<td class="px-6 py-4">
							{accountName(transaction.account_id)}
						</td>

						<td
							class={`px-6 py-4 text-right font-semibold ${
								transaction.amount_minor < 0 ? 'money-negative' : 'money-positive'
							}`}
						>
							{formatMoney(transaction.amount_minor)}
						</td>

						<td class="px-6 py-4 text-right">
							<div class="flex justify-end gap-2">
								<button
									class="secondary-action"
									type="button"
									onclick={() => onEdit(transaction)}
								>
									Edit
								</button>
								<button
									class="danger-action"
									type="button"
									onclick={() => onDelete(transaction)}
								>
									Delete
								</button>
							</div>
						</td>
					</tr>
				{:else}
					<tr>
						<td class="text-muted px-6 py-12 text-center text-sm" colspan="6">
							No transactions match the current filters.
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
