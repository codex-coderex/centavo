<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Goal } from '$lib/api/goals';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';
	import { formatMoney, sanitizeAmountInput } from '../utils/goalFormat';

	let {
		goal,
		amount = $bindable(),
		accountId = $bindable(),
		accounts,
		error,
		saving,
		onClose,
		onSubmit
	} = $props<{
		goal: Goal;
		amount: string;
		accountId: number;
		accounts: Account[];
		error: string;
		saving: boolean;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	let accountOptions = $derived(
		accounts.map((account: Account) => ({
			value: String(account.account_id),
			label: `${account.name} (${formatMoney(account.current_balance_minor)} available)`
		}))
	);

	function handleAmountInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = sanitizeAmountInput(input.value);

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
			<h2 class="text-xl font-bold">Add funds — {goal.name}</h2>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Amount</span>
			<input bind:value={amount} inputmode="decimal" placeholder="1000" oninput={handleAmountInput} />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">From account</span>
			<SearchableCombobox
				value={String(accountId)}
				options={accountOptions}
				placeholder="Select an account"
				searchPlaceholder="Search accounts..."
				disabled={accounts.length === 0}
				onChange={(value) => accountId = Number(value)}
			/>
		</label>

		<p class="text-muted mt-4 text-xs">
			Funds are held in this goal allocation and removed from the account's available balance.
		</p>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="mt-6 flex justify-end gap-2">
			<button class="secondary-action" type="button" onclick={onClose}>Cancel</button>
			<button class="primary-action" type="submit" disabled={saving}>
				{saving ? 'Adding...' : 'Add funds'}
			</button>
		</div>
	</form>
</div>
