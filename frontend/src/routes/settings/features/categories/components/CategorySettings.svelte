<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createCategory,
		createCategoryGroup,
		getAllCategoriesForUser,
		getAllCategoryGroups,
		removeCategory,
		removeCategoryGroup,
		updateCategory,
		updateCategoryGroup,
		type Category,
		type CategoryGroup,
		type CategoryGroupType
	} from '$lib/api/categories';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
	import CategoryGroupModal from '../modals/CategoryGroupModal.svelte';
	import CategoryModal from '../modals/CategoryModal.svelte';

	const userId = 1;
	const categorySections: { type: CategoryGroupType; label: string }[] = [
		{ type: 'expense', label: 'Expenses' },
		{ type: 'income', label: 'Income' },
		{ type: 'transfer', label: 'Transfers' }
	];

	let groups: CategoryGroup[] = $state([]);
	let categories: Category[] = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let modalError = $state('');
	let notice = $state('');

	let showGroupModal = $state(false);
	let showCategoryModal = $state(false);
	let editingGroup: CategoryGroup | null = $state(null);

	let groupName = $state('');
	let groupType: CategoryGroupType = $state('expense');

	let categoryName = $state('');
	let categoryType: CategoryGroupType = $state('expense');
	let selectedGroupId = $state<number | null>(null);

	function categoriesForGroup(groupId: number) {
		return categories.filter((category: Category) => category.group_id === groupId);
	}

	function groupsForType(type: CategoryGroupType) {
		return groups.filter((group: CategoryGroup) => group.type === type);
	}

	function resetGroupModal() {
		groupName = '';
		groupType = 'expense';
		editingGroup = null;
	}

	function resetCategoryModal() {
		categoryName = '';
		categoryType = 'expense';
		selectedGroupId = groups.find((group: CategoryGroup) => group.type === 'expense' && group.is_active)?.group_id ?? null;
	}

	function openGroupModal() {
		error = '';
		modalError = '';
		notice = '';
		resetGroupModal();
		showGroupModal = true;
	}

	function openEditGroupModal(group: CategoryGroup) {
		error = '';
		modalError = '';
		notice = '';
		editingGroup = group;
		groupName = group.name;
		groupType = group.type;
		showGroupModal = true;
	}

	function openCategoryModal() {
		error = '';
		modalError = '';
		notice = '';
		resetCategoryModal();
		showCategoryModal = true;
	}

	function closeModals() {
		showGroupModal = false;
		showCategoryModal = false;
		editingGroup = null;
		modalError = '';
		saving = false;
	}

	async function loadCategories() {
		loading = true;
		error = '';

		try {
			const [groupRows, categoryRows] = await Promise.all([
				getAllCategoryGroups(userId),
				getAllCategoriesForUser(userId)
			]);

			groups = groupRows;
			categories = categoryRows;
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function submitGroup() {
		modalError = '';
		notice = '';

		if (!groupName.trim()) {
			modalError = 'Category group name is required.';
			return;
		}

		saving = true;

		try {
			if (editingGroup) {
				await updateCategoryGroup(editingGroup.group_id, {
					name: groupName.trim()
				});
				notice = 'Category group renamed.';
			} else {
				await createCategoryGroup({
					user_id: userId,
					name: groupName.trim(),
					type: groupType
				});
				notice = 'Category group created.';
			}

			closeModals();
			await loadCategories();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function submitCategory() {
		modalError = '';
		notice = '';

		if (!categoryName.trim()) {
			modalError = 'Category name is required.';
			return;
		}

		if (selectedGroupId === null) {
			modalError = `Create a ${categoryType} group first.`;
			return;
		}

		saving = true;

		try {
			await createCategory({
				group_id: selectedGroupId,
				name: categoryName.trim()
			});

			notice = 'Category created.';
			closeModals();
			await loadCategories();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function setCategoryActive(category: Category, isActive: boolean) {
		error = '';
		notice = '';

		try {
			await updateCategory(category.category_id, { is_active: isActive });
			notice = `Category ${isActive ? 'enabled' : 'disabled'}.`;
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function setGroupActive(group: CategoryGroup, isActive: boolean) {
		error = '';
		notice = '';

		try {
			await updateCategoryGroup(group.group_id, { is_active: isActive });
			notice = `Category group ${isActive ? 'enabled' : 'disabled'}.`;
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function deleteCustomCategory(category: Category) {
		if (category.is_system) {
			error = 'System categories can be disabled, but not deleted.';
			return;
		}

		if (!confirm(`Delete "${category.name}"?`)) return;

		error = '';
		notice = '';

		try {
			const result = await removeCategory(category.category_id);
			notice = `Category ${result.status}.`;
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function deleteCustomGroup(group: CategoryGroup) {
		if (group.is_system) {
			error = 'System category groups can be disabled, but not deleted.';
			return;
		}

		if (!confirm(`Delete "${group.name}" and its categories?`)) return;

		error = '';
		notice = '';

		try {
			const result = await removeCategoryGroup(group.group_id);
			notice = `Category group ${result.status}.`;
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadCategories);
</script>

<ToastOnChange {error} {notice} />

<section class="flex flex-col gap-4">
	<div class="dashboard-card overflow-hidden">
		<div class="flex flex-wrap items-start justify-between gap-4 border-b px-6 py-5" style="border-color: var(--app-border)">
			<div>
				<h2 class="text-lg font-semibold">Categories</h2>
				<p class="text-muted mt-1 text-sm">
					Disable system categories, re-enable greyed out categories, or delete custom categories.
				</p>
			</div>

			<div class="flex flex-wrap gap-2">
				<button class="secondary-action" type="button" onclick={openGroupModal}>Make category group</button>
				<button class="primary-action" type="button" onclick={openCategoryModal}>Make category</button>
			</div>
		</div>

		{#if loading}
			<p class="text-muted p-6 text-sm">Loading categories...</p>
		{:else}
			<div class="divide-y" style="border-color: var(--app-border)">
				{#each categorySections as section}
					<div>
						<div class="border-b px-6 py-4" style="border-color: var(--app-border); background: var(--app-surface-strong)">
							<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">
								{section.label}
							</p>
						</div>

						{#each groupsForType(section.type) as group}
							<div
								class="p-6"
								style="background: {group.is_active ? 'transparent' : 'rgba(126, 114, 101, 0.08)'}"
							>
								<div class="flex items-start justify-between gap-4">
									<div>
										<div class="flex flex-wrap items-center gap-2">
											<h3 class="font-semibold" class:text-muted={!group.is_active}>{group.name}</h3>
											<span class="pill">{group.is_system ? 'system' : 'custom'}</span>
											{#if !group.is_active}
												<span class="pill muted-pill">disabled</span>
											{/if}
										</div>
										<p class="text-muted mt-1 text-sm">
											{categoriesForGroup(group.group_id).length} categories
										</p>
									</div>

									<div class="flex flex-wrap justify-end gap-2">
										<button
											class="secondary-action"
											type="button"
											onclick={() => openEditGroupModal(group)}
										>
											Edit
										</button>

										<button
											class="secondary-action"
											type="button"
											onclick={() => setGroupActive(group, !group.is_active)}
										>
											{group.is_active ? 'Disable' : 'Enable'}
										</button>

										{#if !group.is_system}
											<button class="danger-action" type="button" onclick={() => deleteCustomGroup(group)}>
												Delete
											</button>
										{/if}
									</div>
								</div>

								<div class="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
									{#each categoriesForGroup(group.group_id) as category}
										{@const categoryEnabled = group.is_active && category.is_active}
										<div
											class="flex items-center justify-between gap-3 rounded-lg border px-3 py-2"
											style="border-color: var(--app-border); background: var(--app-surface-strong); opacity: {categoryEnabled ? '1' : '0.55'}"
										>
											<div class="min-w-0">
												<div class="flex items-center gap-2">
													<span
														class="h-2.5 w-2.5 rounded-full"
														style="background: {categoryEnabled ? 'var(--app-green)' : 'var(--app-muted)'}"
													></span>
													<span class="truncate text-sm font-medium" class:text-muted={!categoryEnabled}>
														{category.name}
													</span>
												</div>
												<p class="text-muted mt-1 text-xs">
													{category.is_system ? 'system' : 'custom'} · {!group.is_active ? 'disabled by group' : category.is_active ? 'enabled' : 'disabled'}
												</p>
											</div>

											<div class="flex shrink-0 gap-2">
												<button
													class="secondary-action"
													type="button"
													onclick={() => setCategoryActive(category, !category.is_active)}
												>
													{category.is_active ? 'Disable' : 'Enable'}
												</button>

												{#if !category.is_system}
													<button class="danger-action" type="button" onclick={() => deleteCustomCategory(category)}>
														Delete
													</button>
												{/if}
											</div>
										</div>
									{:else}
										<p class="text-muted text-sm">No categories in this group.</p>
									{/each}
								</div>
							</div>
						{:else}
							<div class="px-6 py-5">
								<p class="text-muted text-sm">No {section.label.toLowerCase()} category groups yet.</p>
							</div>
						{/each}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</section>

{#if showGroupModal}
	<CategoryGroupModal
		bind:groupName
		bind:groupType
		title={editingGroup ? 'Edit category group' : 'New category group'}
		eyebrow={editingGroup ? 'Rename category group' : 'Make category group'}
		submitLabel={editingGroup ? 'Save group' : 'Create group'}
		savingLabel={editingGroup ? 'Saving...' : 'Creating...'}
		lockType={editingGroup !== null}
		error={modalError}
		{saving}
		onClose={closeModals}
		onSubmit={submitGroup}
	/>
{/if}

{#if showCategoryModal}
	<CategoryModal
		bind:categoryName
		bind:categoryType
		bind:selectedGroupId
		error={modalError}
		{groups}
		{saving}
		onClose={closeModals}
		onSubmit={submitCategory}
	/>
{/if}
