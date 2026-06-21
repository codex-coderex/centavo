<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createCategory,
		createCategoryGroup,
		getAllCategories,
		getCategoryGroups,
		removeCategory,
		removeCategoryGroup,
		type Category,
		type CategoryGroup,
		type CategoryGroupType
	} from '$lib/api/categories';

	const userId = 1;

	let groups: CategoryGroup[] = $state([]);
	let categories: Category[] = $state([]);
	let loading = $state(true);
	let error = $state('');
	let notice = $state('');

	let groupName = $state('');
	let groupType: CategoryGroupType = $state('expense');

	let selectedGroupId = $state<number | null>(null);
	let categoryName = $state('');
	let categoryColor = $state('#64748b');

	function categoriesForGroup(groupId: number) {
		return categories.filter((category) => category.group_id === groupId);
	}

	async function loadCategories() {
		loading = true;
		error = '';
		notice = '';

		try {
			const [groupRows, categoryRows] = await Promise.all([
				getCategoryGroups(userId),
				getAllCategories(userId)
			]);

			groups = groupRows;
			categories = categoryRows;

			if (selectedGroupId === null && groupRows.length > 0) {
				selectedGroupId = groupRows[0].group_id;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function submitGroup() {
		error = '';
		notice = '';

		try {
			await createCategoryGroup({
				user_id: userId,
				name: groupName,
				type: groupType
			});

			groupName = '';
			groupType = 'expense';
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function submitCategory() {
		error = '';
		notice = '';

		if (selectedGroupId === null) {
			error = 'Create a category group first.';
			return;
		}

		try {
			await createCategory({
				group_id: selectedGroupId,
				name: categoryName,
				color: categoryColor
			});

			categoryName = '';
			categoryColor = '#64748b';
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function removeOneCategory(categoryId: number) {
		error = '';
		notice = '';

		try {
			const result = await removeCategory(categoryId);
			notice = `Category ${result.status}.`;
			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function removeOneGroup(groupId: number) {
		error = '';
		notice = '';

		try {
			const result = await removeCategoryGroup(groupId);
			notice = `Category group ${result.status}.`;

			if (selectedGroupId === groupId) {
				selectedGroupId = null;
			}

			await loadCategories();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadCategories);
</script>

<main class="min-h-screen bg-slate-950 p-8 text-slate-100">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">Categories</h1>
			<p class="mt-1 text-sm text-slate-400">
				Manage income and expense groups, then add categories inside them.
			</p>
		</div>

		<a class="text-sm text-slate-300 underline" href="/">Home</a>
	</div>

	{#if error}
		<div class="mt-4 rounded-lg border border-red-500/40 bg-red-950/40 p-4 text-red-200">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="mt-4 rounded-lg border border-emerald-500/40 bg-emerald-950/40 p-4 text-emerald-200">
			{notice}
		</div>
	{/if}

	<div class="mt-6 grid gap-6 lg:grid-cols-[360px_1fr]">
		<section class="space-y-4">
			<form
				class="rounded-xl border border-slate-800 bg-slate-900 p-4"
				onsubmit={(event) => {
					event.preventDefault();
					submitGroup();
				}}
			>
				<h2 class="font-semibold">New category group</h2>

				<label class="mt-3 grid gap-1">
					<span class="text-sm text-slate-300">Group name</span>
					<input
						class="rounded border border-slate-700 bg-slate-950 px-3 py-2"
						bind:value={groupName}
						placeholder="Bills, Food, Income"
					/>
				</label>

				<label class="mt-3 grid gap-1">
					<span class="text-sm text-slate-300">Type</span>
					<select
						class="rounded border border-slate-700 bg-slate-950 px-3 py-2"
						bind:value={groupType}
					>
						<option value="expense">Expense</option>
						<option value="income">Income</option>
					</select>
				</label>

				<button
					class="mt-4 w-full rounded bg-indigo-500 px-4 py-2 font-semibold text-white hover:bg-indigo-400"
					type="submit"
				>
					Create group
				</button>
			</form>

			<form
				class="rounded-xl border border-slate-800 bg-slate-900 p-4"
				onsubmit={(event) => {
					event.preventDefault();
					submitCategory();
				}}
			>
				<h2 class="font-semibold">New category</h2>

				<label class="mt-3 grid gap-1">
					<span class="text-sm text-slate-300">Group</span>
					<select
						class="rounded border border-slate-700 bg-slate-950 px-3 py-2"
						bind:value={selectedGroupId}
					>
						{#each groups as group}
							<option value={group.group_id}>
								{group.name} ({group.type})
							</option>
						{/each}
					</select>
				</label>

				<label class="mt-3 grid gap-1">
					<span class="text-sm text-slate-300">Category name</span>
					<input
						class="rounded border border-slate-700 bg-slate-950 px-3 py-2"
						bind:value={categoryName}
						placeholder="Groceries, Rent, Salary"
					/>
				</label>

				<label class="mt-3 grid gap-1">
					<span class="text-sm text-slate-300">Color</span>
					<input
						class="h-10 rounded border border-slate-700 bg-slate-950 px-2"
						type="color"
						bind:value={categoryColor}
					/>
				</label>

				<button
					class="mt-4 w-full rounded bg-indigo-500 px-4 py-2 font-semibold text-white hover:bg-indigo-400"
					type="submit"
				>
					Create category
				</button>
			</form>
		</section>

		<section class="rounded-xl border border-slate-800 bg-slate-900">
			<div class="border-b border-slate-800 p-4">
				<h2 class="font-semibold">Category groups</h2>
			</div>

			{#if loading}
				<p class="p-4 text-slate-300">Loading...</p>
			{:else}
				<div class="divide-y divide-slate-800">
					{#each groups as group}
						<div class="p-4">
							<div class="flex items-start justify-between gap-4">
								<div>
									<div class="flex items-center gap-2">
										<h3 class="font-semibold">{group.name}</h3>
										<span
											class="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300"
										>
											{group.type}
										</span>
										{#if group.is_system}
											<span
												class="rounded-full bg-indigo-950 px-2 py-0.5 text-xs text-indigo-200"
											>
												system
											</span>
										{/if}
									</div>

									<p class="mt-1 text-sm text-slate-400">
										{categoriesForGroup(group.group_id).length} categories
									</p>
								</div>

								<button
									class="text-sm text-red-300 underline"
									type="button"
									onclick={() => removeOneGroup(group.group_id)}
								>
									Remove
								</button>
							</div>

							<div class="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
								{#each categoriesForGroup(group.group_id) as category}
									<div
										class="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 px-3 py-2"
									>
										<div class="flex min-w-0 items-center gap-2">
											<span
												class="h-3 w-3 rounded-full"
												style={`background: ${category.color ?? '#64748b'}`}
											></span>
											<span class="truncate text-sm">{category.name}</span>
											{#if category.is_system}
												<span class="text-xs text-indigo-300">system</span>
											{/if}
										</div>

										<button
											class="ml-3 text-xs text-red-300 underline"
											type="button"
											onclick={() => removeOneCategory(category.category_id)}
										>
											Remove
										</button>
									</div>
								{:else}
									<p class="text-sm text-slate-500">No categories in this group.</p>
								{/each}
							</div>
						</div>
					{:else}
						<p class="p-4 text-slate-400">No category groups yet.</p>
					{/each}
				</div>
			{/if}
		</section>
	</div>
</main>