<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsers, type User } from '$lib/api/users';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
	import CategorySettings from './features/categories/components/CategorySettings.svelte';
	import AboutSettings from './features/general/components/AboutSettings.svelte';
	import ProfileSettings from './features/general/components/ProfileSettings.svelte';
	import SettingsShell, { type SettingsSection } from './features/layout/components/SettingsShell.svelte';
	import TagSettings from './features/tags/components/TagSettings.svelte';

	let users: User[] = $state([]);
	let loadingUsers = $state(true);
	let error = $state('');
	let activeSection: SettingsSection = $state('about');

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

<ToastOnChange {error} />

<SettingsShell bind:activeSection>
	{#if activeSection === 'about'}
		<div class="grid gap-5 xl:grid-cols-2">
			<AboutSettings />
			<ProfileSettings {users} loading={loadingUsers} onRefresh={loadUsers} />
		</div>
	{:else if activeSection === 'tags'}
		<TagSettings />
	{:else}
		<CategorySettings />
	{/if}
</SettingsShell>
