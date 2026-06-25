<script lang="ts">
	import { seedSampleData } from '$lib/api/seed';

	type SeedSummary = {
		accounts: number;
		budgets: number;
		recurring_rules: number;
		goals: number;
		transactions: number;
	};

	type SeedResult = {
		status: string;
		message: string;
		summary: SeedSummary;
	};

	let {
		onClose,
		onSeeded
	}: {
		onClose: () => void;
		onSeeded: (result: SeedResult) => void;
	} = $props();

	let isSeeding = $state(false);
	let seedError = $state('');

	async function confirmSeed() {
		seedError = '';
		isSeeding = true;

		try {
			const result = await seedSampleData();
			onSeeded(result);
			onClose();

			setTimeout(() => {
				window.location.reload();
			}, 500);
		} catch (error) {
			seedError = error instanceof Error ? error.message : 'Failed to seed demo data.';
		} finally {
			isSeeding = false;
		}
	}
</script>

<div class="modal-backdrop" role="presentation">
	<div
		class="modal-card"
		role="dialog"
		aria-modal="true"
		aria-labelledby="seed-modal-title"
	>
		<div class="flex items-start justify-between gap-4">
			<div>
				<h3 id="seed-modal-title" class="text-lg font-semibold">
					Seed demo sample data?
				</h3>

				<p class="text-muted mt-2 text-sm">
					This will push demo data into the backend database.
				</p>
			</div>

			<button
				type="button"
				class="transaction-row-action"
				disabled={isSeeding}
				onclick={onClose}
				aria-label="Close seed sample data modal"
			>
				✕
			</button>
		</div>

		<div
			class="text-muted mt-4 rounded-lg border p-3 text-sm"
			style="border-color: var(--app-border); background: var(--app-surface-strong)"
		>
			<p>This will add:</p>

			<ul class="mt-2 list-disc space-y-1 pl-5">
				<li>4 accounts</li>
				<li>3 budgets</li>
				<li>Budget items</li>
				<li>4 recurring rules</li>
				<li>3 goals linked to accounts</li>
				<li>2 months of transactions</li>
			</ul>
		</div>

		{#if seedError}
			<div class="mt-4 rounded-lg border p-3 text-sm money-negative">
				{seedError}
			</div>
		{/if}

		<div class="mt-5 flex justify-end gap-2">
			<button
				type="button"
				class="secondary-action"
				disabled={isSeeding}
				onclick={onClose}
			>
				No
			</button>

			<button
				type="button"
				class="primary-action"
				disabled={isSeeding}
				onclick={confirmSeed}
			>
				{isSeeding ? 'Seeding...' : 'Yes, seed data'}
			</button>
		</div>
	</div>
</div>