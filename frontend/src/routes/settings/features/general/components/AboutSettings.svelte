<script lang="ts">
	import SeedSampleDataModal from './modals/SeedSampleDataModal.svelte';

	type SeedResult = {
		status: string;
		message: string;
		summary: {
			accounts: number;
			budgets: number;
			recurring_rules: number;
			goals: number;
			transactions: number;
		};
	};

	let showSeedModal = $state(false);
	let seedSuccess = $state('');
	let seedError = $state('');

	function openSeedModal() {
		seedSuccess = '';
		seedError = '';
		showSeedModal = true;
	}

	function closeSeedModal() {
		showSeedModal = false;
	}

	function handleSeeded(result: SeedResult) {
		seedError = '';
		seedSuccess = `${result.message} Added ${result.summary.accounts} accounts, ${result.summary.budgets} budgets, ${result.summary.recurring_rules} recurring rules, ${result.summary.goals} goals, and ${result.summary.transactions} transactions.`;
	}
</script>

<div class="dashboard-card p-5">
	<div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
		<div>
			<h2 class="text-lg font-semibold">About</h2>
			<p class="text-muted mt-1 text-sm">
				Centavo is running locally through pywebview and SQLite.
			</p>
		</div>

		<button type="button" class="primary-action" onclick={openSeedModal}>
			Seed sample data
		</button>
	</div>

	<div
		class="text-muted mt-5 rounded-lg border p-4 text-sm"
		style="border-color: var(--app-border); background: var(--app-surface-strong)"
	>
		<p>Mode: Offline desktop</p>
		<p class="mt-1">Storage: Local SQLite database</p>
	</div>

	{#if seedSuccess}
		<div class="mt-4 rounded-lg border p-3 text-sm money-positive">
			{seedSuccess}
		</div>
	{/if}

	{#if seedError}
		<div class="mt-4 rounded-lg border p-3 text-sm money-negative">
			{seedError}
		</div>
	{/if}
</div>

{#if showSeedModal}
	<SeedSampleDataModal onClose={closeSeedModal} onSeeded={handleSeeded} />
{/if}