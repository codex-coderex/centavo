import { callApi } from './client';

export type Transaction = {
	transaction_id: number;
	account_id: number;
	category_id: number;
	budget_item_id?: number | null;
	recurring_rule_id?: number | null;
	payee?: string | null;
	notes?: string | null;
	amount_minor: number;
	transaction_date: string;
	created_at: string;
	transfer_id?: number | null;
};

export function getTransactionsByUser(userId: number) {
	return callApi<Transaction[]>('get_transactions_by_user', userId);
}

export function getTransactionsByAccount(accountId: number) {
	return callApi<Transaction[]>('get_transactions_by_account', accountId);
}

export function getTransaction(transactionId: number) {
	return callApi<Transaction | null>('get_transaction', transactionId);
}

export function createTransaction(payload: {
	account_id: number;
	amount: number | string;
	transaction_date: string;
	category_id: number;
	budget_item_id?: number | null;
	payee?: string | null;
	notes?: string | null;
	recurring_rule_id?: number | null;
}) {
	return callApi<{ transaction_id: number }>(
		'create_transaction',
		payload.account_id,
		payload.amount,
		payload.transaction_date,
		payload.category_id,
		payload.budget_item_id ?? null,
		payload.payee ?? null,
		payload.notes ?? null,
		payload.recurring_rule_id ?? null
	);
}

export function createTransfer(payload: {
	from_account_id: number;
	to_account_id: number;
	amount: number | string;
	transaction_date: string;
	category_id: number;
	payee?: string | null;
	notes?: string | null;
}) {
	return callApi<{
		transfer_id: number;
		debit_transaction_id: number;
		credit_transaction_id: number;
	}>(
		'create_transfer',
		payload.from_account_id,
		payload.to_account_id,
		payload.amount,
		payload.transaction_date,
		payload.category_id,
		payload.payee ?? 'Transfer',
		payload.notes ?? null
	);
}

export function updateTransaction(
	transactionId: number,
	payload: {
		account_id?: number | null;
		amount?: number | string | null;
		transaction_date?: string | null;
		category_id?: number | null;
		budget_item_id?: number | null;
		payee?: string | null;
		notes?: string | null;
		recurring_rule_id?: number | null;
	} = {}
) {
	return callApi<{ status: string }>(
		'update_transaction',
		transactionId,
		payload.account_id ?? null,
		payload.amount ?? null,
		payload.transaction_date ?? null,
		payload.category_id ?? null,
		payload.budget_item_id ?? null,
		payload.payee ?? null,
		payload.notes ?? null,
		payload.recurring_rule_id ?? null
	);
}

export function deleteTransaction(transactionId: number) {
	return callApi<{ status: string }>('delete_transaction', transactionId);
}

export function updateTransfer(
	transferId: number,
	payload: {
		amount?: number | string | null;
		transaction_date?: string | null;
		payee?: string | null;
		notes?: string | null;
	} = {}
) {
	return callApi<{ status: string }>(
		'update_transfer',
		transferId,
		payload.amount ?? null,
		payload.transaction_date ?? null,
		payload.payee ?? null,
		payload.notes ?? null
	);
}

export function deleteTransfer(transferId: number) {
	return callApi<{ status: string }>('delete_transfer', transferId);
}
