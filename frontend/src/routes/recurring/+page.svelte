<script lang="ts">
	import { onMount } from 'svelte';
	import { getAccounts, type Account } from '$lib/api/accounts';
	import { getAllCategories, type Category } from '$lib/api/categories';
	import SearchableCombobox from '$lib/shared/components/SearchableCombobox.svelte';
	import {
		createRecurringRule,
		deactivateRecurringRule,
		generateTransaction,
		getRecurringRules,
		pauseRecurringRule,
		resumeRecurringRule,
		type FrequencyUnit,
		type RecurringRule
	} from '$lib/api/recurring';

	const userId = 1;

	let recurringRules: RecurringRule[] = $state([]);
	let accounts: Account[] = $state([]);
	let categories: Category[] = $state([]);

	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let notice = $state('');

	let accountId: number | null = $state(null);
	let categoryId: number | null = $state(null);
	let name = $state('');
	let amount = $state('');
	let interval = $state(1);
	let frequencyUnit: FrequencyUnit = $state('month');
	let nextDue = $state(new Date().toISOString().slice(0, 10));
	let endDate = $state('');

	const frequencyOptions: { value: FrequencyUnit; label: string }[] = [
		{ value: 'day', label: 'Day' },
		{ value: 'week', label: 'Week' },
		{ value: 'month', label: 'Month' },
		{ value: 'year', label: 'Year' }
	];
	let accountOptions = $derived(
		accounts.map((account: Account) => ({
			value: String(account.account_id),
			label: account.name
		}))
	);
	let categoryOptions = $derived(
		categories.map((category: Category) => ({
			value: String(category.category_id),
			label: category.name
		}))
	);

	function formatMoney(amountMinor: number) {
		return new Intl.NumberFormat('en-PH', {
			style: 'currency',
			currency: 'PHP'
		}).format(amountMinor / 100);
	}

	function formatDate(value: string | null | undefined) {
		if (!value) return '—';

		return new Date(value).toLocaleDateString('en-PH', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function accountName(id: number) {
		return accounts.find((account) => account.account_id === id)?.name ?? `Account ${id}`;
	}

	function categoryName(id: number) {
		return categories.find((category) => category.category_id === id)?.name ?? `Category ${id}`;
	}

	async function loadPage() {
		loading = true;
		error = '';
		notice = '';

		try {
			const [recurringRows, accountRows, categoryRows] = await Promise.all([
				getRecurringRules(userId),
				getAccounts(userId),
				getAllCategories(userId)
			]);

			recurringRules = recurringRows;
			accounts = accountRows;
			categories = categoryRows;

			if (accountId === null && accountRows.length > 0) {
				accountId = accountRows[0].account_id;
			}

			if (categoryId === null && categoryRows.length > 0) {
				categoryId = categoryRows[0].category_id;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	async function submitRecurring() {
		error = '';
		notice = '';

		if (accountId === null) {
			error = 'Create an account first.';
			return;
		}

		if (categoryId === null) {
			error = 'Create a category first.';
			return;
		}

		if (!amount.trim()) {
			error = 'Amount is required.';
			return;
		}

		if (interval <= 0) {
			error = 'Interval must be greater than zero.';
			return;
		}

		if (!nextDue) {
			error = 'Next due date is required.';
			return;
		}

		saving = true;

		try {
			await createRecurringRule({
				account_id: accountId,
				category_id: categoryId,
				name: name.trim() || 'Recurring item',
				expected_amount: amount,
				interval,
				frequency_unit: frequencyUnit,
				start_date: nextDue,
				next_due_date: nextDue,
				end_date: endDate || null
			});

			name = '';
			amount = '';
			interval = 1;
			frequencyUnit = 'month';
			nextDue = new Date().toISOString().slice(0, 10);
			endDate = '';

			notice = 'Recurring rule created.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function pause(rule: RecurringRule) {
		error = '';
		notice = '';

		try {
			await pauseRecurringRule(rule.recurring_rule_id);
			notice = 'Recurring rule paused.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function resume(rule: RecurringRule) {
		error = '';
		notice = '';

		try {
			await resumeRecurringRule(rule.recurring_rule_id);
			notice = 'Recurring rule resumed.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function deactivate(rule: RecurringRule) {
		if (!confirm(`Deactivate "${rule.name ?? 'recurring rule'}"?`)) {
			return;
		}

		error = '';
		notice = '';

		try {
			await deactivateRecurringRule(rule.recurring_rule_id);
			notice = 'Recurring rule deactivated.';
			await loadPage();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	async function generate(rule: RecurringRule) {
		if (!confirm(`Generate a transaction for "${rule.name ?? 'recurring rule'}"?`)) {
			return;
		}

		error = '';
		notice = '';

		try {
			await generateTransaction(rule.recurring_rule_id);
			notice = 'Transaction generated.';
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
			<h1 class="text-3xl font-bold tracking-tight text-slate-100">Recurring</h1>
			<p class="mt-2 text-sm text-slate-400">
				Manage recurring bills, income, and subscriptions.
			</p>
		</div>

		<div class="rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-400">
			{recurringRules.length} rules
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
				submitRecurring();
			}}
		>
			<h2 class="text-lg font-semibold text-slate-100">New recurring rule</h2>
			<p class="mt-1 text-sm text-slate-400">
				Add a repeating income or expense rule.
			</p>

			<label class="mt-5 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Name</span>
				<input
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
					bind:value={name}
					placeholder="Netflix, Rent, Salary"
				/>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Amount</span>
				<input
					class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400"
					bind:value={amount}
					placeholder="-499 or 50000"
				/>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Account</span>
				<SearchableCombobox
					value={accountId === null ? '' : String(accountId)}
					options={accountOptions}
					placeholder="Select an account"
					searchPlaceholder="Search accounts..."
					disabled={accounts.length === 0}
					onChange={(value) => accountId = Number(value)}
				/>
			</label>

			<label class="mt-4 grid gap-2">
				<span class="text-sm font-medium text-slate-300">Category</span>
				<SearchableCombobox
					value={categoryId === null ? '' : String(categoryId)}
					options={categoryOptions}
					placeholder="Select a category"
					searchPlaceholder="Search categories..."
					disabled={categories.length === 0}
					onChange={(value) => categoryId = Number(value)}
				/>
			</label>

			<div class="mt-4 grid grid-cols-[1fr_1.4fr] gap-4">
				<label class="grid gap-2">
					<span class="text-sm font-medium text-slate-300">Every</span>
					<input
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
						type="number"
						min="1"
						bind:value={interval}
					/>
				</label>

				<label class="grid gap-2">
					<span class="text-sm font-medium text-slate-300">Frequency</span>
					<SearchableCombobox
						bind:value={frequencyUnit}
						options={frequencyOptions}
						placeholder="Select a frequency"
						searchPlaceholder="Search frequencies..."
					/>
				</label>
			</div>

			<div class="mt-4 grid gap-4 sm:grid-cols-2">
				<label class="grid gap-2">
					<span class="text-sm font-medium text-slate-300">Next due</span>
					<input
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
						type="date"
						bind:value={nextDue}
					/>
				</label>

				<label class="grid gap-2">
					<span class="text-sm font-medium text-slate-300">End date</span>
					<input
						class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-400"
						type="date"
						bind:value={endDate}
					/>
				</label>
			</div>

			<button
				class="mt-5 w-full rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
				type="submit"
				disabled={saving || accounts.length === 0 || categories.length === 0}
			>
				{saving ? 'Creating...' : 'Create recurring rule'}
			</button>
		</form>

		<div class="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
			<div class="border-b border-slate-800 px-5 py-4">
				<h2 class="text-lg font-semibold text-slate-100">Recurring rules</h2>
				<p class="mt-1 text-sm text-slate-400">
					Current repeating items.
				</p>
			</div>

			{#if loading}
				<p class="p-5 text-sm text-slate-400">Loading recurring rules...</p>
			{:else}
				<div class="divide-y divide-slate-800">
					{#each recurringRules as rule}
						<div class="px-5 py-4">
							<div class="flex items-start justify-between gap-4">
								<div>
									<p class="font-medium text-slate-100">
										{rule.name ?? 'Recurring item'}
									</p>
									<p class="mt-1 text-xs text-slate-400">
										{formatMoney(rule.expected_amount_minor)}
										· {accountName(rule.account_id)}
										· {categoryName(rule.category_id)}
									</p>
									<p class="mt-1 text-xs text-slate-500">
										Every {rule.interval} {rule.frequency_unit}
										· next due {formatDate(rule.next_due_date)}
										· ends {formatDate(rule.end_date)}
									</p>
									<p class="mt-2">
										<span class="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-300">
											{rule.status}
										</span>
									</p>
								</div>

								<div class="flex flex-wrap justify-end gap-2">
									{#if rule.status === 'active'}
										<button
											class="rounded-lg border border-amber-500/30 px-3 py-1.5 text-xs font-medium text-amber-300 hover:bg-amber-950/40"
											type="button"
											onclick={() => pause(rule)}
										>
											Pause
										</button>
									{:else if rule.status === 'paused'}
										<button
											class="rounded-lg border border-emerald-500/30 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:bg-emerald-950/40"
											type="button"
											onclick={() => resume(rule)}
										>
											Resume
										</button>
									{/if}

									<button
										class="rounded-lg border border-indigo-500/30 px-3 py-1.5 text-xs font-medium text-indigo-300 hover:bg-indigo-950/40"
										type="button"
										onclick={() => generate(rule)}
									>
										Generate
									</button>

									<button
										class="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs font-medium text-red-300 hover:bg-red-950/40"
										type="button"
										onclick={() => deactivate(rule)}
									>
										Deactivate
									</button>
								</div>
							</div>
						</div>
					{:else}
						<p class="p-5 text-sm text-slate-500">No recurring rules yet.</p>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</section>
