<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import {
		addAccountToGoal,
		completeGoal,
		createGoal,
		deleteGoal,
		removeAccountFromGoal,
		updateGoal,
		type Goal,
		type GoalAccount
	} from '$lib/api/goals';
	import { dateInputValue } from '../utils/goalFormat';
	import { allocatedForGoal, allocationsForGoal } from '../utils/goalTotals';
	import AddGoalFundsModal from './AddGoalFundsModal.svelte';
	import CompleteGoalModal from './CompleteGoalModal.svelte';
	import DeleteGoalModal from './DeleteGoalModal.svelte';
	import GoalModal from './GoalModal.svelte';

	let {
		showGoalModal = $bindable(),
		showFundsModal = $bindable(),
		showDeleteModal = $bindable(),
		showCompleteModal = $bindable(),
		editingGoal = $bindable(),
		fundingGoal = $bindable(),
		deletingGoal = $bindable(),
		completingGoal = $bindable(),
		userId,
		accounts,
		goalAccounts,
		onRefresh,
		onNotice
	} = $props<{
		showGoalModal: boolean;
		showFundsModal: boolean;
		showDeleteModal: boolean;
		showCompleteModal: boolean;
		editingGoal: Goal | null;
		fundingGoal: Goal | null;
		deletingGoal: Goal | null;
		completingGoal: Goal | null;
		userId: number;
		accounts: Account[];
		goalAccounts: GoalAccount[];
		onRefresh: () => Promise<void>;
		onNotice: (message: string) => void;
	}>();

	let saving = $state(false);
	let modalError = $state('');
	let goalName = $state('');
	let targetAmount = $state('');
	let targetDate = $state('');
	let linkedAccountId = $state(0);
	let fundsAmount = $state('');
	let fundsAccountId = $state(0);

	function primaryAllocation(goal: Goal | null) {
		return goal ? allocationsForGoal(goal.goal_id, goalAccounts)[0] : undefined;
	}

	function resetGoalForm() {
		const allocation = primaryAllocation(editingGoal);

		modalError = '';
		goalName = editingGoal?.name ?? '';
		targetAmount = editingGoal ? (editingGoal.target_amount_minor / 100).toFixed(2) : '';
		targetDate = dateInputValue(editingGoal?.target_date);
		linkedAccountId = allocation?.account_id ?? accounts[0]?.account_id ?? 0;
	}

	function resetFundsForm() {
		const allocation = primaryAllocation(fundingGoal);

		modalError = '';
		fundsAmount = '';
		fundsAccountId = allocation?.account_id ?? accounts[0]?.account_id ?? 0;
	}

	$effect(() => {
		if (showGoalModal) resetGoalForm();
	});

	$effect(() => {
		if (showFundsModal) resetFundsForm();
	});

	function closeGoalModal() {
		showGoalModal = false;
		editingGoal = null;
		modalError = '';
		saving = false;
	}

	function closeFundsModal() {
		showFundsModal = false;
		fundingGoal = null;
		modalError = '';
		saving = false;
	}

	function closeDeleteModal() {
		showDeleteModal = false;
		deletingGoal = null;
		modalError = '';
		saving = false;
	}

	function closeCompleteModal() {
		showCompleteModal = false;
		completingGoal = null;
		modalError = '';
		saving = false;
	}

	async function submitGoal() {
		modalError = '';

		if (!goalName.trim()) {
			modalError = 'Goal name is required.';
			return;
		}

		if (!targetAmount.trim()) {
			modalError = 'Target amount is required.';
			return;
		}

		if (linkedAccountId === 0) {
			modalError = 'Select a linked account.';
			return;
		}

		saving = true;

		try {
			if (editingGoal) {
				const existingAllocation = primaryAllocation(editingGoal);
				const allocatedAmount = allocatedForGoal(editingGoal.goal_id, goalAccounts);

				await updateGoal(editingGoal.goal_id, {
					name: goalName.trim(),
					target_amount: targetAmount,
					target_date: targetDate || null
				});

				if (existingAllocation?.account_id !== linkedAccountId) {
					await addAccountToGoal({
						goal_id: editingGoal.goal_id,
						account_id: linkedAccountId,
						allocated_amount: allocatedAmount / 100
					});
					if (existingAllocation) {
						await removeAccountFromGoal(editingGoal.goal_id, existingAllocation.account_id);
					}
				}

				onNotice('Goal updated.');
			} else {
				const result = await createGoal({
					user_id: userId,
					name: goalName.trim(),
					target_amount: targetAmount,
					target_date: targetDate || null
				});

				await addAccountToGoal({
					goal_id: result.goal_id,
					account_id: linkedAccountId,
					allocated_amount: 0
				});

				onNotice('Goal created.');
			}

			closeGoalModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function submitFunds() {
		modalError = '';

		if (!fundingGoal) {
			modalError = 'Goal does not exist.';
			return;
		}

		if (!fundsAmount.trim()) {
			modalError = 'Amount is required.';
			return;
		}

		if (fundsAccountId === 0) {
			modalError = 'Select an account.';
			return;
		}

		saving = true;

		try {
			await addAccountToGoal({
				goal_id: fundingGoal.goal_id,
				account_id: fundsAccountId,
				allocated_amount: fundsAmount
			});

			onNotice('Funds allocated.');
			closeFundsModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function confirmCompleteGoal() {
		modalError = '';

		if (!completingGoal) {
			modalError = 'Goal does not exist.';
			return;
		}

		saving = true;

		try {
			await completeGoal(completingGoal.goal_id);
			onNotice('Goal completed and archived.');
			closeCompleteModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function confirmDeleteGoal() {
		modalError = '';

		if (!deletingGoal) {
			modalError = 'Goal does not exist.';
			return;
		}

		saving = true;

		try {
			await deleteGoal(deletingGoal.goal_id);
			onNotice('Goal deleted.');
			closeDeleteModal();
			await onRefresh();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}
</script>

{#if showGoalModal}
	<GoalModal
		bind:name={goalName}
		bind:targetAmount
		bind:targetDate
		bind:accountId={linkedAccountId}
		{accounts}
		error={modalError}
		{saving}
		title={editingGoal ? 'Edit goal' : 'New goal'}
		submitLabel={editingGoal ? 'Save changes' : 'Create goal'}
		savingLabel={editingGoal ? 'Saving...' : 'Creating...'}
		onClose={closeGoalModal}
		onSubmit={submitGoal}
	/>
{/if}

{#if showCompleteModal && completingGoal}
	<CompleteGoalModal
		goal={completingGoal}
		allocatedAmount={allocatedForGoal(completingGoal.goal_id, goalAccounts)}
		{saving}
		error={modalError}
		onClose={closeCompleteModal}
		onConfirm={confirmCompleteGoal}
	/>
{/if}

{#if showDeleteModal && deletingGoal}
	<DeleteGoalModal
		goal={deletingGoal}
		allocatedAmount={allocatedForGoal(deletingGoal.goal_id, goalAccounts)}
		{saving}
		error={modalError}
		onClose={closeDeleteModal}
		onConfirm={confirmDeleteGoal}
	/>
{/if}

{#if showFundsModal && fundingGoal}
	<AddGoalFundsModal
		goal={fundingGoal}
		bind:amount={fundsAmount}
		bind:accountId={fundsAccountId}
		{accounts}
		error={modalError}
		{saving}
		onClose={closeFundsModal}
		onSubmit={submitFunds}
	/>
{/if}
