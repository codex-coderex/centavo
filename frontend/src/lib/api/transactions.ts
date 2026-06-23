import { callApi } from './client';

export type Transaction = {
	transaction_id: number;
	account_id: number;
	category_id?: number | null;
	recurring_rule_id?: number | null;
	payee?: string | null;
	notes?: string | null;
	amount: number | string;
	transaction_date: string;
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
	category_id?: number | null;
	payee?: string | null;
	notes?: string | null;
	recurring_rule_id?: number | null;
}) {
	return callApi<{ transaction_id: number }>(
		'create_transaction',
		payload.account_id,
		payload.amount,
		payload.transaction_date,
		payload.category_id ?? null,
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
	payee?: string | null;
	notes?: string | null;
}) {
	return callApi<{
		debit_transaction_id: number;
		credit_transaction_id: number;
	}>(
		'create_transfer',
		payload.from_account_id,
		payload.to_account_id,
		payload.amount,
		payload.transaction_date,
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
		payee?: string | null;
		notes?: string | null;
		recurring_rule_id?: number | null;
	} = {}
) {
	return callApi<void>(
		'update_transaction',
		transactionId,
		payload.account_id ?? null,
		payload.amount ?? null,
		payload.transaction_date ?? null,
		payload.category_id ?? null,
		payload.payee ?? null,
		payload.notes ?? null,
		payload.recurring_rule_id ?? null
	);
}

export function deleteTransaction(transactionId: number) {
	return callApi<void>('delete_transaction', transactionId);
}
