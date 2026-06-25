<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsers, type User } from '$lib/api/users';
	import CategorySettings from './features/categories/components/CategorySettings.svelte';
	import AboutSettings from './features/general/components/AboutSettings.svelte';
	import ProfileSettings from './features/general/components/ProfileSettings.svelte';

	let users: User[] = $state([]);
	let loadingUsers = $state(true);
	let error = $state('');

	async function loadUsers() {
		loadingUsers = true;
		error = '';

		try {
			users = await getUsers();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loadingUsers = false;
		}
	}

	onMount(loadUsers);
</script>

<section class="flex flex-col gap-8 p-8">
	<div class="flex items-end justify-between gap-4">
		<div>
			<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Control center</p>
			<h1 class="mt-1 text-3xl font-bold tracking-tight">Settings</h1>
			<p class="text-muted mt-2 text-sm">
				App preferences, local data, and category configuration.
			</p>
		</div>
	</div>

	{#if error}
		<div class="rounded-2xl border p-4 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
			{error}
		</div>
	{/if}

	<CategorySettings />

	<div class="grid gap-6 xl:grid-cols-3">
		<ProfileSettings {users} loading={loadingUsers} />
		<AboutSettings />
	</div>
</section>
