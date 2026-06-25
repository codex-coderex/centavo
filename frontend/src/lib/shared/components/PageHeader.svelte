<script lang="ts">
	let {
		eyebrow,
		title,
		subtitle = '',
		children
	} = $props<{
		eyebrow: string;
		title: string;
		subtitle?: string;
		children?: import('svelte').Snippet;
	}>();
</script>

<header class="page-header">
	<div>
		<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">{eyebrow}</p>
		<h1 class="mt-1 text-3xl font-bold tracking-tight">{title}</h1>
		{#if subtitle}
			<p class="text-muted mt-2 text-sm">{subtitle}</p>
		{/if}
	</div>

	{#if children}
		<div class="flex flex-wrap justify-end gap-2">
			{@render children()}
		</div>
	{/if}
</header>
