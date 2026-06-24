<script lang="ts">
	import type { Category } from '$lib/api/categories';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';
	import { sanitizeAmountInput } from '../utils/budgetFormat';

	let {
		categoryId = $bindable(),
		plannedAmount = $bindable(),
		rolloverEnabled = $bindable(),
		categories,
		error,
		saving,
		title,
		submitLabel,
		savingLabel,
		onClose,
		onSubmit
	} = $props<{
		categoryId: number;
		plannedAmount: string;
		rolloverEnabled: boolean;
		categories: Category[];
		error: string;
		saving: boolean;
		title: string;
		submitLabel: string;
		savingLabel: string;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	let categoryOptions = $derived(
		categories.map((category: Category) => ({
			value: String(category.category_id),
			label: category.name
		}))
	);

	function handleAmountInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = sanitizeAmountInput(input.value);

		plannedAmount = next;
		input.value = next;
	}
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Budget item</p>
				<h2 class="mt-1 text-xl font-bold">{title}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Category</span>
			<SearchableCombobox
				value={String(categoryId)}
				options={categoryOptions}
				placeholder="Select a category"
				searchPlaceholder="Search categories..."
				disabled={categories.length === 0}
				onChange={(value) => categoryId = Number(value)}
			/>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Planned amount</span>
			<input bind:value={plannedAmount} inputmode="decimal" placeholder="0.00" oninput={handleAmountInput} />
		</label>

		<label class="mt-4 flex items-center justify-between gap-4 rounded-xl border p-3" style="border-color: var(--app-border)">
			<span>
				<span class="block text-sm font-medium">Rollover</span>
				<span class="text-muted text-xs">Carry unused planned amount forward.</span>
			</span>
			<input bind:checked={rolloverEnabled} type="checkbox" />
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
