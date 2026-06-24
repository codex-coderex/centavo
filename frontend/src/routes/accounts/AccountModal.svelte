<script lang="ts">
	import type { AccountType } from '$lib/api/accounts';

	export type AccountTypeOption = {
		value: AccountType;
		label: string;
	};

	let {
		name = $bindable(),
		type = $bindable(),
		openingBalance = $bindable(),
		accountTypes,
		error,
		saving,
		onClose,
		onSubmit
	} = $props<{
		name: string;
		type: AccountType;
		openingBalance: string;
		accountTypes: AccountTypeOption[];
		error: string;
		saving: boolean;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	function sanitizeBalanceInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = input.value
			.replace(/[^\d.]/g, '')
			.replace(/(\..*)\./g, '$1')
			.replace(/^(\d*)(\.\d{0,2}).*$/, '$1$2');

		openingBalance = next;
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
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Make account</p>
				<h2 class="mt-1 text-xl font-bold">New account</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Account name</span>
			<input bind:value={name} placeholder="Landbank, Cash, Savings" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Account type</span>
			<select class="combobox" bind:value={type}>
				{#each accountTypes as accountType}
					<option value={accountType.value}>{accountType.label}</option>
				{/each}
			</select>
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Opening balance</span>
			<input
				bind:value={openingBalance}
				inputmode="decimal"
				placeholder="0.00"
				oninput={sanitizeBalanceInput}
			/>
		</label>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<button class="primary-action mt-6 w-full" type="submit" disabled={saving}>
			{saving ? 'Creating...' : 'Create account'}
		</button>
	</form>
</div>
