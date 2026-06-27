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

<div class="flex flex-wrap items-center justify-end gap-2">
	<button class="secondary-action" type="button" onclick={onArchived}>
		Archived goals ({archivedCount})
	</button>
	<button class="primary-action" type="button" onclick={onAdd}>+ New goal</button>
</div>
