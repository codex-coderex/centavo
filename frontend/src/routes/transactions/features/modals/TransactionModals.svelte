<script lang="ts">
	import type { Account, AccountType } from '$lib/api/accounts';
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';
	import {
		addTagToTransaction,
		removeTagFromTransaction,
		type Tag
	} from '$lib/api/tags';
	import {
		createTransaction,
		createTransfer,
		updateTransaction,
		updateTransfer,
		type Transaction
	} from '$lib/api/transactions';
	import CreateTransactionModal from './CreateTransactionModal.svelte';
	import { dateInputValue, todayInputValue } from '../utils/transactionFormat';

	let {
		showCreateModal = $bindable(),
		showEditModal = $bindable(),
		editingTransaction = $bindable(),
		activeAccounts,
		accounts,
		transactions,
		budgets,
		budgetItems,
		categories,
		categoryGroups,
		tags,
		transactionTagIds,
		categoryName,
		onRefresh,
		onNotice
	} = $props<{
		showCreateModal: boolean;
		showEditModal: boolean;
		editingTransaction: Transaction | null;
		activeAccounts: Account[];
		accounts: Account[];
		transactions: Transaction[];
		budgets: Budget[];
		budgetItems: BudgetItem[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		tags: Tag[];
		transactionTagIds: Record<number, number[]>;
		categoryName: (categoryId: number) => string;
		onRefresh: () => Promise<void>;
		onNotice: (message: string) => void;
	}>();

	let saving = $state(false);
	let modalError = $state('');
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
	let createTagIds: number[] = $state([]);

	let editAccountId = $state(0);
	let editToAccountId = $state(0);
	let editMode: CategoryGroupType = $state('expense');
	let editCategoryGroupId = $state(0);
	let editCategoryId = $state(0);
	let editBudgetId = $state('none');
	let editBudgetItemId = $state('none');
	let editAmount = $state('');
	let editDate = $state('');
	let editPayee = $state('');
	let editNotes = $state('');
	let editTagIds: number[] = $state([]);

	let wasCreateOpen = $state(false);
	let lastEditingTransactionId = $state<number | null>(null);

	const balanceProtectedAccountTypes: AccountType[] = [
		'checking',
		'savings',
		'cash',
		'investment',
		'other_asset'
	];

	function isTransfer(transaction: Transaction) {
		return transaction.transfer_id !== null && transaction.transfer_id !== undefined;
	}

	function amountToMinorUnits(value: string) {
		return Math.round(Number(value) * 100);
	}

	function groupsForType(type: CategoryGroupType) {
		return categoryGroups.filter((group: CategoryGroup) => group.type === type);
	}

	function accountById(accountId: number) {
		return accounts.find((account: Account) => account.account_id === accountId)
			?? activeAccounts.find((account: Account) => account.account_id === accountId);
	}

	function wouldDropBalanceBelowZero(accountId: number, balanceDeltaMinor: number) {
		const account = accountById(accountId);
		if (!account || !balanceProtectedAccountTypes.includes(account.type)) return false;

		return account.current_balance_minor + balanceDeltaMinor < 0;
	}

	function budgetIdForBudgetItem(budgetItemId: number | null | undefined) {
		if (budgetItemId == null) return 'none';

		const item = budgetItems.find((row: BudgetItem) => row.budget_item_id === budgetItemId);
		return item ? String(item.budget_id) : 'none';
	}

	function categoryGroupForCategory(categoryId: number) {
		const category = categories.find((row: Category) => row.category_id === categoryId);
		return categoryGroups.find((row: CategoryGroup) => row.group_id === category?.group_id);
	}

	function resetCreateModal() {
		modalError = '';
		createMode = 'expense';
		createAccountId = activeAccounts[0]?.account_id ?? 0;
		createToAccountId = activeAccounts.find((account: Account) => account.account_id !== createAccountId)?.account_id ?? 0;
		createCategoryGroupId = groupsForType('expense')[0]?.group_id ?? 0;
		createCategoryId = categories.find((category: Category) => category.group_id === createCategoryGroupId)?.category_id ?? 0;
		createBudgetId = 'none';
		createBudgetItemId = 'none';
		createAmount = '';
		createDate = todayInputValue();
		createPayee = '';
		createNotes = '';
		createTagIds = [];
	}

	function resetEditModal(transaction: Transaction) {
		const group = categoryGroupForCategory(transaction.category_id);
		const pairedTransferTransaction = isTransfer(transaction)
			? transactions.find(
					(row: Transaction) =>
						row.transfer_id === transaction.transfer_id
						&& row.transaction_id !== transaction.transaction_id
				)
			: null;

		modalError = '';
		editAccountId = transaction.account_id;
		editToAccountId = pairedTransferTransaction?.account_id ?? 0;
		editMode = group?.type ?? (transaction.amount_minor < 0 ? 'expense' : 'income');
		editCategoryGroupId = group?.group_id ?? 0;
		editCategoryId = transaction.category_id;
		editBudgetId = budgetIdForBudgetItem(transaction.budget_item_id);
		editBudgetItemId = transaction.budget_item_id ? String(transaction.budget_item_id) : 'none';
		editAmount = Math.abs(transaction.amount_minor / 100).toFixed(2);
		editDate = dateInputValue(transaction.transaction_date);
		editPayee = transaction.payee ?? '';
		editNotes = transaction.notes ?? '';
		editTagIds = transactionTagIds[transaction.transaction_id] ?? [];
	}

	async function syncTransactionTags(transactionId: number, nextTagIds: number[]) {
		const currentTagIds: number[] = transactionTagIds[transactionId] ?? [];
		const toAdd = nextTagIds.filter((tagId: number) => !currentTagIds.includes(tagId));
		const toRemove = currentTagIds.filter((tagId: number) => !nextTagIds.includes(tagId));

		await Promise.all([
			...toAdd.map((tagId: number) => addTagToTransaction(transactionId, tagId)),
			...toRemove.map((tagId: number) => removeTagFromTransaction(transactionId, tagId))
		]);
	}

	$effect(() => {
		if (showCreateModal && !wasCreateOpen) {
			resetCreateModal();
		}

		wasCreateOpen = showCreateModal;
	});

	$effect(() => {
		if (
			showEditModal
			&& editingTransaction
			&& editingTransaction.transaction_id !== lastEditingTransactionId
		) {
			lastEditingTransactionId = editingTransaction.transaction_id;
			resetEditModal(editingTransaction);
		}
	});

	function closeCreateModal() {
		showCreateModal = false;
		modalError = '';
		saving = false;
	}

	function closeEditModal() {
		showEditModal = false;
		editingTransaction = null;
		lastEditingTransactionId = null;
		modalError = '';
		saving = false;
	}

	async function submitCreateTransaction() {
		modalError = '';

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

		const createAmountMinor = amountToMinorUnits(createAmount);

		if (!Number.isFinite(createAmountMinor) || createAmountMinor <= 0) {
			modalError = 'Amount must be greater than zero.';
			return;
		}

		if (createMode === 'expense' && wouldDropBalanceBelowZero(createAccountId, -createAmountMinor)) {
			modalError = 'Insufficient available balance for this transaction.';
			return;
		}

		if (createMode === 'transfer' && wouldDropBalanceBelowZero(createAccountId, -createAmountMinor)) {
			modalError = 'Insufficient available balance in the source account.';
			return;
		}

		saving = true;

		try {
			if (createMode === 'transfer') {
				const result = await createTransfer({
					from_account_id: createAccountId,
					to_account_id: createToAccountId,
					category_id: createCategoryId,
					amount: createAmount,
					transaction_date: createDate,
					payee: createPayee || 'Transfer',
					notes: createNotes || null
				});
				await Promise.all([
					syncTransactionTags(result.debit_transaction_id, createTagIds),
					syncTransactionTags(result.credit_transaction_id, createTagIds)
				]);
			} else {
				const result = await createTransaction({
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
				await syncTransactionTags(result.transaction_id, createTagIds);
			}

			onNotice(createMode === 'transfer' ? 'Transfer created.' : 'Transaction created.');
			closeCreateModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function submitEditTransaction() {
		modalError = '';

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
			!isTransfer(editingTransaction)
			&& editMode === 'expense'
			&& editBudgetId !== 'none'
			&& editBudgetItemId === 'none'
		) {
			modalError = 'The selected budget does not have an item for this category.';
			return;
		}

		const editAmountMinor = amountToMinorUnits(editAmount);

		if (!Number.isFinite(editAmountMinor) || editAmountMinor <= 0) {
			modalError = 'Amount must be greater than zero.';
			return;
		}

		if (isTransfer(editingTransaction)) {
			const debitTransaction = editingTransaction.amount_minor < 0
				? editingTransaction
				: transactions.find(
					(row: Transaction) =>
						row.transfer_id === editingTransaction?.transfer_id
						&& row.amount_minor < 0
				);

			if (
				debitTransaction
				&& wouldDropBalanceBelowZero(
					debitTransaction.account_id,
					-editAmountMinor - debitTransaction.amount_minor
				)
			) {
				modalError = 'Insufficient available balance in the source account.';
				return;
			}
		} else {
			const nextAmountMinor = editMode === 'expense' ? -editAmountMinor : editAmountMinor;

			if (editAccountId === editingTransaction.account_id) {
				if (wouldDropBalanceBelowZero(editAccountId, nextAmountMinor - editingTransaction.amount_minor)) {
					modalError = 'Insufficient available balance for this transaction.';
					return;
				}
			} else {
				if (wouldDropBalanceBelowZero(editingTransaction.account_id, -editingTransaction.amount_minor)) {
					modalError = 'Insufficient available balance for this transaction.';
					return;
				}

				if (wouldDropBalanceBelowZero(editAccountId, nextAmountMinor)) {
					modalError = 'Insufficient available balance for this transaction.';
					return;
				}
			}
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
				const pairedTransferTransaction = transactions.find(
					(row: Transaction) =>
						row.transfer_id === editingTransaction?.transfer_id
						&& row.transaction_id !== editingTransaction.transaction_id
				);
				await Promise.all([
					syncTransactionTags(editingTransaction.transaction_id, editTagIds),
					pairedTransferTransaction
						? syncTransactionTags(pairedTransferTransaction.transaction_id, editTagIds)
						: Promise.resolve()
				]);
			} else {
				await updateTransaction(editingTransaction.transaction_id, {
					account_id: editAccountId,
					category_id: editCategoryId,
					budget_item_id: editMode !== 'expense' || editBudgetId === 'none' || editBudgetItemId === 'none' ? 0 : Number(editBudgetItemId),
					amount: editMode === 'expense' ? `-${editAmount}` : editAmount,
					transaction_date: editDate,
					payee: editPayee || null,
					notes: editNotes || null
				});
				await syncTransactionTags(editingTransaction.transaction_id, editTagIds);
			}

			onNotice(isTransfer(editingTransaction) ? 'Transfer updated.' : 'Transaction updated.');
			closeEditModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}
</script>

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
		{tags}
		bind:selectedTagIds={createTagIds}
		onClose={closeCreateModal}
		onSubmit={submitCreateTransaction}
	/>
{/if}

{#if showEditModal && editingTransaction}
	<CreateTransactionModal
		{accounts}
		{budgets}
		{budgetItems}
		{categories}
		{categoryGroups}
		bind:mode={editMode}
		bind:accountId={editAccountId}
		bind:toAccountId={editToAccountId}
		bind:categoryGroupId={editCategoryGroupId}
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
		{tags}
		bind:selectedTagIds={editTagIds}
		eyebrow={isTransfer(editingTransaction) ? 'Edit transfer' : 'Edit transaction'}
		title={editingTransaction.payee ?? 'No payee'}
		submitLabel="Save changes"
		savingLabel="Saving..."
		lockTransferStructure={isTransfer(editingTransaction)}
		onClose={closeEditModal}
		onSubmit={submitEditTransaction}
	/>
{/if}
