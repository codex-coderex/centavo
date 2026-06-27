<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Goal, GoalAccount } from '$lib/api/goals';
	import { formatDate, formatMoney } from '../utils/goalFormat';
	import { primaryAccountForGoal } from '../utils/goalTotals';

	let {
		goals,
		goalAccounts,
		accounts,
		onClose
	} = $props<{
		goals: Goal[];
		goalAccounts: GoalAccount[];
		accounts: Account[];
		onClose: () => void;
	}>();

	function accountLabel(goal: Goal) {
		return primaryAccountForGoal(goal.goal_id, goalAccounts, accounts)?.name ?? 'Funds released';
	}
</script>

<div class="modal-backdrop">
	<div class="modal-card max-h-[85vh] overflow-y-auto">
		<div class="flex items-start justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Archived goals</p>
				<h2 class="mt-1 text-xl font-bold">Completed goals</h2>
				<p class="text-muted mt-1 text-sm">Completed goals are kept here for reference.</p>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<div class="mt-6 grid gap-3">
			{#each goals as goal}
				<div class="flex items-center justify-between gap-4 rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-surface-strong)">
					<div>
						<p class="font-semibold">{goal.name}</p>
						<p class="text-muted mt-1 text-xs">
							{accountLabel(goal)} · target {formatMoney(goal.target_amount_minor)} · due {formatDate(goal.target_date)}
						</p>
					</div>

					<span class="pill shrink-0">Archived</span>
				</div>
			{:else}
				<p class="text-muted rounded-xl border p-4 text-sm" style="border-color: var(--app-border)">
					No archived goals.
				</p>
			{/each}
		</div>
	</div>
</div>
