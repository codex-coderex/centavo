<script lang="ts">
	import {
		createCategory,
		getCategoryGroups,
		type CategoryGroup
	} from '$lib/api/categories';
	import { onMount } from 'svelte';

	let { isOpen = $bindable(), userId, onCreated } = $props<{
		isOpen: boolean;
		userId: number;
		onCreated: () => void;
	}>();

	let groups: CategoryGroup[] = $state([]);
	let loadingGroups = $state(true);
	let saving = $state(false);
	let error = $state('');

	let name = $state('');
	let groupId: number | null = $state(null);

	async function loadGroups() {
		try {
			groups = await getCategoryGroups(userId);
			// Auto-select the first group if none is selected
			if (groups.length > 0) {
				groupId = groups[0].group_id;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loadingGroups = false;
		}
	}

	async function submitCategory() {
		error = '';

		if (!name.trim()) {
			error = 'Category name is required.';
			return;
		}

		if (groupId === null) {
			error = 'Please select a group.';
			return;
		}

		saving = true;

		try {
			await createCategory({
				group_id: groupId,
				name: name.trim()
			});

			name = '';
			isOpen = false;
			onCreated(); // Tell the parent page to refresh categories
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	function close() {
		isOpen = false;
		name = '';
		error = '';
	}

	$effect(() => {
		if (isOpen) {
			loadGroups();
		}
	});
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
		<div class="w-full max-w-md rounded-2xl border border-slate-800/60 bg-slate-900 p-6 shadow-xl">
			<div class="mb-6 flex items-center justify-between">
				<h2 class="text-lg font-semibold text-slate-100">Quick Add Category</h2>
				<button
					class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-800 hover:text-slate-200"
					onclick={close}
					type="button"
					aria-label="Close category modal"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>

			{#if error}
				<div class="mb-4 rounded-xl border border-red-500/30 bg-red-950/30 p-4 text-sm text-red-200">
					{error}
				</div>
			{/if}

			<form
				onsubmit={(e) => {
					e.preventDefault();
					submitCategory();
				}}
				class="flex flex-col gap-4"
			>
				<label class="grid gap-2">
					<span class="text-sm font-medium text-slate-300">Category Name</span>
					<input
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
						bind:value={name}
						placeholder="e.g., Groceries"
					/>
				</label>

				<label class="grid gap-2">
					<span class="text-sm font-medium text-slate-300">Group</span>
					{#if loadingGroups}
						<p class="text-sm text-slate-500">Loading groups...</p>
					{:else}
						<select
							class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
							bind:value={groupId}
						>
							{#each groups as group}
								<option value={group.group_id}>{group.name} ({group.type})</option>
							{/each}
						</select>
					{/if}
				</label>

				<div class="mt-4 flex gap-3">
					<button
						class="flex-1 rounded-lg border border-slate-700 bg-transparent px-4 py-2.5 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
						type="button"
						onclick={close}
						disabled={saving}
					>
						Cancel
					</button>
					<button
						class="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
						type="submit"
						disabled={saving}
					>
						{saving ? 'Saving...' : 'Save Category'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
