<script lang="ts">
	let { onAdd } = $props<{
		onAdd: () => void;
	}>();
</script>

<div class="flex flex-wrap items-center justify-end gap-2">
	<button class="primary-action" type="button" onclick={onAdd}>+ New goal</button>
</div>
