<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';
	import {
		createRecurringRule,
		updateRecurringRule,
		type FrequencyUnit,
		type RecurringRule
	} from '$lib/api/recurring';
	import { amountInputValue, todayInputValue } from '../utils/recurringFormat';
	import RecurringRuleModal from './RecurringRuleModal.svelte';

	let {
		showRuleModal = $bindable(),
		editingRule = $bindable(),
		accounts,
		categories,
		categoryGroups,
		onRefresh,
		onNotice
	} = $props<{
		showRuleModal: boolean;
		editingRule: RecurringRule | null;
		accounts: Account[];
		categories: Category[];
		categoryGroups: CategoryGroup[];
		onRefresh: () => void | Promise<void>;
		onNotice: (message: string) => void;
	}>();

	let mode: CategoryGroupType = $state('expense');
	let accountId = $state(0);
	let categoryGroupId = $state(0);
	let categoryId = $state(0);
	let name = $state('');
	let amount = $state('');
	let interval = $state(1);
	let frequencyUnit: FrequencyUnit = $state('month');
	let nextDueDate = $state(todayInputValue());
	let endDate = $state('');
	let saving = $state(false);
	let error = $state('');
	let modalKey = $state('');

	function firstGroupId(nextMode: CategoryGroupType) {
		return categoryGroups.find((group: CategoryGroup) => group.type === nextMode && group.is_active)?.group_id ?? 0;
	}

	function firstCategoryId(groupId: number) {
		return categories.find((category: Category) => category.group_id === groupId && category.is_active)?.category_id ?? 0;
	}

	function groupForCategory(nextCategoryId: number) {
		const category = categories.find((row: Category) => row.category_id === nextCategoryId);
		return categoryGroups.find((group: CategoryGroup) => group.group_id === category?.group_id);
	}

	function closeModal() {
		showRuleModal = false;
		editingRule = null;
		error = '';
	}

	function resetForm() {
		const editingMode = editingRule?.expected_amount_minor && editingRule.expected_amount_minor > 0
			? 'income'
			: 'expense';
		const editingGroup = editingRule ? groupForCategory(editingRule.category_id) : null;

		mode = editingGroup?.type === 'income' ? 'income' : editingMode;
		accountId = editingRule?.account_id ?? accounts[0]?.account_id ?? 0;
		categoryGroupId = editingGroup?.group_id ?? firstGroupId(mode);
		categoryId = editingRule?.category_id ?? firstCategoryId(categoryGroupId);
		name = editingRule?.name ?? '';
		amount = editingRule ? amountInputValue(Math.abs(editingRule.expected_amount_minor)) : '';
		interval = editingRule?.interval ?? 1;
		frequencyUnit = editingRule?.frequency_unit ?? 'month';
		nextDueDate = editingRule?.next_due_date?.slice(0, 10) ?? todayInputValue();
		endDate = editingRule?.end_date?.slice(0, 10) ?? '';
		error = '';
	}

	function signedAmount() {
		const normalized = amount.trim();
		return mode === 'expense' ? `-${normalized}` : normalized;
	}

	function validateForm() {
		if (!name.trim()) return 'Name is required.';
		if (!amount.trim()) return 'Amount is required.';
		if (Number(amount) <= 0) return 'Amount must be greater than zero.';
		if (!accountId) return 'Select an account.';
		if (!categoryGroupId || !categoryId) return 'Select a category.';
		if (interval <= 0) return 'Repeat interval must be greater than zero.';
		if (!nextDueDate) return 'Next due date is required.';
		return '';
	}

	async function submitRule() {
		error = validateForm();
		if (error) return;

		saving = true;

		try {
			if (editingRule) {
				await updateRecurringRule(editingRule.recurring_rule_id, {
					account_id: accountId,
					category_id: categoryId,
					name: name.trim(),
					expected_amount: signedAmount(),
					interval,
					frequency_unit: frequencyUnit,
					start_date: editingRule.start_date,
					next_due_date: nextDueDate,
					end_date: endDate || null
				});
				onNotice('Recurring rule updated.');
			} else {
				await createRecurringRule({
					account_id: accountId,
					category_id: categoryId,
					name: name.trim(),
					expected_amount: signedAmount(),
					interval,
					frequency_unit: frequencyUnit,
					start_date: nextDueDate,
					next_due_date: nextDueDate,
					end_date: endDate || null
				});
				onNotice('Recurring rule created.');
			}

			closeModal();
			await onRefresh();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	$effect(() => {
		const nextKey = showRuleModal ? String(editingRule?.recurring_rule_id ?? 'new') : '';

		if (nextKey && nextKey !== modalKey) {
			modalKey = nextKey;
			resetForm();
		}

		if (!nextKey) {
			modalKey = '';
		}
	});
</script>

{#if showRuleModal}
	<RecurringRuleModal
		bind:mode
		{accounts}
		{categories}
		{categoryGroups}
		bind:accountId
		bind:categoryGroupId
		bind:categoryId
		bind:name
		bind:amount
		bind:interval
		bind:frequencyUnit
		bind:nextDueDate
		bind:endDate
		{error}
		{saving}
		title={editingRule ? 'Edit Recurring Rule' : 'New Recurring Rule'}
		submitLabel={editingRule ? 'Save Changes' : 'Create Rule'}
		savingLabel={editingRule ? 'Saving...' : 'Creating...'}
		onClose={closeModal}
		onSubmit={submitRule}
	/>
{/if}
