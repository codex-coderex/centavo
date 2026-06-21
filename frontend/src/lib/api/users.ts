import { callApi } from './client';

export type User = {
	user_id: number;
	currency_code: string;
	name: string;
	created_at?: string;
};

export function getUsers() {
	return callApi<User[]>('get_users');
}

export function getUser(userId: number) {
	return callApi<User | null>('get_user', userId);
}

export function createUser(payload: { name: string; currency_code: string }) {
	return callApi<{ user_id: number }>(
		'create_user',
		payload.name,
		payload.currency_code
	);
}

export function updateUser(
	userId: number,
	payload: { name?: string; currency_code?: string } = {}
) {
	return callApi<void>(
		'update_user',
		userId,
		payload.name ?? null,
		payload.currency_code ?? null
	);
}