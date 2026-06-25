<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';
	import type { Tag } from '$lib/api/tags';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';

	let {
		mode = $bindable(),
		accounts,
		budgets,
		budgetItems,
		categories,
		categoryGroups,
		accountId = $bindable(),
		toAccountId = $bindable(),
		categoryGroupId = $bindable(),
		categoryId = $bindable(),
		budgetId = $bindable(),
		budgetItemId = $bindable(),
		amount = $bindable(),
		transactionDate = $bindable(),
		payee = $bindable(),
		notes = $bindable(),
		selectedTagIds = $bindable(),
		error,
		saving,
		tags = [],
		categoryName,
		eyebrow = 'Add transaction',
		title = 'New transaction',
		submitLabel = 'Create transaction',
		savingLabel = 'Creating...',
		lockTransferStructure = false,
		lockTransactionStructure = false,
		onClose,
		onSubmit
	} = $props<{
		mode: CategoryGroupType;
		accounts: Account[];
		budgets: Budget[];
		budgetItems: BudgetItem[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		accountId: number;
		toAccountId: number;
		categoryGroupId: number;
		categoryId: number;
		budgetId: string;
		budgetItemId: string;
		amount: string;
		transactionDate: string;
		payee: string;
		notes: string;
		selectedTagIds: number[];
		error: string;
		saving: boolean;
		tags?: Tag[];
		categoryName: (categoryId: number) => string;
		eyebrow?: string;
		title?: string;
		submitLabel?: string;
		savingLabel?: string;
		lockTransferStructure?: boolean;
		lockTransactionStructure?: boolean;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	let structureLocked = $derived(lockTransactionStructure || (mode === 'transfer' && lockTransferStructure));
	let tagPickerValue = $state('');
	let categoryGroupsForMode = $derived(
		categoryGroups.filter((group: CategoryGroup) => group.type === mode)
	);

	let categoriesForGroup = $derived(
		categories.filter((category: Category) => category.group_id === categoryGroupId)
	);

	let budgetItemsForCategory = $derived(
		mode === 'expense' && budgetId !== 'none'
			? budgetItems.filter(
					(item: BudgetItem) =>
						item.budget_id === Number(budgetId) && item.category_id === categoryId
				)
			: []
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
			label: categoryName(category.category_id)
		}))
	);
	let budgetOptions = $derived([
		{ value: 'none', label: 'None' },
		...budgets.map((budget: Budget) => ({
			value: String(budget.budget_id),
			label: budget.name
		}))
	]);
	let selectedTags = $derived(
		tags.filter((tag: Tag) => selectedTagIds.includes(tag.tag_id))
	);
	let availableTagOptions = $derived(
		tags
			.filter((tag: Tag) => !selectedTagIds.includes(tag.tag_id))
			.map((tag: Tag) => ({
				value: String(tag.tag_id),
				label: tag.name
			}))
	);

	$effect(() => {
		if (!categoryGroupsForMode.some((group: CategoryGroup) => group.group_id === categoryGroupId)) {
			categoryGroupId = categoryGroupsForMode[0]?.group_id ?? 0;
		}

		if (!categoriesForGroup.some((category: Category) => category.category_id === categoryId)) {
			categoryId = categoriesForGroup[0]?.category_id ?? 0;
		}

		if (
			budgetItemId !== 'none'
			&& !budgetItemsForCategory.some((item: BudgetItem) => String(item.budget_item_id) === budgetItemId)
		) {
			budgetItemId = 'none';
		}

		if (budgetId !== 'none' && budgetItemId === 'none') {
			budgetItemId = budgetItemsForCategory[0]?.budget_item_id
				? String(budgetItemsForCategory[0].budget_item_id)
				: 'none';
		}
	});

	function sanitizeAmountInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = input.value
			.replace(/[^\d.]/g, '')
			.replace(/(\..*)\./g, '$1')
			.replace(/^(\d*)(\.\d{0,2}).*$/, '$1$2');

		amount = next;
		input.value = next;
	}

	function addSelectedTag(value: string) {
		const tagId = Number(value);

		if (tagId && !selectedTagIds.includes(tagId)) {
			selectedTagIds = [...selectedTagIds, tagId];
		}

		tagPickerValue = '';
	}

	function removeSelectedTag(tagId: number) {
		selectedTagIds = selectedTagIds.filter((currentTagId: number) => currentTagId !== tagId);
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">{eyebrow}</p>
				<h2 class="mt-1 text-xl font-bold">{title}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<div class="mt-6 grid grid-cols-3 gap-2 rounded-full bg-(--app-surface-strong) p-1">
			{#each [
				{ value: 'expense', label: 'Expense' },
				{ value: 'income', label: 'Income' },
				{ value: 'transfer', label: 'Transfer' }
			] as option}
				<button
					class={mode === option.value ? 'primary-action' : 'secondary-action'}
					type="button"
					disabled={structureLocked}
					onclick={() => {
						mode = option.value as CategoryGroupType;
						budgetItemId = 'none';
					}}
				>
					{option.label}
				</button>
			{/each}
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Amount</span>
			<input bind:value={amount} inputmode="decimal" placeholder="0.00" oninput={sanitizeAmountInput} />
			<p class="text-muted text-xs">
				Enter the amount without signs. {mode === 'expense' ? 'Expenses are saved as negative.' : mode === 'income' ? 'Income is saved as positive.' : 'Transfers create one negative and one positive transaction.'}
			</p>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">{mode === 'transfer' ? 'From account' : 'Account'}</span>
			<SearchableCombobox
				value={String(accountId)}
				options={accountOptions}
				placeholder="Select an account"
				searchPlaceholder="Search accounts..."
				disabled={structureLocked}
				onChange={(value) => accountId = Number(value)}
			/>
		</label>

		{#if mode === 'transfer'}
			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium">To account</span>
				<SearchableCombobox
					value={String(toAccountId)}
					options={accountOptions}
					placeholder="Select an account"
					searchPlaceholder="Search accounts..."
					disabled={lockTransferStructure}
					onChange={(value) => toAccountId = Number(value)}
				/>
			</label>
		{/if}

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category group</span>
			<SearchableCombobox
				value={String(categoryGroupId)}
				options={categoryGroupOptions}
				placeholder="Select a category group"
				searchPlaceholder="Search groups..."
				disabled={structureLocked || categoryGroupsForMode.length === 0}
				onChange={(value) => categoryGroupId = Number(value)}
			/>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category</span>
			<SearchableCombobox
				value={String(categoryId)}
				options={categoryOptions}
				placeholder="Select a category"
				searchPlaceholder="Search categories..."
				disabled={structureLocked || categoriesForGroup.length === 0}
				onChange={(value) => categoryId = Number(value)}
			/>
		</label>

		{#if mode === 'expense'}
			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium">Budget</span>
				<SearchableCombobox
					bind:value={budgetId}
					options={budgetOptions}
					placeholder="None"
					searchPlaceholder="Search budgets..."
					disabled={structureLocked}
				/>
				{#if !structureLocked && budgetId !== 'none' && budgetItemsForCategory.length === 0}
					<p class="text-muted text-xs">
						This budget does not have an item for the selected category.
					</p>
				{/if}
			</label>
		{/if}

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Transaction date</span>
			<input bind:value={transactionDate} type="date" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">{mode === 'expense' ? 'Merchant' : 'Payee'}</span>
			<input bind:value={payee} placeholder={mode === 'expense' ? 'Search merchants...' : 'Payee'} />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Notes</span>
			<textarea bind:value={notes} rows="3" placeholder="Add a note..."></textarea>
		</label>

		<div class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Tags</span>
			{#if selectedTags.length > 0}
				<div class="flex flex-wrap gap-2">
					{#each selectedTags as tag}
						<button
							class="transaction-tag-pill"
							type="button"
							aria-label={`Remove ${tag.name} tag`}
							onclick={() => removeSelectedTag(tag.tag_id)}
						>
							{tag.name} ×
						</button>
					{/each}
				</div>
			{/if}

			{#if tags.length > 0 && availableTagOptions.length > 0}
				<SearchableCombobox
					bind:value={tagPickerValue}
					options={availableTagOptions}
					placeholder="Add a tag"
					searchPlaceholder="Search tags..."
					onChange={addSelectedTag}
				/>
			{:else if tags.length === 0}
				<p class="text-muted text-xs">Create tags in Settings to use them here.</p>
			{:else}
				<p class="text-muted text-xs">All tags are selected.</p>
			{/if}
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
