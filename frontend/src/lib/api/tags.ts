import { callApi } from './client';

export type Tag = {
	tag_id: number;
	user_id: number;
	name: string;
};

export function getTags(userId: number) {
	return callApi<Tag[]>('get_tags', userId);
}

export function getTag(tagId: number) {
	return callApi<Tag | null>('get_tag', tagId);
}

export function createTag(payload: { user_id: number; name: string }) {
	return callApi<{ tag_id: number }>('create_tag', payload.user_id, payload.name);
}

export function updateTag(tagId: number, payload: { name?: string | null } = {}) {
	return callApi<{ status: string }>('update_tag', tagId, payload.name ?? null);
}

export function deleteTag(tagId: number) {
	return callApi<{ status: string }>('delete_tag', tagId);
}

export function getTransactionTags(transactionId: number) {
	return callApi<Tag[]>('get_transaction_tags', transactionId);
}

export function addTagToTransaction(transactionId: number, tagId: number) {
	return callApi<{ status: string }>('add_tag_to_transaction', transactionId, tagId);
}

export function removeTagFromTransaction(transactionId: number, tagId: number) {
	return callApi<{ status: string }>('remove_tag_from_transaction', transactionId, tagId);
}
