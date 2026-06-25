<script lang="ts">
	export type SettingsSection = 'about' | 'tags' | 'categories';

	let {
		activeSection = $bindable(),
		children
	} = $props<{
		activeSection: SettingsSection;
		children: import('svelte').Snippet;
	}>();

	const sections: { id: SettingsSection; label: string; description: string }[] = [
		{ id: 'about', label: 'About', description: 'Local app details' },
		{ id: 'tags', label: 'Tags', description: 'Transaction labels' },
		{ id: 'categories', label: 'Categories', description: 'Groups and categories' }
	];
</script>

<section class="settings-page flex min-h-screen flex-col">
	<header class="border-b px-6 py-5" style="border-color: var(--app-border); background: var(--app-surface)">
		<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Control center</p>
		<h1 class="mt-1 text-3xl font-bold tracking-tight">Settings</h1>
	</header>

	<div class="grid flex-1 gap-5 p-5 lg:grid-cols-[15rem_minmax(0,1fr)]">
		<aside class="dashboard-card h-fit overflow-hidden p-2">
			{#each sections as section}
				<button
					class={`w-full rounded-xl px-4 py-3 text-left transition-colors ${activeSection === section.id ? 'bg-(--app-orange-soft)' : 'hover:bg-black/4'}`}
					type="button"
					onclick={() => activeSection = section.id}
				>
					<p class={activeSection === section.id ? 'font-bold text-(--app-orange-dark)' : 'font-semibold'}>
						{section.label}
					</p>
					<p class="text-muted mt-0.5 text-xs">{section.description}</p>
				</button>
			{/each}
		</aside>

		<div class="min-w-0">
			{@render children()}
		</div>
	</div>
</section>
