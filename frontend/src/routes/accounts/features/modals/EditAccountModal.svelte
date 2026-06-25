<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import { sanitizeBalance } from '../utils/accountFormat';

	let {
		account,
		name = $bindable(),
		balance = $bindable(),
		error,
		saving,
		fmtBalance,
		accountBalance,
		onClose,
		onSubmit
	} = $props<{
		account: Account;
		name: string;
		balance: string;
		error: string;
		saving: boolean;
		fmtBalance: (minor: number | undefined | null) => string;
		accountBalance: (account: Account) => number;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();

	function sanitizeBalanceInput(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const next = sanitizeBalance(input.value);

		balance = next;
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
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Edit account</p>
				<h2 class="mt-1 text-xl font-bold">{account.name}</h2>
				<p class="text-muted mt-1 text-sm">Current balance: {fmtBalance(accountBalance(account))}</p>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Account name</span>
			<input bind:value={name} placeholder="Landbank, Cash, Savings" />
		</label>

		<label class="mt-4 grid gap-2">
			<span class="text-sm font-medium">Current balance</span>
			<input
				bind:value={balance}
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
			{saving ? 'Saving...' : 'Save account'}
		</button>
	</form>
</div>
