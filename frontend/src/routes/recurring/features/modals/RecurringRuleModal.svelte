<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';
	import type { FrequencyUnit } from '$lib/api/recurring';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';
	import { sanitizeSignedAmount } from '../utils/recurringFormat';

	let {
		mode = $bindable(),
		accounts,
		categories,
		categoryGroups,
		accountId = $bindable(),
		categoryGroupId = $bindable(),
		categoryId = $bindable(),
		name = $bindable(),
		amount = $bindable(),
		interval = $bindable(),
		frequencyUnit = $bindable(),
		nextDueDate = $bindable(),
		endDate = $bindable(),
		error,
		saving,
		title,
		submitLabel,
		savingLabel,
		onClose,
		onSubmit
	} = $props<{
		mode: CategoryGroupType;
		accounts: Account[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		accountId: number;
		categoryGroupId: number;
		categoryId: number;
		name: string;
		amount: string;
		interval: number;
		frequencyUnit: FrequencyUnit;
		nextDueDate: string;
		endDate: string;
		error: string;
		saving: boolean;
		title: string;
		submitLabel: string;
		savingLabel: string;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	const frequencyOptions: { value: FrequencyUnit; label: string }[] = [
		{ value: 'day', label: 'Day(s)' },
		{ value: 'week', label: 'Week(s)' },
		{ value: 'month', label: 'Month(s)' },
		{ value: 'year', label: 'Year(s)' }
	];

	let categoryGroupsForMode = $derived(
		categoryGroups.filter((group: CategoryGroup) => group.type === mode && group.is_active)
	);
	let categoriesForGroup = $derived(
		categories.filter((category: Category) => category.group_id === categoryGroupId && category.is_active)
	);
	let accountOptions = $derived(
		accounts.map((account: Account) => ({
			value: String(account.account_id),
			label: account.name
		}))
	);
	let categoryGroupOptions = $derived(
		categoryGroupsForMode.map((group: CategoryGroup) => ({
			value: String(group.group_id),
			label: group.name
		}))
	);
	let categoryOptions = $derived(
		categoriesForGroup.map((category: Category) => ({
			value: String(category.category_id),
			label: category.name
		}))
	);

	$effect(() => {
		if (!categoryGroupsForMode.some((group: CategoryGroup) => group.group_id === categoryGroupId)) {
			categoryGroupId = categoryGroupsForMode[0]?.group_id ?? 0;
		}

		if (!categoriesForGroup.some((category: Category) => category.category_id === categoryId)) {
			categoryId = categoriesForGroup[0]?.category_id ?? 0;
		}
	});

	function sanitizeAmountInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = sanitizeSignedAmount(input.value).replace(/^-/, '');
		amount = next;
		input.value = next;
	}
</script>

<div class="modal-backdrop">
	<form
		class="modal-card max-w-[470px]"
		onsubmit={(event) => {
			event.preventDefault();
			onSubmit();
		}}
	>
		<div class="flex items-start justify-between gap-4 border-b pb-5" style="border-color: var(--app-border)">
			<h2 class="text-xl font-bold">{title}</h2>
			<button class="text-muted text-2xl leading-none hover:text-(--app-text)" type="button" onclick={onClose}>×</button>
		</div>

		<div class="mt-5 grid grid-cols-2 gap-2 rounded-full bg-(--app-surface-strong) p-1">
			{#each [
				{ value: 'expense', label: 'Expense' },
				{ value: 'income', label: 'Income' }
			] as option}
				<button
					class={mode === option.value ? 'primary-action' : 'secondary-action'}
					type="button"
					onclick={() => mode = option.value as CategoryGroupType}
				>
					{option.label}
				</button>
			{/each}
		</div>

		<div class="mt-5 grid gap-4 sm:grid-cols-2">
			<label class="grid gap-2">
				<span class="text-sm font-medium">{mode === 'expense' ? 'Merchant' : 'Payee'}</span>
				<input bind:value={name} placeholder={mode === 'expense' ? 'e.g. Netflix' : 'e.g. Salary'} />
			</label>

			<label class="grid gap-2">
				<span class="text-sm font-medium">Amount</span>
				<input bind:value={amount} inputmode="decimal" placeholder={mode === 'expense' ? 'e.g. 549' : 'e.g. 30000'} oninput={sanitizeAmountInput} />
			</label>
		</div>

		<div class="mt-4 grid gap-4 sm:grid-cols-2">
			<label class="grid gap-2">
				<span class="text-sm font-medium">Account</span>
				<SearchableCombobox
					value={String(accountId)}
					options={accountOptions}
					placeholder="Select an account"
					searchPlaceholder="Search accounts..."
					disabled={accounts.length === 0}
					onChange={(value) => accountId = Number(value)}
				/>
			</label>

			<label class="grid gap-2">
				<span class="text-sm font-medium">Category group</span>
				<SearchableCombobox
					value={String(categoryGroupId)}
					options={categoryGroupOptions}
					placeholder="Select a group"
					searchPlaceholder="Search groups..."
					disabled={categoryGroupsForMode.length === 0}
					onChange={(value) => categoryGroupId = Number(value)}
				/>
			</label>
		</div>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category</span>
			<SearchableCombobox
				value={String(categoryId)}
				options={categoryOptions}
				placeholder="Select a category"
				searchPlaceholder="Search categories..."
				disabled={categoriesForGroup.length === 0}
				onChange={(value) => categoryId = Number(value)}
			/>
		</label>

		<div class="mt-4 grid gap-4 sm:grid-cols-2">
			<label class="grid gap-2">
				<span class="text-sm font-medium">Repeat Every</span>
				<input bind:value={interval} min="1" type="number" />
			</label>

			<label class="grid gap-2">
				<span class="text-sm font-medium">Unit</span>
				<SearchableCombobox
					bind:value={frequencyUnit}
					options={frequencyOptions}
					placeholder="Select a unit"
					searchPlaceholder="Search units..."
				/>
			</label>
		</div>

		<div class="mt-4 grid gap-4 sm:grid-cols-2">
			<label class="grid gap-2">
				<span class="text-sm font-medium">Next Due Date</span>
				<input bind:value={nextDueDate} type="date" />
			</label>

			<label class="grid gap-2">
				<span class="text-sm font-medium">End Date (optional)</span>
				<input bind:value={endDate} type="date" />
			</label>
		</div>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="mt-6 flex justify-end gap-3 border-t pt-4" style="border-color: var(--app-border)">
			<button class="secondary-action" type="button" onclick={onClose}>Cancel</button>
			<button class="primary-action" type="submit" disabled={saving}>
				{saving ? savingLabel : submitLabel}
			</button>
		</div>
	</form>
</div>
