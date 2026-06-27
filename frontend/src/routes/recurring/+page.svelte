<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getAllCategories, getCategoryGroups, type Category, type CategoryGroup } from '$lib/api/categories';
	import {
		deactivateRecurringRule,
		deleteRecurringRule,
		generateTransaction,
		getRecurringRules,
		pauseRecurringRule,
		resumeRecurringRule,
		type RecurringRule
	} from '$lib/api/recurring';
	import ConfirmActionModal from '$lib/shared/components/ConfirmActionModal.svelte';
	import RecurringView from './features/components/RecurringView.svelte';
	import RecurringModals from './features/modals/RecurringModals.svelte';

	const userId = 1;

	let recurringRules: RecurringRule[] = $state([]);
	let accounts: Account[] = $state([]);
	let categories: Category[] = $state([]);
	let categoryGroups: CategoryGroup[] = $state([]);
	let editingRule: RecurringRule | null = $state(null);
	let deactivatingRule: RecurringRule | null = $state(null);
	let loading = $state(true);
	let error = $state('');
	let notice = $state('');
	let actionError = $state('');
	let actionSaving = $state(false);
	let showRuleModal = $state(false);
	let showDeactivateModal = $state(false);
	let showArchived = $state(false);

	let visibleRecurringRules = $derived(
		recurringRules.filter((rule: RecurringRule) =>
			showArchived ? rule.status === 'inactive' : rule.status !== 'inactive'
		)
	);
	let archivedRecurringRules = $derived(
		recurringRules.filter((rule: RecurringRule) => rule.status === 'inactive')
	);

	async function loadPage() {
		loading = true;
		error = '';

		try {
			const [recurringRows, accountRows, categoryRows, groupRows] = await Promise.all([
				getRecurringRules(userId),
				getAccounts(userId),
				getAllCategories(userId),
				getCategoryGroups(userId)
			]);

			recurringRules = recurringRows;
			accounts = accountRows;
			categories = categoryRows;
			categoryGroups = groupRows;
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function openCreateRule() {
		notice = '';
		editingRule = null;
		showRuleModal = true;
	}

	function openEditRule(rule: RecurringRule) {
		notice = '';
		editingRule = rule;
		showRuleModal = true;
	}

	async function pauseRule(rule: RecurringRule) {
		error = '';
		notice = '';

		try {
			await pauseRecurringRule(rule.recurring_rule_id);
			notice = 'Recurring rule paused.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function resumeRule(rule: RecurringRule) {
		error = '';
		notice = '';

		try {
			await resumeRecurringRule(rule.recurring_rule_id);
			notice = 'Recurring rule resumed.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function generateNow(rule: RecurringRule) {
		error = '';
		notice = '';

		try {
			await generateTransaction(rule.recurring_rule_id);
			notice = 'Transaction generated.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	function openDeactivateRule(rule: RecurringRule) {
		error = '';
		notice = '';
		actionError = '';
		deactivatingRule = rule;
		showDeactivateModal = true;
	}

	function closeDeactivateRule() {
		showDeactivateModal = false;
		deactivatingRule = null;
		actionError = '';
		actionSaving = false;
	}

	async function confirmDeactivateRule() {
		if (!deactivatingRule) return;

		error = '';
		notice = '';
		actionError = '';
		actionSaving = true;

		try {
			await deactivateRecurringRule(deactivatingRule.recurring_rule_id);
			notice = 'Recurring rule deactivated.';
			closeDeactivateRule();
			await loadPage();
		} catch (err) {
			actionError = err instanceof Error ? err.message : String(err);
		} finally {
			actionSaving = false;
		}
	}

	async function deleteRule(rule: RecurringRule) {
		if (!confirm(`Delete "${rule.name || 'this recurring rule'}" permanently?`)) {
			return;
		}

		error = '';
		notice = '';

		try {
			await deleteRecurringRule(rule.recurring_rule_id);
			notice = 'Recurring rule deleted.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadPage);
</script>

<RecurringView
	recurringRules={visibleRecurringRules}
	archivedCount={archivedRecurringRules.length}
	{showArchived}
	{accounts}
	{categories}
	{categoryGroups}
	{loading}
	{error}
	{notice}
	onAdd={openCreateRule}
	onArchived={() => showArchived = !showArchived}
	onPause={pauseRule}
	onResume={resumeRule}
	onGenerate={generateNow}
	onEdit={openEditRule}
	onDeactivate={openDeactivateRule}
	onDelete={deleteRule}
/>

<RecurringModals
	bind:showRuleModal
	bind:editingRule
	{accounts}
	{categories}
	{categoryGroups}
	onRefresh={loadPage}
	onNotice={(message) => notice = message}
/>

{#if showDeactivateModal && deactivatingRule}
	<ConfirmActionModal
		eyebrow="Deactivate recurring rule"
		title={deactivatingRule.name || 'Recurring rule'}
		message="This will deactivate the recurring rule."
		detail="It will stop generating future transactions and move to the archived recurring rules view."
		confirmLabel="Deactivate rule"
		savingLabel="Deactivating..."
		saving={actionSaving}
		error={actionError}
		variant="warning"
		onClose={closeDeactivateRule}
		onConfirm={confirmDeactivateRule}
	/>
{/if}
