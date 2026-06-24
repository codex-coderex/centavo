<script lang="ts">
	import type { BudgetPeriodType } from '$lib/api/budgets';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';

	let {
		name = $bindable(),
		period = $bindable(),
		startDate = $bindable(),
		endDate = $bindable(),
		error,
		saving,
		title,
		submitLabel,
		savingLabel,
		onClose,
		onSubmit
	} = $props<{
		name: string;
		period: BudgetPeriodType;
		startDate: string;
		endDate: string;
		error: string;
		saving: boolean;
		title: string;
		submitLabel: string;
		savingLabel: string;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	const periods: { value: BudgetPeriodType; label: string }[] = [
		{ value: 'weekly', label: 'Weekly' },
		{ value: 'monthly', label: 'Monthly' },
		{ value: 'quarterly', label: 'Quarterly' },
		{ value: 'yearly', label: 'Yearly' },
		{ value: 'custom', label: 'Custom' }
	];
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Budget</p>
				<h2 class="mt-1 text-xl font-bold">{title}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Budget name</span>
			<input bind:value={name} placeholder="June 2026" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Period</span>
			<SearchableCombobox
				bind:value={period}
				options={periods}
				placeholder="Select a period"
				searchPlaceholder="Search periods..."
			/>
		</label>

		<div class="mt-4 grid gap-4 sm:grid-cols-2">
			<label class="grid gap-2">
				<span class="text-sm font-medium">Start date</span>
				<input bind:value={startDate} type="date" />
			</label>

			<label class="grid gap-2">
				<span class="text-sm font-medium">End date</span>
				<input bind:value={endDate} type="date" />
			</label>
		</div>

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
