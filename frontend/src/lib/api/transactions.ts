import { callApi } from './client';

export type TransactionStatus = 'pending' | 'cleared' | 'void';

export type Transaction = {
	transaction_id: number;
	account_id: number;
	category_id: number;
	recurring_id?: number | null;
	transfer_pair_id?: number | null;
	goal_id?: number | null;
	merchant?: string | null;
	amount_minor: number;
	txn_date: string;
	status: TransactionStatus;
	needs_review: boolean;
	note?: string | null;
	updated_at?: string | null;
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
	txn_date: string;
	category_id: number;
	merchant?: string | null;
	note?: string | null;
	goal_id?: number | null;
	recurring_id?: number | null;
}) {
	return callApi<{ transaction_id: number }>(
		'create_transaction',
		payload.account_id,
		payload.amount,
		payload.txn_date,
		payload.category_id,
		payload.merchant ?? null,
		payload.note ?? null,
		payload.goal_id ?? null,
		payload.recurring_id ?? null
	);
}

export function createTransfer(payload: {
	from_account_id: number;
	to_account_id: number;
	amount: number | string;
	txn_date: string;
	category_id: number;
}) {
	return callApi<{
		debit_transaction_id: number;
		credit_transaction_id: number;
	}>(
		'create_transfer',
		payload.from_account_id,
		payload.to_account_id,
		payload.amount,
		payload.txn_date,
		payload.category_id
	);
}

export function updateTransaction(
	transactionId: number,
	payload: {
		merchant?: string | null;
		amount?: number | string | null;
		category_id?: number | null;
		note?: string | null;
		status?: TransactionStatus | null;
		needs_review?: boolean | null;
		txn_date?: string | null;
	} = {}
) {
	return callApi<void>(
		'update_transaction',
		transactionId,
		payload.merchant ?? null,
		payload.amount ?? null,
		payload.category_id ?? null,
		payload.note ?? null,
		payload.status ?? null,
		payload.needs_review ?? null,
		payload.txn_date ?? null
	);
}

export function flagForReview(transactionId: number) {
	return callApi<void>('flag_for_review', transactionId);
}