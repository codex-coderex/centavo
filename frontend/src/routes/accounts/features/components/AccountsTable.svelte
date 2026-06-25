<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import { accountBalance, formatBalance, typeColor, typeLabel } from '../utils/accountFormat';

	let {
		accounts,
		loading,
		onEdit,
		onArchive
	} = $props<{
		accounts: Account[];
		loading: boolean;
		onEdit: (account: Account) => void;
		onArchive: (account: Account) => void | Promise<void>;
	}>();
</script>

<div class="dashboard-card overflow-hidden">
	<div class="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-5" style="border-color: var(--app-border)">
		<div>
			<p class="text-sm font-semibold">Active accounts</p>
			<p class="text-muted mt-1 text-xs">Archived accounts are hidden from this list.</p>
		</div>

		<span class="pill">{accounts.length} active</span>
	</div>

	{#if loading}
		<p class="text-muted px-6 py-12 text-center text-sm">Loading accounts...</p>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="text-muted text-[11px] font-bold uppercase tracking-widest">
					<tr>
						<th class="px-6 py-3">Name</th>
						<th class="px-6 py-3">Type</th>
						<th class="px-6 py-3">Balance</th>
						<th class="px-6 py-3">Status</th>
						<th class="px-6 py-3 text-right">Actions</th>
					</tr>
				</thead>

				<tbody>
					{#each accounts as account}
						<tr class="border-t" style="border-color: var(--app-border)">
							<td class="px-6 py-4 font-medium">{account.name}</td>
							<td class="px-6 py-4">
								<span class="inline-flex items-center gap-2">
									<span
										class="h-2 w-2 shrink-0 rounded-full"
										style="background:{typeColor(account.type)}"
									></span>
									{typeLabel(account.type)}
								</span>
							</td>
							<td class="px-6 py-4 font-semibold tabular-nums">
								{formatBalance(accountBalance(account))}
							</td>
							<td class="px-6 py-4">
								<span class="pill">{account.status}</span>
							</td>
							<td class="px-6 py-4 text-right">
								<div class="flex justify-end gap-2">
									<button class="secondary-action" type="button" onclick={() => onEdit(account)}>
										Edit
									</button>
									<button class="danger-action" type="button" onclick={() => onArchive(account)}>
										Archive
									</button>
								</div>
							</td>
						</tr>
					{:else}
						<tr>
							<td class="text-muted px-6 py-12 text-center text-sm" colspan="5">
								No accounts yet. Create one to get started.
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
