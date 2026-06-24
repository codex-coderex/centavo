import { callApi } from './client';

export type CategoryGroupType = 'income' | 'expense' | 'transfer';

export type CategoryGroup = {
	group_id: number;
	user_id: number;
	name: string;
	type: CategoryGroupType;
	is_system: boolean;
	is_active: boolean;
};

export type Category = {
	category_id: number;
	group_id: number;
	name: string;
	is_system: boolean;
	is_active: boolean;
};

export function getCategoryGroups(userId: number) {
	return callApi<CategoryGroup[]>('get_category_groups', userId);
}

export function getAllCategoryGroups(userId: number) {
	return callApi<CategoryGroup[]>('get_all_category_groups', userId);
}

export function getCategories(groupId: number) {
	return callApi<Category[]>('get_categories', groupId);
}

export function getAllCategories(userId: number) {
	return callApi<Category[]>('get_all_categories', userId);
}

export function getAllCategoriesForUser(userId: number) {
	return callApi<Category[]>('get_all_categories_for_user', userId);
}

export function createCategoryGroup(payload: {
	user_id: number;
	name: string;
	type: CategoryGroupType;
}) {
	return callApi<{ group_id: number }>(
		'create_category_group',
		payload.user_id,
		payload.name,
		payload.type
	);
}

export function createCategory(payload: { group_id: number; name: string }) {
	return callApi<{ category_id: number }>(
		'create_category',
		payload.group_id,
		payload.name
	);
}

export function updateCategoryGroup(
	groupId: number,
	payload: {
		name?: string | null;
		type?: CategoryGroupType | null;
		is_active?: boolean | null;
	} = {}
) {
	return callApi<{ status: string }>(
		'update_category_group',
		groupId,
		payload.name ?? null,
		payload.type ?? null,
		payload.is_active ?? null
	);
}

export function updateCategory(
	categoryId: number,
	payload: { name?: string | null; is_active?: boolean | null } = {}
) {
	return callApi<{ status: string }>(
		'update_category',
		categoryId,
		payload.name ?? null,
		payload.is_active ?? null
	);
}

export function deactivateCategory(categoryId: number) {
	return callApi<{ status: string }>('deactivate_category', categoryId);
}

export function deactivateCategoryGroup(groupId: number) {
	return callApi<{ status: string }>('deactivate_category_group', groupId);
}

export function removeCategory(categoryId: number) {
	return callApi<{ status: string }>('remove_category', categoryId);
}

export function removeCategoryGroup(groupId: number) {
	return callApi<{ status: string }>('remove_category_group', groupId);
}
