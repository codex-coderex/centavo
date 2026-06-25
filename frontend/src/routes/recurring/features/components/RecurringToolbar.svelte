<script lang="ts">
	let { onAdd } = $props<{
		onAdd: () => void;
	}>();
</script>

<button class="primary-action" type="button" onclick={onAdd}>+ New Recurring</button>
