<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getBudgetItems, getBudgets, type Budget, type BudgetItem } from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup, type CategoryGroupType } from '$lib/api/categories';
	import PageHeader from '$lib/shared/components/PageHeader.svelte';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
	import {
		deleteTransaction,
		deleteTransfer,
		getTransactionsByUser,
		type Transaction
	} from '$lib/api/transactions';
	import { getTags, getTransactionTags, type Tag } from '$lib/api/tags';
	import TransactionModals from './features/modals/TransactionModals.svelte';
	import TransactionsFilterPanel from './features/components/TransactionsFilterPanel.svelte';
	import TransactionsTable from './features/components/TransactionsTable.svelte';
	import TransactionsToolbar from './features/components/TransactionsToolbar.svelte';
	import {
		countActiveFilters,
		filterTransactions,
		categoryGroupForCategory as getCategoryGroupForCategory,
		type TransactionFilters
	} from './features/utils/transactionFilters';
	import {
		formatDate,
		formatGroupDate,
		formatMoney
	} from './features/utils/transactionFormat';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let activeAccounts: Account[] = $state([]);
	let budgets: Budget[] = $state([]);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let tags: Tag[] = $state([]);
	let transactionTagIds: Record<number, number[]> = $state({});
	let transactions: Transaction[] = $state([]);
	let loading = $state(true);
	let error = $state('');
	let notice = $state('');
	let showCreateModal = $state(false);
	let showEditModal = $state(false);
	let editingTransaction: Transaction | null = $state(null);
	let filterAccountIds: number[] = $state([]);
	let filterTypes: CategoryGroupType[] = $state([]);
	let filterCategoryGroupIds: number[] = $state([]);
	let filterCategoryIds: number[] = $state([]);
	let filterSearch = $state('');
	let filterDateFrom = $state('');
	let filterDateTo = $state('');
	let filterAmountMin = $state('');
	let filterAmountMax = $state('');
	let showSearchTools = $state(false);
	let showDateTools = $state(false);
	let showFilterPanel = $state(false);
	let filterPanelRegion: HTMLDivElement | undefined = $state();

	let transactionFilters: TransactionFilters = $derived({
		search: filterSearch,
		dateFrom: filterDateFrom,
		dateTo: filterDateTo,
		accountIds: filterAccountIds,
		types: filterTypes,
		categoryGroupIds: filterCategoryGroupIds,
		categoryIds: filterCategoryIds,
		amountMin: filterAmountMin,
		amountMax: filterAmountMax
	});
	let filteredTransactions = $derived(
		filterTransactions(
			transactions,
			transactionFilters,
			categories,
			categoryGroups,
			accountName,
			categoryName
		)
	);
	let activeFilterCount = $derived(countActiveFilters(transactionFilters));

	function accountName(accountId: number) {
		return accounts.find((account) => account.account_id === accountId)?.name ?? `Account ${accountId}`;
	}

	function categoryName(categoryId: number) {
		const category = categories.find((row) => row.category_id === categoryId);

		if (!category) return `Category ${categoryId}`;
		return category.name;
	}

	function categoryGroupForCategory(categoryId: number) {
		return getCategoryGroupForCategory(categoryId, categories, categoryGroups);
	}

	function categoryGroupName(categoryId: number) {
		return categoryGroupForCategory(categoryId)?.name ?? 'No group';
	}

	function isTransfer(transaction: Transaction) {
		return transaction.transfer_id !== null && transaction.transfer_id !== undefined;
	}

	function clearTransactionFilters() {
		filterAccountIds = [];
		filterTypes = [];
		filterCategoryGroupIds = [];
		filterCategoryIds = [];
		filterSearch = '';
		filterDateFrom = '';
		filterDateTo = '';
		filterAmountMin = '';
		filterAmountMax = '';
	}

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [activeAccountRows, accountRows, budgetRows, categoryRows, groupRows, tagRows, transactionRows] = await Promise.all([
				getAccounts(userId),
				getAccounts(userId, false),
				getBudgets(userId),
				getAllCategories(userId),
				getCategoryGroups(userId),
				getTags(userId),
				getTransactionsByUser(userId)
			]);

			activeAccounts = activeAccountRows;
			accounts = accountRows;
			budgets = budgetRows;
			budgetItems = (await Promise.all(
				budgetRows.map((budget) => getBudgetItems(budget.budget_id))
			)).flat();
			categories = categoryRows;
			categoryGroups = groupRows;
			tags = tagRows;
			transactions = transactionRows;
			const transactionTagRows = await Promise.all(
				transactionRows.map(async (transaction) => ({
					transactionId: transaction.transaction_id,
					tags: await getTransactionTags(transaction.transaction_id)
				}))
			);
			transactionTagIds = Object.fromEntries(
				transactionTagRows.map((row) => [
					row.transactionId,
					row.tags.map((tag) => tag.tag_id)
				])
			);
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function openCreateModal() {
		error = '';
		notice = '';
		showCreateModal = true;
	}

	function openEditModal(transaction: Transaction) {
		error = '';
		notice = '';
		editingTransaction = transaction;
		showEditModal = true;
	}

	async function removeTransaction(transaction: Transaction) {
		const confirmed = confirm(
			isTransfer(transaction)
				? 'Delete this transfer pair?'
				: `Delete "${transaction.payee ?? 'this transaction'}"?`
		);

		if (!confirmed) return;

		error = '';
		notice = '';

		try {
			if (isTransfer(transaction)) {
				await deleteTransfer(transaction.transfer_id!);
				notice = 'Transfer deleted.';
			} else {
				await deleteTransaction(transaction.transaction_id);
				notice = 'Transaction deleted.';
			}

			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(() => {
		loadPage();

		function closeTransactionToolsOnOutsideClick(event: MouseEvent) {
			if (
				(showFilterPanel || showSearchTools || showDateTools)
				&& filterPanelRegion
				&& !filterPanelRegion.contains(event.target as Node)
			) {
				showFilterPanel = false;
				showSearchTools = false;
				showDateTools = false;
			}
		}

		window.addEventListener('mousedown', closeTransactionToolsOnOutsideClick);

		return () => {
			window.removeEventListener('mousedown', closeTransactionToolsOnOutsideClick);
		};
	});
</script>

<ToastOnChange {error} {notice} />

<section class="transaction-page flex min-h-screen flex-col">
	<div bind:this={filterPanelRegion} class="relative">
		<PageHeader eyebrow="Ledger" title="Transactions" subtitle={`${filteredTransactions.length} shown · ${transactions.length} total`}>
			<TransactionsToolbar
				bind:search={filterSearch}
				bind:dateFrom={filterDateFrom}
				bind:dateTo={filterDateTo}
				filterCount={activeFilterCount}
				bind:showSearch={showSearchTools}
				bind:showDate={showDateTools}
				bind:showFilters={showFilterPanel}
				onAdd={openCreateModal}
			/>
		</PageHeader>

		{#if showFilterPanel}
			<TransactionsFilterPanel
				bind:selectedAccountIds={filterAccountIds}
				bind:selectedTypes={filterTypes}
				bind:selectedCategoryGroupIds={filterCategoryGroupIds}
				bind:selectedCategoryIds={filterCategoryIds}
				bind:amountMin={filterAmountMin}
				bind:amountMax={filterAmountMax}
				accounts={activeAccounts}
				{categoryGroups}
				{categories}
				filterCount={activeFilterCount}
				onClear={clearTransactionFilters}
				onClose={() => showFilterPanel = false}
			/>
		{/if}
	</div>

	<div class="flex flex-col gap-5 p-5">
		<div class="transaction-table-card overflow-visible">
			<TransactionsTable
				transactions={filteredTransactions}
				{loading}
				{formatDate}
				{formatGroupDate}
				{formatMoney}
				{accountName}
				{categoryName}
				{categoryGroupName}
				{isTransfer}
				{tags}
				{transactionTagIds}
				onEdit={openEditModal}
				onDelete={removeTransaction}
			/>
		</div>
	</div>
</section>

<TransactionModals
	bind:showCreateModal
	bind:showEditModal
	bind:editingTransaction
	{activeAccounts}
	{accounts}
	{transactions}
	{budgets}
	{budgetItems}
	{categories}
	{categoryGroups}
	{tags}
	{transactionTagIds}
	{categoryName}
	onRefresh={loadPage}
	onNotice={(message) => notice = message}
/>
