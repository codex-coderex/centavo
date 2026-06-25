<script lang="ts">
	let {
		archivedCount,
		onAdd,
		onArchived
	} = $props<{
		archivedCount: number;
		onAdd: () => void;
		onArchived: () => void;
	}>();
</script>

<div class="flex flex-wrap justify-end gap-2">
	<button class="secondary-action" type="button" onclick={onArchived}>
		Archived accounts ({archivedCount})
	</button>
	<button class="primary-action" type="button" onclick={onAdd}>Add account</button>
</div>
