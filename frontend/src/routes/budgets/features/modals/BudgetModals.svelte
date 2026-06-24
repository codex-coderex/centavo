<script lang="ts">
	import {
		createBudget,
		createBudgetItem,
		updateBudget,
		updateBudgetItem,
		type Budget,
		type BudgetItem,
		type BudgetPeriodType
	} from '$lib/api/budgets';
	import type { Category, CategoryGroup } from '$lib/api/categories';
	import {
		dateInputValue,
		defaultBudgetName,
		todayInputValue
	} from '../utils/budgetFormat';
	import BudgetItemModal from './BudgetItemModal.svelte';
	import BudgetModal from './BudgetModal.svelte';

	let {
		showBudgetModal = $bindable(),
		showBudgetItemModal = $bindable(),
		editingBudget = $bindable(),
		editingBudgetItem = $bindable(),
		selectedBudgetId = $bindable(),
		userId,
		categories,
		categoryGroups,
		onRefresh,
		onRefreshBudgetItems,
		onNotice
	} = $props<{
		showBudgetModal: boolean;
		showBudgetItemModal: boolean;
		editingBudget: Budget | null;
		editingBudgetItem: BudgetItem | null;
		selectedBudgetId: number | null;
		userId: number;
		categories: Category[];
		categoryGroups: CategoryGroup[];
		onRefresh: () => Promise<void>;
		onRefreshBudgetItems: () => Promise<void>;
		onNotice: (message: string) => void;
	}>();

	let saving = $state(false);
	let modalError = $state('');
	let budgetName = $state('');
	let budgetPeriod: BudgetPeriodType = $state('monthly');
	let budgetStartDate = $state('');
	let budgetEndDate = $state('');
	let itemCategoryId = $state(0);
	let itemPlannedAmount = $state('');
	let itemRolloverEnabled = $state(false);

	let expenseCategoryIds = $derived(
		categoryGroups
			.filter((group: CategoryGroup) => group.type === 'expense')
			.map((group: CategoryGroup) => group.group_id)
	);
	let expenseCategories = $derived(
		categories.filter(
			(category: Category) =>
				category.is_active && expenseCategoryIds.includes(category.group_id)
		)
	);

	function resetBudgetForm(budget: Budget | null = null) {
		budgetName = budget?.name ?? defaultBudgetName();
		budgetPeriod = budget?.period_type ?? 'monthly';
		budgetStartDate = budget ? dateInputValue(budget.start_date) : todayInputValue();
		budgetEndDate = dateInputValue(budget?.end_date);
	}

	function resetBudgetItemForm(item: BudgetItem | null = null) {
		itemCategoryId = item?.category_id ?? expenseCategories[0]?.category_id ?? 0;
		itemPlannedAmount = item ? (item.planned_amount_minor / 100).toFixed(2) : '';
		itemRolloverEnabled = item?.rollover_enabled ?? false;
	}

	$effect(() => {
		if (showBudgetModal) {
			modalError = '';
			resetBudgetForm(editingBudget);
		}
	});

	$effect(() => {
		if (showBudgetItemModal) {
			modalError = '';
			resetBudgetItemForm(editingBudgetItem);
		}
	});

	function closeBudgetModal() {
		showBudgetModal = false;
		editingBudget = null;
		modalError = '';
		saving = false;
	}

	function closeBudgetItemModal() {
		showBudgetItemModal = false;
		editingBudgetItem = null;
		modalError = '';
		saving = false;
	}

	async function submitBudget() {
		modalError = '';

		if (!budgetName.trim()) {
			modalError = 'Budget name is required.';
			return;
		}

		if (!budgetStartDate) {
			modalError = 'Start date is required.';
			return;
		}

		saving = true;

		try {
			if (editingBudget) {
				await updateBudget(editingBudget.budget_id, {
					name: budgetName.trim(),
					period_type: budgetPeriod,
					start_date: budgetStartDate,
					end_date: budgetEndDate || null
				});
				onNotice('Budget updated.');
			} else {
				await createBudget({
					user_id: userId,
					name: budgetName.trim(),
					period_type: budgetPeriod,
					start_date: budgetStartDate,
					end_date: budgetEndDate || null
				});
				selectedBudgetId = null;
				onNotice('Budget created.');
			}

			closeBudgetModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function submitBudgetItem() {
		modalError = '';

		if (selectedBudgetId === null) {
			modalError = 'Select a budget first.';
			return;
		}

		if (itemCategoryId === 0) {
			modalError = 'Select a category first.';
			return;
		}

		if (!itemPlannedAmount.trim()) {
			modalError = 'Planned amount is required.';
			return;
		}

		saving = true;

		try {
			if (editingBudgetItem) {
				await updateBudgetItem(editingBudgetItem.budget_item_id, {
					category_id: itemCategoryId,
					planned_amount: itemPlannedAmount,
					rollover_enabled: itemRolloverEnabled
				});
				onNotice('Budget item updated.');
			} else {
				await createBudgetItem({
					budget_id: selectedBudgetId,
					category_id: itemCategoryId,
					planned_amount: itemPlannedAmount,
					rollover_enabled: itemRolloverEnabled
				});
				onNotice('Budget item created.');
			}

			closeBudgetItemModal();
			await onRefreshBudgetItems();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}
</script>

{#if showBudgetModal}
	<BudgetModal
		bind:name={budgetName}
		bind:period={budgetPeriod}
		bind:startDate={budgetStartDate}
		bind:endDate={budgetEndDate}
		error={modalError}
		{saving}
		title={editingBudget ? 'Edit budget' : 'New budget'}
		submitLabel={editingBudget ? 'Save changes' : 'Create budget'}
		savingLabel={editingBudget ? 'Saving...' : 'Creating...'}
		onClose={closeBudgetModal}
		onSubmit={submitBudget}
	/>
{/if}

{#if showBudgetItemModal}
	<BudgetItemModal
		bind:categoryId={itemCategoryId}
		bind:plannedAmount={itemPlannedAmount}
		bind:rolloverEnabled={itemRolloverEnabled}
		categories={expenseCategories}
		error={modalError}
		{saving}
		title={editingBudgetItem ? 'Edit item' : 'New item'}
		submitLabel={editingBudgetItem ? 'Save changes' : 'Add item'}
		savingLabel={editingBudgetItem ? 'Saving...' : 'Adding...'}
		onClose={closeBudgetItemModal}
		onSubmit={submitBudgetItem}
	/>
{/if}
