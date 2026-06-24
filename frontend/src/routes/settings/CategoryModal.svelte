<script lang="ts">
	import type {
		CategoryGroup,
		CategoryGroupType
	} from '$lib/api/categories';

	let {
		categoryName = $bindable(),
		categoryType = $bindable(),
		selectedGroupId = $bindable(),
		error,
		groups,
		saving,
		onClose,
		onSubmit
	} = $props<{
		categoryName: string;
		categoryType: CategoryGroupType;
		selectedGroupId: number | null;
		error: string;
		groups: CategoryGroup[];
		saving: boolean;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	let groupsForCategoryType = $derived(
		groups.filter((group: CategoryGroup) => group.type === categoryType && group.is_active)
	);

	$effect(() => {
		if (!groupsForCategoryType.some((group: CategoryGroup) => group.group_id === selectedGroupId)) {
			selectedGroupId = groupsForCategoryType[0]?.group_id ?? null;
		}
	});
</script>

<div class="modal-backdrop">
	<form
		class="modal-card"
		onsubmit={(event) => {
			event.preventDefault();
			onSubmit();
		}}
	>
		<div class="flex items-start justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Make category</p>
				<h2 class="mt-1 text-xl font-bold">New category</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Category name</span>
			<input bind:value={categoryName} placeholder="Groceries, Rent, Salary" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category group type</span>
			<select class="combobox" bind:value={categoryType}>
				<option value="expense">Expense</option>
				<option value="income">Income</option>
				<option value="transfer">Transfer</option>
			</select>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category group</span>
			<select class="combobox" bind:value={selectedGroupId} disabled={groupsForCategoryType.length === 0}>
				{#if groupsForCategoryType.length === 0}
					<option value={null}>No active {categoryType} groups</option>
				{/if}
				{#each groupsForCategoryType as group}
					<option value={group.group_id}>{group.name}</option>
				{/each}
			</select>
			<p class="text-muted text-xs">
				Only active {categoryType} category groups are shown here.
			</p>
		</label>

		{#if groupsForCategoryType.length === 0}
			<p class="text-muted mt-3 text-sm">
				No {categoryType} groups yet. Make a category group first.
			</p>
		{/if}

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<button class="primary-action mt-6 w-full" type="submit" disabled={saving || groupsForCategoryType.length === 0}>
			Create category
		</button>
	</form>
</div>
