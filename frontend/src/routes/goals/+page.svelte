<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { completeGoal, createGoal, getGoals, type Goal } from '$lib/api/goals';

	const userId = 1;

	let goals: Goal[] = $state([]);
	let accounts: Account[] = $state([]);

	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let notice = $state('');

	let name = $state('');
	let targetAmount = $state('');
	let accountId: number | null = $state(null);
	let targetDate = $state('');

	function formatMoney(amountMinor: number) {
		return new Intl.NumberFormat('en-PH', {
			style: 'currency',
			currency: 'PHP'
		}).format(amountMinor / 100);
	}

	function formatDate(value: string | null | undefined) {
		if (!value) return 'No date';
		return new Date(value).toLocaleDateString('en-PH', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function accountName(id: number) {
		return accounts.find((account) => account.account_id === id)?.name ?? `Account ${id}`;
	}

	async function loadPage() {
		loading = true;
		error = '';
		notice = '';

		try {
			const [goalRows, accountRows] = await Promise.all([
				getGoals(userId),
				getAccounts(userId)
			]);

			goals = goalRows;
			accounts = accountRows;

			if (accountId === null && accountRows.length > 0) {
				accountId = accountRows[0].account_id;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function submitGoal() {
		error = '';
		notice = '';

		if (!name.trim() || !targetAmount.trim()) {
			error = 'Name and target amount are required.';
			return;
		}

		if (accountId === null) {
			error = 'Create an account first.';
			return;
		}

		saving = true;

		try {
			await createGoal({
				user_id: userId,
				name: name.trim(),
				target_amount: targetAmount,
				account_id: accountId,
				target_date: targetDate || null
			});

			name = '';
			targetAmount = '';
			targetDate = '';
			notice = 'Goal created.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function complete(goal: Goal) {
		if (!confirm(`Mark "${goal.name}" as completed?`)) return;
		try {
			await completeGoal(goal.goal_id);
			notice = 'Goal completed.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadPage);
</script>

<div class="flex flex-col gap-8 p-8">
	<div class="flex items-end justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Plan</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-50">Goals</h1>
		</div>
		<div class="rounded-full border border-slate-800/60 bg-slate-900/80 px-3 py-1 text-xs font-medium text-slate-400">
			{goals.length} goals
		</div>
	</div>

	{#if error}
		<div class="rounded-2xl border border-red-500/30 bg-red-950/30 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-sm text-emerald-200">
			{notice}
		</div>
	{/if}

	<div class="grid gap-4 xl:grid-cols-[380px_1fr]">
		<form
			class="rounded-2xl border border-slate-800/60 bg-slate-900/80 p-6"
			onsubmit={(e) => { e.preventDefault(); submitGoal(); }}
		>
			<p class="text-sm font-semibold text-slate-100">New goal</p>
			<p class="mt-1 text-xs text-slate-500">Add a savings target linked to an account.</p>

			<label class="mt-5 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Goal name</span>
				<input class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400" bind:value={name} placeholder="Emergency fund" />
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Target amount</span>
				<input class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400" bind:value={targetAmount} placeholder="50000" />
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Account</span>
				<select class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400" bind:value={accountId}>
					{#each accounts as account}
						<option value={account.account_id}>{account.name}</option>
					{/each}
				</select>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Target date</span>
				<input class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400" type="date" bind:value={targetDate} />
			</label>

			<button
				class="mt-5 w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-60"
				type="submit"
				disabled={saving || accounts.length === 0}
			>
				{saving ? 'Creating...' : 'Create goal'}
			</button>
		</form>

		<div class="overflow-hidden rounded-2xl border border-slate-800/60 bg-slate-900/80">
			<div class="border-b border-slate-800/60 px-6 py-5">
				<p class="text-sm font-semibold text-slate-100">Goals</p>
			</div>

			{#if loading}
				<p class="px-6 py-12 text-center text-sm text-slate-600">Loading goals...</p>
			{:else}
				<div class="divide-y divide-slate-800/60">
					{#each goals as goal}
						<div class="flex items-center justify-between gap-4 px-6 py-4">
							<div>
								<p class="font-medium text-slate-100">{goal.name}</p>
								<p class="mt-1 text-xs text-slate-400">
									{formatMoney(goal.target_amount_minor)} · {accountName(goal.account_id)} · {formatDate(goal.target_date)}
								</p>
								<span class="mt-2 inline-block rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-300">
									{goal.status}
								</span>
							</div>

							{#if goal.status !== 'completed'}
								<button
									class="rounded-lg border border-emerald-500/30 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:bg-emerald-950/40"
									onclick={() => complete(goal)}
								>
									Complete
								</button>
							{/if}
						</div>
					{:else}
						<p class="px-6 py-12 text-center text-sm text-slate-600">No goals yet.</p>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>