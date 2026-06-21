<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsers, type User } from '$lib/api/users';

	let users: User[] = $state([]);
	let error = $state('');
	let loading = $state(true);

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
		<h1 class="text-3xl font-bold tracking-tight text-slate-100">Offline Finance</h1>
		<p class="mt-2 text-sm text-slate-400">Local-first personal finance app.</p>
	</div>

	{#if loading}
		<p class="text-slate-300">Loading...</p>
	{:else if error}
		<div class="rounded-xl border border-red-500/40 bg-red-950/40 p-4 text-red-200">
			<p class="font-semibold">Bridge test failed</p>
			<p class="mt-2">{error}</p>
		</div>
	{:else}
		<div class="rounded-xl border border-slate-800 bg-slate-900 p-6">
			<p class="mb-3 font-semibold text-slate-100">Users from Python/SQLite:</p>
			<pre class="overflow-auto text-sm text-slate-200">{JSON.stringify(users, null, 2)}</pre>
		</div>
	{/if}
</section>