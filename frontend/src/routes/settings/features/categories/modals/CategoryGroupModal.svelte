<script lang="ts">
	import type { CategoryGroupType } from '$lib/api/categories';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';

	const categoryGroupTypeOptions = [
		{ value: 'expense', label: 'Expense' },
		{ value: 'income', label: 'Income' },
		{ value: 'transfer', label: 'Transfer' }
	];

	let {
		groupName = $bindable(),
		groupType = $bindable(),
		error,
		saving,
		eyebrow = 'Make category group',
		title = 'New category group',
		submitLabel = 'Create group',
		savingLabel = 'Creating...',
		lockType = false,
		onClose,
		onSubmit
	} = $props<{
		groupName: string;
		groupType: CategoryGroupType;
		error: string;
		saving: boolean;
		eyebrow?: string;
		title?: string;
		submitLabel?: string;
		savingLabel?: string;
		lockType?: boolean;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">{eyebrow}</p>
				<h2 class="mt-1 text-xl font-bold">{title}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Category group name</span>
			<input bind:value={groupName} placeholder="Food, Bills, Side income" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category group type</span>
			<SearchableCombobox
				bind:value={groupType}
				options={categoryGroupTypeOptions}
				placeholder="Select a category group type"
				searchPlaceholder="Search category group types..."
				disabled={lockType}
			/>
			{#if lockType}
				<p class="text-muted text-xs">Group type cannot be changed after creation.</p>
			{/if}
		</label>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<button class="primary-action mt-6 w-full" type="submit" disabled={saving}>
			{saving ? savingLabel : submitLabel}
		</button>
	</form>
</div>
