<script lang="ts">
	import { dismissToast, toasts } from '$lib/shared/toast';
</script>

<div class="toast-host" aria-live="polite" aria-atomic="true">
	{#each $toasts as toast}
		<div class={`toast-card ${toast.kind}`}>
			<p>{toast.message}</p>
			<button type="button" aria-label="Dismiss notification" onclick={() => dismissToast(toast.id)}>Close</button>
		</div>
	{/each}
</div>
