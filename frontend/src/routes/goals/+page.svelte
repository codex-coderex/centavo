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
		if (!value) return 'No target date';

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

		if (!name.trim()) {
			error = 'Goal name is required.';
			return;
		}

		if (!targetAmount.trim()) {
			error = 'Target amount is required.';
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
		if (!confirm(`Mark "${goal.name}" as completed?`)) {
			return;
		}

		error = '';
		notice = '';

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

<section>
	<div class="mb-8 flex items-start justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight text-slate-100">Goals</h1>
			<p class="mt-2 text-sm text-slate-400">
				Track savings goals and target dates.
			</p>
		</div>

		<div class="rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-400">
			{goals.length} goals
		</div>
	</div>

	{#if error}
		<div class="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	{#if notice}
		<div class="mb-4 rounded-xl border border-emerald-500/40 bg-emerald-950/40 p-4 text-sm text-emerald-200">
			{notice}
		</div>
	{/if}

	<div class="grid gap-6 xl:grid-cols-[380px_1fr]">
		<form
			class="rounded-xl border border-slate-800 bg-slate-900 p-5"
			onsubmit={(event) => {
				event.preventDefault();
				submitGoal();
			}}
		>
			<h2 class="text-lg font-semibold text-slate-100">New goal</h2>
			<p class="mt-1 text-sm text-slate-400">
				Add a savings target linked to an account.
			</p>

			<label class="mt-5 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Goal name</span>
				<input
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
					bind:value={name}
					placeholder="Emergency fund"
				/>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Target amount</span>
				<input
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
					bind:value={targetAmount}
					placeholder="50000"
				/>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Account</span>
				<select
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
					bind:value={accountId}
				>
					{#each accounts as account}
						<option value={account.account_id}>{account.name}</option>
					{/each}
				</select>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Target date</span>
				<input
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
					type="date"
					bind:value={targetDate}
				/>
			</label>

			<button
				class="mt-5 w-full rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
				type="submit"
				disabled={saving || accounts.length === 0}
			>
				{saving ? 'Creating...' : 'Create goal'}
			</button>
		</form>

		<div class="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
			<div class="border-b border-slate-800 px-5 py-4">
				<h2 class="text-lg font-semibold text-slate-100">Goals</h2>
				<p class="mt-1 text-sm text-slate-400">
					Active and completed goals.
				</p>
			</div>

			{#if loading}
				<p class="p-5 text-sm text-slate-400">Loading goals...</p>
			{:else}
				<div class="divide-y divide-slate-800">
					{#each goals as goal}
						<div class="flex items-center justify-between gap-4 px-5 py-4">
							<div>
								<p class="font-medium text-slate-100">{goal.name}</p>
								<p class="mt-1 text-xs text-slate-400">
									{formatMoney(goal.target_amount_minor)} · {accountName(goal.account_id)} · {formatDate(goal.target_date)}
								</p>
								<p class="mt-2">
									<span class="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-300">
										{goal.status}
									</span>
								</p>
							</div>

							{#if goal.status !== 'completed'}
								<button
									class="rounded-lg border border-emerald-500/30 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:bg-emerald-950/40"
									type="button"
									onclick={() => complete(goal)}
								>
									Complete
								</button>
							{/if}
						</div>
					{:else}
						<p class="p-5 text-sm text-slate-500">No goals yet.</p>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</section>