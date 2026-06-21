<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsers, type User } from '$lib/api/users';

	let users: User[] = $state([]);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			users = await getUsers();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	});
</script>

<section>
	<div class="mb-8">
		<h1 class="text-3xl font-bold tracking-tight text-slate-100">Settings</h1>
		<p class="mt-2 text-sm text-slate-400">
			App preferences, local data, and system configuration.
		</p>
	</div>

	{#if error}
		<div class="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-200">
			{error}
		</div>
	{/if}

	<div class="grid gap-6 xl:grid-cols-2">
		<div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
			<h2 class="text-lg font-semibold text-slate-100">Profile</h2>
			<p class="mt-1 text-sm text-slate-400">
				Current local user record.
			</p>

			{#if loading}
				<p class="mt-5 text-sm text-slate-400">Loading user...</p>
			{:else}
				<div class="mt-5 space-y-3">
					{#each users as user}
						<div class="rounded-lg border border-slate-800 bg-slate-950 p-4">
							<p class="font-medium text-slate-100">{user.name}</p>
							<p class="mt-1 text-sm text-slate-400">
								Default currency: {user.currency_code}
							</p>
							<p class="mt-1 text-xs text-slate-600">
								User ID: {user.user_id}
							</p>
						</div>
					{:else}
						<p class="text-sm text-slate-500">No user found.</p>
					{/each}
				</div>
			{/if}
		</div>

		<div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
			<h2 class="text-lg font-semibold text-slate-100">Categories</h2>
			<p class="mt-1 text-sm text-slate-400">
				System category enable/disable controls will live here later.
			</p>

			<div class="mt-5 rounded-lg border border-slate-800 bg-slate-950 p-4">
				<p class="text-sm font-medium text-slate-300">Planned behavior</p>
				<ul class="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-400">
					<li>System categories can be disabled here.</li>
					<li>System categories cannot be deleted.</li>
					<li>Uncategorized cannot be disabled or deleted.</li>
					<li>Custom categories are managed from the Categories page.</li>
				</ul>
			</div>
		</div>

		<div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
			<h2 class="text-lg font-semibold text-slate-100">Local data</h2>
			<p class="mt-1 text-sm text-slate-400">
				Backup, restore, and database location options will go here.
			</p>

			<div class="mt-5 flex flex-wrap gap-3">
				<button
					class="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 opacity-60"
					type="button"
					disabled
				>
					Export backup
				</button>

				<button
					class="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 opacity-60"
					type="button"
					disabled
				>
					Restore backup
				</button>
			</div>
		</div>

		<div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
			<h2 class="text-lg font-semibold text-slate-100">About</h2>
			<p class="mt-1 text-sm text-slate-400">
				Centavo is running locally through pywebview and SQLite.
			</p>

			<div class="mt-5 rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm text-slate-400">
				<p>Mode: Offline desktop</p>
				<p class="mt-1">Storage: Local SQLite database</p>
			</div>
		</div>
	</div>
</section>