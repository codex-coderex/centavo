<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getBudgetItems, getBudgets, type Budget, type BudgetItem } from '$lib/api/budgets';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup, type CategoryGroupType } from '$lib/api/categories';
	import {
		createTransaction,
		createTransfer,
		deleteTransaction,
		deleteTransfer,
		getTransactionsByUser,
		updateTransaction,
		updateTransfer,
		type Transaction
	} from '$lib/api/transactions';
	import FilterCombobox from './FilterCombobox.svelte';
	import CreateTransactionModal from './CreateTransactionModal.svelte';
	import TransactionModal from './TransactionModal.svelte';
	import TransactionsTable from './TransactionsTable.svelte';

	const userId = 1;

	let accounts: Account[] = $state([]);
	let activeAccounts: Account[] = $state([]);
	let budgets: Budget[] = $state([]);
	let budgetItems: BudgetItem[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let transactions: Transaction[] = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let notice = $state('');
	let modalError = $state('');
	let showCreateModal = $state(false);
	let showEditModal = $state(false);
	let editingTransaction: Transaction | null = $state(null);

	let createMode: CategoryGroupType = $state('expense');
	let createAccountId = $state(0);
	let createToAccountId = $state(0);
	let createCategoryGroupId = $state(0);
	let createCategoryId = $state(0);
	let createBudgetId = $state('none');
	let createBudgetItemId = $state('none');
	let createAmount = $state('');
	let createDate = $state('');
	let createPayee = $state('');
	let createNotes = $state('');

	let editAccountId = $state(0);
	let editCategoryId = $state(0);
	let editBudgetId = $state('none');
	let editBudgetItemId = $state('none');
	let editAmount = $state('');
	let editDate = $state('');
	let editPayee = $state('');
	let editNotes = $state('');
	let filterAccountId = $state('all');
	let filterType: 'all' | CategoryGroupType = $state('all');
	let filterCategoryGroupId = $state('all');
	let filterCategoryId = $state('all');
	let filterSearch = $state('');

	let accountFilterOptions = $derived([
		{ value: 'all', label: 'All accounts' },
		...accounts.map((account) => ({
			value: String(account.account_id),
			label: account.name
		}))
	]);
	let typeFilterOptions = [
		{ value: 'all', label: 'All types' },
		{ value: 'expense', label: 'Expense' },
		{ value: 'income', label: 'Income' },
		{ value: 'transfer', label: 'Transfer' }
	];
	let groupFilterOptions = $derived([
		{ value: 'all', label: 'All groups' },
		...categoryGroups
			.filter((group) => filterType === 'all' || group.type === filterType)
			.map((group) => ({
				value: String(group.group_id),
				label: group.name
			}))
	]);
	let categoryFilterOptions = $derived([
		{ value: 'all', label: 'All categories' },
		...categories
			.filter((category) => filterCategoryGroupId === 'all' || category.group_id === Number(filterCategoryGroupId))
			.map((category) => ({
				value: String(category.category_id),
				label: categoryName(category.category_id)
			}))
	]);
	let filteredTransactions = $derived(
		transactions.filter((transaction) => {
			const group = categoryGroupForCategory(transaction.category_id);
			const search = filterSearch.trim().toLowerCase();

			if (filterAccountId !== 'all' && transaction.account_id !== Number(filterAccountId)) {
				return false;
			}

			if (filterType !== 'all' && group?.type !== filterType) {
				return false;
			}

			if (filterCategoryGroupId !== 'all' && group?.group_id !== Number(filterCategoryGroupId)) {
				return false;
			}

			if (filterCategoryId !== 'all' && transaction.category_id !== Number(filterCategoryId)) {
				return false;
			}

			if (
				search
				&& ![
					transaction.payee ?? '',
					transaction.notes ?? '',
					accountName(transaction.account_id),
					categoryName(transaction.category_id)
				].some((value) => value.toLowerCase().includes(search))
			) {
				return false;
			}

			return true;
		})
	);

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

	function dateInputValue(value: string) {
		return new Date(value).toISOString().slice(0, 10);
	}

	function accountName(accountId: number) {
		return accounts.find((account) => account.account_id === accountId)?.name ?? `Account ${accountId}`;
	}

	function categoryName(categoryId: number) {
		const category = categories.find((row) => row.category_id === categoryId);

		if (!category) return `Category ${categoryId}`;
		return category.name;
	}

	function categoryGroupForCategory(categoryId: number) {
		const category = categories.find((row) => row.category_id === categoryId);
		return categoryGroups.find((row) => row.group_id === category?.group_id);
	}

	function todayInputValue() {
		return new Date().toISOString().slice(0, 10);
	}

	function isTransfer(transaction: Transaction) {
		return transaction.transfer_id !== null && transaction.transfer_id !== undefined;
	}

	function groupsForType(type: CategoryGroupType) {
		return categoryGroups.filter((group) => group.type === type);
	}

	$effect(() => {
		if (
			filterCategoryGroupId !== 'all'
			&& !groupFilterOptions.some((option) => option.value === filterCategoryGroupId)
		) {
			filterCategoryGroupId = 'all';
		}

		if (
			filterCategoryId !== 'all'
			&& !categoryFilterOptions.some((option) => option.value === filterCategoryId)
		) {
			filterCategoryId = 'all';
		}
	});

	function budgetIdForBudgetItem(budgetItemId: number | null | undefined) {
		if (budgetItemId == null) return 'none';

		const item = budgetItems.find((row) => row.budget_item_id === budgetItemId);
		return item ? String(item.budget_id) : 'none';
	}

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [activeAccountRows, accountRows, budgetRows, categoryRows, groupRows, transactionRows] = await Promise.all([
				getAccounts(userId),
				getAccounts(userId, false),
				getBudgets(userId),
				getAllCategories(userId),
				getCategoryGroups(userId),
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
			transactions = transactionRows;
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function openCreateModal() {
		error = '';
		notice = '';
		modalError = '';
		createMode = 'expense';
		createAccountId = activeAccounts[0]?.account_id ?? 0;
		createToAccountId = activeAccounts.find((account) => account.account_id !== createAccountId)?.account_id ?? 0;
		createCategoryGroupId = groupsForType('expense')[0]?.group_id ?? 0;
		createCategoryId = categories.find((category) => category.group_id === createCategoryGroupId)?.category_id ?? 0;
		createBudgetId = 'none';
		createBudgetItemId = 'none';
		createAmount = '';
		createDate = todayInputValue();
		createPayee = '';
		createNotes = '';
		showCreateModal = true;
	}

	function closeCreateModal() {
		showCreateModal = false;
		modalError = '';
		saving = false;
	}

	function openEditModal(transaction: Transaction) {
		error = '';
		notice = '';
		modalError = '';
		editingTransaction = transaction;
		editAccountId = transaction.account_id;
		editCategoryId = transaction.category_id;
		editBudgetId = budgetIdForBudgetItem(transaction.budget_item_id);
		editBudgetItemId = transaction.budget_item_id ? String(transaction.budget_item_id) : 'none';
		editAmount = isTransfer(transaction)
			? Math.abs(transaction.amount_minor / 100).toFixed(2)
			: (transaction.amount_minor / 100).toFixed(2);
		editDate = dateInputValue(transaction.transaction_date);
		editPayee = transaction.payee ?? '';
		editNotes = transaction.notes ?? '';
		showEditModal = true;
	}

	async function submitCreateTransaction() {
		modalError = '';
		notice = '';

		if (createAccountId === 0) {
			modalError = 'Create an active account first.';
			return;
		}

		if (createCategoryId === 0) {
			modalError = `Create an active ${createMode} category first.`;
			return;
		}

		if (createMode === 'transfer') {
			if (createToAccountId === 0) {
				modalError = 'Create another active account first.';
				return;
			}

			if (createAccountId === createToAccountId) {
				modalError = 'Cannot transfer to the same account.';
				return;
			}
		}

		if (!createAmount.trim()) {
			modalError = 'Amount is required.';
			return;
		}

		if (!createDate) {
			modalError = 'Transaction date is required.';
			return;
		}

		if (createMode === 'expense' && createBudgetId !== 'none' && createBudgetItemId === 'none') {
			modalError = 'The selected budget does not have an item for this category.';
			return;
		}

		saving = true;

		try {
			if (createMode === 'transfer') {
				await createTransfer({
					from_account_id: createAccountId,
					to_account_id: createToAccountId,
					category_id: createCategoryId,
					amount: createAmount,
					transaction_date: createDate,
					payee: createPayee || 'Transfer',
					notes: createNotes || null
				});
			} else {
				await createTransaction({
					account_id: createAccountId,
					category_id: createCategoryId,
					budget_item_id: createMode === 'expense' && createBudgetId !== 'none' && createBudgetItemId !== 'none'
						? Number(createBudgetItemId)
						: null,
					amount: createMode === 'expense' ? `-${createAmount}` : createAmount,
					transaction_date: createDate,
					payee: createPayee || null,
					notes: createNotes || null
				});
			}

			notice = createMode === 'transfer' ? 'Transfer created.' : 'Transaction created.';
			closeCreateModal();
			await loadPage();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	function closeEditModal() {
		showEditModal = false;
		editingTransaction = null;
		modalError = '';
		saving = false;
	}

	async function submitEditTransaction() {
		modalError = '';
		notice = '';

		if (editingTransaction === null) {
			modalError = 'Transaction does not exist.';
			return;
		}

		if (!editAmount.trim()) {
			modalError = 'Amount is required.';
			return;
		}

		if (!editDate) {
			modalError = 'Transaction date is required.';
			return;
		}

		if (
			editingTransaction !== null
			&& !isTransfer(editingTransaction)
			&& editBudgetId !== 'none'
			&& editBudgetItemId === 'none'
		) {
			modalError = 'The selected budget does not have an item for this category.';
			return;
		}

		saving = true;

		try {
			if (isTransfer(editingTransaction)) {
				await updateTransfer(editingTransaction.transfer_id!, {
					amount: editAmount,
					transaction_date: editDate,
					payee: editPayee || null,
					notes: editNotes || null
				});
			} else {
				await updateTransaction(editingTransaction.transaction_id, {
					account_id: editAccountId,
					category_id: editCategoryId,
					budget_item_id: editBudgetId === 'none' || editBudgetItemId === 'none' ? 0 : Number(editBudgetItemId),
					amount: editAmount,
					transaction_date: editDate,
					payee: editPayee || null,
					notes: editNotes || null
				});
			}

			notice = isTransfer(editingTransaction) ? 'Transfer updated.' : 'Transaction updated.';
			closeEditModal();
			await loadPage();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
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

	onMount(loadPage);
</script>

<section class="flex flex-col gap-8 p-8">
	<div class="flex flex-wrap items-start justify-between gap-4">
		<div>
			<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Records</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight">Transactions</h1>
			<p class="text-muted mt-2 text-sm">
				Edit or delete transactions. Transfers update and delete as pairs.
			</p>
		</div>
		

		<div class="flex flex-wrap justify-end gap-2">
			<div class="pill">
				{filteredTransactions.length} of {transactions.length} transactions
			</div>
			<button class="primary-action" type="button" onclick={openCreateModal}>Add transaction</button>
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
		<div class="border-b px-6 py-5" style="border-color: var(--app-border)">
			<h2 class="text-base font-semibold">All transactions</h2>
			<p class="text-muted mt-1 text-sm">
				Showing transactions across active and archived accounts.
			</p>

			<div class="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
				<label class="grid gap-2">
					<span class="text-xs font-semibold uppercase tracking-widest text-muted">Search</span>
					<input bind:value={filterSearch} placeholder="Payee, note, account, category" />
				</label>

				<label class="grid gap-2">
					<span class="text-xs font-semibold uppercase tracking-widest text-muted">Account</span>
					<FilterCombobox
						id="transaction-filter-account"
						bind:value={filterAccountId}
						options={accountFilterOptions}
						placeholder="All accounts"
						searchPlaceholder="Type to filter accounts..."
					/>
				</label>

				<label class="grid gap-2">
					<span class="text-xs font-semibold uppercase tracking-widest text-muted">Type</span>
					<FilterCombobox
						id="transaction-filter-type"
						bind:value={filterType}
						options={typeFilterOptions}
						placeholder="All types"
						searchPlaceholder="Type to filter types..."
						onChange={(value) => filterType = value as 'all' | CategoryGroupType}
					/>
				</label>

				<label class="grid gap-2">
					<span class="text-xs font-semibold uppercase tracking-widest text-muted">Category group</span>
					<FilterCombobox
						id="transaction-filter-group"
						bind:value={filterCategoryGroupId}
						options={groupFilterOptions}
						placeholder="All groups"
						searchPlaceholder="Type to filter groups..."
					/>
				</label>

				<label class="grid gap-2">
					<span class="text-xs font-semibold uppercase tracking-widest text-muted">Category</span>
					<FilterCombobox
						id="transaction-filter-category"
						bind:value={filterCategoryId}
						options={categoryFilterOptions}
						placeholder="All categories"
						searchPlaceholder="Type to filter categories..."
					/>
				</label>
			</div>
		</div>

		<TransactionsTable
			transactions={filteredTransactions}
			{loading}
			{formatDate}
			{formatMoney}
			{accountName}
			{categoryName}
			{isTransfer}
			onEdit={openEditModal}
			onDelete={removeTransaction}
		/>
	</div>
</section>

{#if showCreateModal}
	<CreateTransactionModal
		accounts={activeAccounts}
		{budgetItems}
		{budgets}
		{categories}
		categoryGroups={categoryGroups}
		bind:mode={createMode}
		bind:accountId={createAccountId}
		bind:toAccountId={createToAccountId}
		bind:categoryGroupId={createCategoryGroupId}
		bind:categoryId={createCategoryId}
		bind:budgetId={createBudgetId}
		bind:budgetItemId={createBudgetItemId}
		bind:amount={createAmount}
		bind:transactionDate={createDate}
		bind:payee={createPayee}
		bind:notes={createNotes}
		error={modalError}
		{saving}
		{categoryName}
		onClose={closeCreateModal}
		onSubmit={submitCreateTransaction}
	/>
{/if}

{#if showEditModal && editingTransaction}
	<TransactionModal
		transaction={editingTransaction}
		{accounts}
		{budgets}
		{budgetItems}
		{categories}
		bind:accountId={editAccountId}
		bind:categoryId={editCategoryId}
		bind:budgetId={editBudgetId}
		bind:budgetItemId={editBudgetItemId}
		bind:amount={editAmount}
		bind:transactionDate={editDate}
		bind:payee={editPayee}
		bind:notes={editNotes}
		error={modalError}
		{saving}
		{categoryName}
		onClose={closeEditModal}
		onSubmit={submitEditTransaction}
	/>
{/if}
