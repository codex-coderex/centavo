<script lang="ts">
	import type { CategoryGroupType } from '$lib/api/categories';

	let {
		groupName = $bindable(),
		groupType = $bindable(),
		error,
		saving,
		onClose,
		onSubmit
	} = $props<{
		groupName: string;
		groupType: CategoryGroupType;
		error: string;
		saving: boolean;
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Make category group</p>
				<h2 class="mt-1 text-xl font-bold">New category group</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Category group name</span>
			<input bind:value={groupName} placeholder="Food, Bills, Side income" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category group type</span>
			<select class="combobox" bind:value={groupType}>
				<option value="expense">Expense</option>
				<option value="income">Income</option>
				<option value="transfer">Transfer</option>
			</select>
		</label>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<button class="primary-action mt-6 w-full" type="submit" disabled={saving}>
			Create group
		</button>
	</form>
</div>
