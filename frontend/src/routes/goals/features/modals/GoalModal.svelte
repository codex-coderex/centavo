<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';
	import { sanitizeAmountInput } from '../utils/goalFormat';

	let {
		name = $bindable(),
		targetAmount = $bindable(),
		targetDate = $bindable(),
		accountId = $bindable(),
		accounts,
		error,
		saving,
		title,
		submitLabel,
		savingLabel,
		onClose,
		onSubmit
	} = $props<{
		name: string;
		targetAmount: string;
		targetDate: string;
		accountId: number;
		accounts: Account[];
		error: string;
		saving: boolean;
		title: string;
		submitLabel: string;
		savingLabel: string;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	let accountOptions = $derived(
		accounts.map((account: Account) => ({
			value: String(account.account_id),
			label: account.name
		}))
	);

	function handleAmountInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = sanitizeAmountInput(input.value);

		targetAmount = next;
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
			<h2 class="text-xl font-bold">{title}</h2>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Goal name</span>
			<input bind:value={name} placeholder="Emergency fund" />
		</label>

		<div class="mt-4 grid gap-4 sm:grid-cols-2">
			<label class="grid gap-2">
				<span class="text-sm font-medium">Target amount</span>
				<input bind:value={targetAmount} inputmode="decimal" placeholder="30000" oninput={handleAmountInput} />
			</label>

			<label class="grid gap-2">
				<span class="text-sm font-medium">Target date</span>
				<input bind:value={targetDate} type="date" />
			</label>
		</div>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Linked account</span>
			<SearchableCombobox
				value={String(accountId)}
				options={accountOptions}
				placeholder="Select an account"
				searchPlaceholder="Search accounts..."
				disabled={accounts.length === 0}
				onChange={(value) => accountId = Number(value)}
			/>
		</label>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="mt-6 flex justify-end gap-2">
			<button class="secondary-action" type="button" onclick={onClose}>Cancel</button>
			<button class="primary-action" type="submit" disabled={saving}>
				{saving ? savingLabel : submitLabel}
			</button>
		</div>
	</form>
</div>
