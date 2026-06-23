import { callApi } from './client';

export type AccountStatus = 'active' | 'archived';

export type Account = {
	account_id: number;
	user_id: number;
	name: string;
	type: string;
	opening_balance_minor: number;
	created_at: string;
	status: AccountStatus;
};

export function getAccounts(userId: number) {
	return callApi<Account[]>('get_accounts', userId);
}

export function getAccount(accountId: number) {
	return callApi<Account | null>('get_account', accountId);
}

export function createAccount(payload: {
	user_id: number;
	name: string;
	type: string;
	opening_balance?: number | string;
}) {
	return callApi<{ account_id: number }>(
		'create_account',
		payload.user_id,
		payload.name,
		payload.type,
		payload.opening_balance ?? 0
	);
}

export function updateAccount(
	accountId: number,
	payload: {
		name?: string;
		type?: string;
		opening_balance?: number | string | null;
		status?: AccountStatus;
	} = {}
) {
	return callApi<{ status: string }>(
		'update_account',
		accountId,
		payload.name ?? null,
		payload.type ?? null,
		payload.opening_balance ?? null,
		payload.status ?? null
	);
}

export function archiveAccount(accountId: number) {
	return callApi<{ status: string }>('archive_account', accountId);
}
