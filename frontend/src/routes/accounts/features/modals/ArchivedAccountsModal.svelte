<script lang="ts">
	import type { Account } from '$lib/api/accounts';

	let {
		accounts,
		error,
		restoringId,
		typeLabel,
		fmtBalance,
		accountBalance,
		onClose,
		onEdit,
		onRestore
	} = $props<{
		accounts: Account[];
		error: string;
		restoringId: number | null;
		typeLabel: (type: string) => string;
		fmtBalance: (minor: number | undefined | null) => string;
		accountBalance: (account: Account) => number;
		onClose: () => void;
		onEdit: (account: Account) => void;
		onRestore: (account: Account) => void | Promise<void>;
	}>();
</script>

<div class="modal-backdrop">
	<div class="modal-card max-h-[85vh] overflow-y-auto">
		<div class="flex items-start justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Archived accounts</p>
				<h2 class="mt-1 text-xl font-bold">Deactivated accounts</h2>
				<p class="text-muted mt-1 text-sm">Re-enable archived accounts from here.</p>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="mt-6 grid gap-3">
			{#each accounts as account}
				<div class="flex items-center justify-between gap-4 rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-surface-strong)">
					<div>
						<p class="font-semibold">{account.name}</p>
						<p class="text-muted mt-1 text-xs">
							{typeLabel(account.type)} · {fmtBalance(accountBalance(account))}
						</p>
					</div>

					<div class="flex shrink-0 gap-2">
						<button class="secondary-action" type="button" onclick={() => onEdit(account)}>
							Edit
						</button>
						<button
							class="primary-action"
							type="button"
							disabled={restoringId === account.account_id}
							onclick={() => onRestore(account)}
						>
							{restoringId === account.account_id ? 'Enabling...' : 'Enable'}
						</button>
					</div>
				</div>
			{:else}
				<p class="text-muted rounded-xl border p-4 text-sm" style="border-color: var(--app-border)">
					No archived accounts.
				</p>
			{/each}
		</div>
	</div>
</div>
