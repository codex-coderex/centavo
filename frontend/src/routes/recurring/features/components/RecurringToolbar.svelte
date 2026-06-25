<script lang="ts">
	let { archivedCount, showArchived, onAdd, onArchived } = $props<{
		archivedCount: number;
		showArchived: boolean;
		onAdd: () => void;
		onArchived: () => void;
	}>();
</script>

<div class="flex flex-wrap items-center gap-2">
	<button class="secondary-action" type="button" onclick={onArchived}>
		{showArchived ? 'Active rules' : `Archived (${archivedCount})`}
	</button>
	<button class="primary-action" type="button" onclick={onAdd}>+ New Recurring</button>
</div>
