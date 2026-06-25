<script lang="ts">
	import type { Tag } from '$lib/api/tags';
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
		tags,
		transactionTagIds,
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
		tags: Tag[];
		transactionTagIds: Record<number, number[]>;
		onEdit: (transaction: Transaction) => void;
		onDelete: (transaction: Transaction) => void | Promise<void>;
	}>();

	type SortKey = 'payee' | 'category' | 'account' | 'date' | 'amount' | 'created';
	let sortKey: SortKey = $state('date');
	let sortDirection: 'asc' | 'desc' = $state('desc');

	function transactionDay(transaction: Transaction) {
		return transaction.transaction_date.slice(0, 10);
	}

	function tagsForTransaction(transactionId: number) {
		const ids = transactionTagIds[transactionId] ?? [];
		return tags.filter((tag: Tag) => ids.includes(tag.tag_id));
	}

	function sortValue(transaction: Transaction, key: SortKey) {
		if (key === 'payee') return transaction.payee ?? '';
		if (key === 'category') return categoryName(transaction.category_id);
		if (key === 'account') return accountName(transaction.account_id);
		if (key === 'date') return transactionDay(transaction);
		if (key === 'amount') return Math.abs(transaction.amount_minor);
		return transaction.created_at ?? transaction.transaction_date;
	}

	function compareValues(left: string | number, right: string | number) {
		if (typeof left === 'number' && typeof right === 'number') return left - right;
		return String(left).localeCompare(String(right), undefined, {
			numeric: true,
			sensitivity: 'base'
		});
	}

	function compareTransactions(a: Transaction, b: Transaction) {
		const primary = compareValues(sortValue(a, sortKey), sortValue(b, sortKey));
		if (primary !== 0) return sortDirection === 'asc' ? primary : -primary;

		// Stable, deterministic tie-breakers so rows do not jump randomly.
		const dateTie = b.transaction_date.localeCompare(a.transaction_date);
		if (dateTie !== 0) return dateTie;

		return b.transaction_id - a.transaction_id;
	}

	function setSort(key: SortKey) {
		if (sortKey === key) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
			return;
		}

		sortKey = key;
		sortDirection = key === 'payee' || key === 'category' || key === 'account' ? 'asc' : 'desc';
	}

	function sortMark(key: SortKey) {
		if (sortKey !== key) return '↕';
		return sortDirection === 'asc' ? '↑' : '↓';
	}

	function ariaSort(key: SortKey) {
		if (sortKey !== key) return 'none';
		return sortDirection === 'asc' ? 'ascending' : 'descending';
	}

	let groupedTransactions = $derived.by(() => {
		const groups = new Map<string, Transaction[]>();

		for (const transaction of [...transactions].sort(compareTransactions)) {
			const day = transactionDay(transaction);
			const group = groups.get(day);

			if (group) {
				group.push(transaction);
			} else {
				groups.set(day, [transaction]);
			}
		}

		return Array.from(groups, ([date, rows]) => ({ date, transactions: rows }));
	});
</script>

{#if loading}
	<p class="text-muted px-6 py-12 text-center text-sm">Loading transactions...</p>
{:else if transactions.length === 0}
	<p class="text-muted px-6 py-12 text-center text-sm">No transactions match the current filters.</p>
{:else}
	<div class="overflow-x-auto">
		<table class="transaction-table w-full min-w-[760px] table-fixed border-collapse text-left text-sm">
			<colgroup>
				<col class="w-[38%]" />
				<col class="w-[22%]" />
				<col class="w-[22%]" />
				<col class="w-[12rem]" />
			</colgroup>
			<thead>
				<tr class="border-b text-xs font-bold uppercase tracking-widest text-muted" style="border-color: var(--app-border)">
					<th class="px-5 py-4" aria-sort={ariaSort('payee')}>
						<button class="sortable-header" type="button" onclick={() => setSort('payee')}>Payee {sortMark('payee')}</button>
					</th>
					<th class="px-5 py-4" aria-sort={ariaSort('category')}>
						<button class="sortable-header" type="button" onclick={() => setSort('category')}>Category {sortMark('category')}</button>
					</th>
					<th class="px-5 py-4" aria-sort={ariaSort('account')}>
						<button class="sortable-header" type="button" onclick={() => setSort('account')}>Account {sortMark('account')}</button>
					</th>
					<th class="px-5 py-4 text-right" aria-sort={ariaSort('amount')}>
						<button class="sortable-header ml-auto" type="button" onclick={() => setSort('amount')}>Amount {sortMark('amount')}</button>
					</th>
				</tr>
			</thead>
			<tbody>
				{#each groupedTransactions as group (group.date)}
					<tr class="transaction-date-group border-b text-xs font-bold text-muted" style="border-color: var(--app-border)">
						<td class="px-5 py-2.5" colspan="4">
							<button class="sortable-date-header" type="button" onclick={() => setSort('date')} title="Sort by date">
								{formatGroupDate(group.date)} {sortKey === 'date' ? sortMark('date') : ''}
							</button>
						</td>
					</tr>

					{#each group.transactions as transaction (transaction.transaction_id)}
						<tr class="transaction-row border-b last:border-b-0" style="border-color: var(--app-border)">
							<td class="px-5 py-3.5">
								<div class="flex min-w-0 items-center gap-2.5">
									<span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-(--app-soft) text-xs">
										{isTransfer(transaction) ? '↔' : transaction.amount_minor < 0 ? '−' : '+'}
									</span>
									<div class="min-w-0 flex-1">
										<p class="truncate font-semibold" title={transaction.payee ?? 'No payee'}>{transaction.payee ?? 'No payee'}</p>
										{#if transaction.notes}
											<p class="transaction-note-fade text-muted text-xs" title={transaction.notes}>{transaction.notes}</p>
										{/if}
										{#if tagsForTransaction(transaction.transaction_id).length > 0}
											<div class="mt-2 flex min-w-0 flex-wrap gap-1.5 overflow-hidden">
												{#each tagsForTransaction(transaction.transaction_id) as tag (tag.tag_id)}
													<span class="transaction-tag-pill compact max-w-full truncate" title={tag.name}>{tag.name}</span>
												{/each}
											</div>
										{/if}
									</div>
								</div>
							</td>
							<td class="px-5 py-3.5">
								<p class="truncate" title={categoryName(transaction.category_id)}>{categoryName(transaction.category_id)}</p>
								<p class="text-muted truncate text-xs" title={categoryGroupName(transaction.category_id)}>{categoryGroupName(transaction.category_id)}</p>
							</td>
							<td class="px-5 py-3.5 text-muted"><p class="truncate" title={accountName(transaction.account_id)}>{accountName(transaction.account_id)}</p></td>
							<td class={`px-5 py-3.5 text-right font-semibold ${transaction.amount_minor < 0 ? 'money-negative' : 'money-positive'}`}>
								<div class="flex items-center justify-end gap-4">
									<span>{formatMoney(transaction.amount_minor)}</span>
									<span class="transaction-row-actions inline-flex shrink-0 items-center gap-3">
										<button class="transaction-row-action" type="button" onclick={() => onEdit(transaction)}>Edit</button>
										<button class="transaction-row-action danger" type="button" onclick={() => onDelete(transaction)}>Delete</button>
									</span>
								</div>
							</td>
						</tr>
					{/each}
				{/each}
			</tbody>
		</table>
	</div>
{/if}
