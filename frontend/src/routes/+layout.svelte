<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import './layout.css';
	import AppShell from '$lib/shared/components/AppShell.svelte';

	let { children } = $props();

	onMount(() => {
		// If pywebview boots onto the physical index.html file path...
		if (window.location.pathname.endsWith('index.html')) {
			// Automatically navigate to the root dashboard page
			setTimeout(() => {
				goto('/', { replaceState: true });
			}, 0);
		}
	});
</script>

<AppShell>
	{@render children()}
</AppShell>
