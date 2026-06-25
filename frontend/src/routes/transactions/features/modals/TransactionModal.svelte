<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Budget, BudgetItem } from '$lib/api/budgets';
	import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';
	import type { Transaction } from '$lib/api/transactions';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';

	let {
		transaction,
		accounts,
		budgets,
		budgetItems,
		categories,
		categoryGroups,
		mode = $bindable(),
		accountId = $bindable(),
		categoryGroupId = $bindable(),
		categoryId = $bindable(),
		budgetId = $bindable(),
		budgetItemId = $bindable(),
		amount = $bindable(),
		transactionDate = $bindable(),
		payee = $bindable(),
		notes = $bindable(),
		error,
		saving,
		categoryName,
		onClose,
		onSubmit
	} = $props<{
		transaction: Transaction;
		accounts: Account[];
		budgets: Budget[];
		budgetItems: BudgetItem[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		mode: CategoryGroupType;
		accountId: number;
		categoryGroupId: number;
		categoryId: number;
		budgetId: string;
		budgetItemId: string;
		amount: string;
		transactionDate: string;
		payee: string;
		notes: string;
		error: string;
		saving: boolean;
		categoryName: (categoryId: number) => string;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	let isTransfer = $derived(transaction.transfer_id !== null && transaction.transfer_id !== undefined);
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
	let categoryOptions = $derived(
		categoriesForGroup.map((category: Category) => ({
			value: String(category.category_id),
			label: categoryName(category.category_id)
		}))
	);
	let categoryGroupOptions = $derived(
		categoryGroupsForMode.map((group: CategoryGroup) => ({
			value: String(group.group_id),
			label: group.name
		}))
	);
	let budgetOptions = $derived([
		{ value: 'none', label: 'None' },
		...budgets.map((budget: Budget) => ({
			value: String(budget.budget_id),
			label: budget.name
		}))
	]);

	$effect(() => {
		if (!categoryGroupsForMode.some((group: CategoryGroup) => group.group_id === categoryGroupId)) {
			categoryGroupId = categoryGroupsForMode[0]?.group_id ?? 0;
		}

		if (!categoriesForGroup.some((category: Category) => category.category_id === categoryId)) {
			categoryId = categoriesForGroup[0]?.category_id ?? 0;
		}

		if (isTransfer || mode !== 'expense' || budgetId === 'none') {
			budgetItemId = 'none';
			return;
		}

		budgetItemId = budgetItemsForCategory[0]?.budget_item_id
			? String(budgetItemsForCategory[0].budget_item_id)
			: 'none';
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">
					{isTransfer ? 'Edit transfer' : 'Edit transaction'}
				</p>
				<h2 class="mt-1 text-xl font-bold">{transaction.payee ?? 'No payee'}</h2>
				{#if isTransfer}
					<p class="text-muted mt-1 text-sm">
						Transfer account/category changes are locked. Edit amount, date, payee, and notes here.
					</p>
				{/if}
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<div class="mt-6 grid grid-cols-3 gap-2">
			{#each [
				{ value: 'expense', label: 'Expense' },
				{ value: 'income', label: 'Income' },
				{ value: 'transfer', label: 'Transfer' }
			] as option}
				<button
					class={mode === option.value ? 'primary-action' : 'secondary-action'}
					type="button"
					disabled={isTransfer}
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
			<span class="text-sm font-medium">Account</span>
			<SearchableCombobox
				value={String(accountId)}
				options={accountOptions}
				placeholder="Select an account"
				searchPlaceholder="Search accounts..."
				disabled={isTransfer}
				onChange={(value) => accountId = Number(value)}
			/>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Category group</span>
			<SearchableCombobox
				value={String(categoryGroupId)}
				options={categoryGroupOptions}
				placeholder="Select a category group"
				searchPlaceholder="Search groups..."
				disabled={isTransfer || categoryGroupsForMode.length === 0}
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
				disabled={isTransfer || categoriesForGroup.length === 0}
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
					disabled={isTransfer}
				/>
				{#if !isTransfer && budgetId !== 'none' && budgetItemsForCategory.length === 0}
					<p class="text-muted text-xs">
						This budget does not have an item for the selected category.
					</p>
				{/if}
			</label>
		{/if}

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">{isTransfer ? 'Transfer amount' : 'Amount'}</span>
			<input bind:value={amount} inputmode="decimal" placeholder="0.00" oninput={sanitizeAmountInput} />
			<p class="text-muted text-xs">
				Enter the amount without signs. {mode === 'expense' ? 'Expenses are saved as negative.' : mode === 'income' ? 'Income is saved as positive.' : 'Transfers update both sides of the transfer pair.'}
			</p>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Transaction date</span>
			<input bind:value={transactionDate} type="date" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Payee</span>
			<input bind:value={payee} placeholder="Merchant or payee" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Notes</span>
			<textarea bind:value={notes} rows="3" placeholder="Optional notes"></textarea>
		</label>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<button class="primary-action mt-6 w-full" type="submit" disabled={saving}>
			{saving ? 'Saving...' : 'Save changes'}
		</button>
	</form>
</div>
