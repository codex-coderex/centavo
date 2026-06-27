<script lang="ts">
	import type { Goal } from '$lib/api/goals';
	import { formatMoney } from '../utils/goalFormat';

	let {
		goal,
		allocatedAmount,
		saving,
		error,
		onClose,
		onConfirm
	} = $props<{
		goal: Goal;
		allocatedAmount: number;
		saving: boolean;
		error: string;
		onClose: () => void;
		onConfirm: () => void | Promise<void>;
	}>();
</script>

<div class="modal-backdrop">
	<div class="modal-card">
		<div class="flex items-start justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Complete goal</p>
				<h2 class="mt-1 text-xl font-bold">{goal.name}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<div class="mt-6 rounded-xl border p-4 text-sm" style="border-color: rgba(66, 142, 91, 0.3); background: rgba(66, 142, 91, 0.08)">
			<p class="font-semibold money-positive">This will complete and archive the goal.</p>
			<p class="text-muted mt-2">
				The allocated funds, currently {formatMoney(allocatedAmount)}, will be released for use and this goal will move to Archived goals.
			</p>
		</div>
		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="mt-6 flex justify-end gap-2">
			<button class="secondary-action" type="button" onclick={onClose}>Cancel</button>
			<button class="primary-action" type="button" disabled={saving} onclick={onConfirm}>
				{saving ? 'Completing...' : 'Complete goal'}
			</button>
		</div>
	</div>
</div>
