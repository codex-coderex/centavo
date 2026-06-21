import { callApi } from './client';

export type AccountStatus = 'active' | 'archived';

export type Account = {
	account_id: number;
	user_id: number;
	name: string;
	type: string;
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
}) {
	return callApi<{ account_id: number }>(
		'create_account',
		payload.user_id,
		payload.name,
		payload.type
	);
}

export function updateAccount(
	accountId: number,
	payload: {
		name?: string;
		type?: string;
		status?: AccountStatus;
	} = {}
) {
	return callApi<void>(
		'update_account',
		accountId,
		payload.name ?? null,
		payload.type ?? null,
		payload.status ?? null
	);
}

export function archiveAccount(accountId: number) {
	return callApi<void>('archive_account', accountId);
}