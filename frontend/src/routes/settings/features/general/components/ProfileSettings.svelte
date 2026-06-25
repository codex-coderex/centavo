<script lang="ts">
	import type { User } from '$lib/api/users';

	let { users, loading } = $props<{
		users: User[];
		loading: boolean;
	}>();
</script>

<div class="dashboard-card p-5">
	<h2 class="text-lg font-semibold">Profile</h2>
	<p class="text-muted mt-1 text-sm">Current local user record.</p>

	{#if loading}
		<p class="text-muted mt-5 text-sm">Loading user...</p>
	{:else}
		<div class="mt-5 space-y-3">
			{#each users as user}
				<div class="rounded-lg border p-4" style="border-color: var(--app-border); background: var(--app-surface-strong)">
					<p class="font-medium">{user.name}</p>
					<p class="text-muted mt-1 text-xs">User ID: {user.user_id}</p>
				</div>
			{:else}
				<p class="text-muted text-sm">No user found.</p>
			{/each}
		</div>
	{/if}
</div>
