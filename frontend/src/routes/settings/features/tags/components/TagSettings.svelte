<script lang="ts">
	import { onMount } from 'svelte';
	import { createTag, deleteTag, getTags, updateTag, type Tag } from '$lib/api/tags';
	import ToastOnChange from '$lib/shared/components/ToastOnChange.svelte';
	import TagModal from '../modals/TagModal.svelte';

	const userId = 1;

	let tags: Tag[] = $state([]);
	let editingTag: Tag | null = $state(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let modalError = $state('');
	let notice = $state('');
	let showTagModal = $state(false);
	let tagName = $state('');

	async function loadTags() {
		loading = true;
		error = '';

		try {
			tags = await getTags(userId);
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		} finally {
			loading = false;
		}
	}

	function openCreateTag() {
		notice = '';
		modalError = '';
		editingTag = null;
		tagName = '';
		showTagModal = true;
	}

	function openEditTag(tag: Tag) {
		notice = '';
		modalError = '';
		editingTag = tag;
		tagName = tag.name;
		showTagModal = true;
	}

	function closeTagModal() {
		showTagModal = false;
		modalError = '';
		saving = false;
		editingTag = null;
	}

	async function submitTag() {
		modalError = '';
		notice = '';

		if (!tagName.trim()) {
			modalError = 'Tag name is required.';
			return;
		}

		saving = true;

		try {
			if (editingTag) {
				await updateTag(editingTag.tag_id, { name: tagName.trim() });
				notice = 'Tag updated.';
			} else {
				await createTag({ user_id: userId, name: tagName.trim() });
				notice = 'Tag created.';
			}

			closeTagModal();
			await loadTags();
		} catch (err) {
			modalError = err instanceof Error ? err.message : String(err);
		} finally {
			saving = false;
		}
	}

	async function removeTag(tag: Tag) {
		if (!confirm(`Delete "${tag.name}"? This removes the tag from transactions that use it.`)) return;

		error = '';
		notice = '';

		try {
			await deleteTag(tag.tag_id);
			notice = 'Tag deleted.';
			await loadTags();
		} catch (err) {
			error = err instanceof Error ? err.message : String(err);
		}
	}

	onMount(loadTags);
</script>

<ToastOnChange {error} {notice} />

<section class="flex flex-col gap-4">
	<div class="dashboard-card overflow-hidden">
		<div class="flex flex-wrap items-start justify-between gap-4 border-b px-6 py-5" style="border-color: var(--app-border)">
			<div>
				<h2 class="text-lg font-semibold">Tags</h2>
				<p class="text-muted mt-1 text-sm">Create labels you can attach to transactions.</p>
			</div>

			<button class="primary-action" type="button" onclick={openCreateTag}>Make tag</button>
		</div>

		{#if loading}
			<p class="text-muted p-6 text-sm">Loading tags...</p>
		{:else}
			<div class="divide-y" style="border-color: var(--app-border)">
				{#each tags as tag}
					<div class="flex flex-wrap items-center justify-between gap-4 px-6 py-4">
						<div>
							<p class="font-semibold">{tag.name}</p>
							<p class="text-muted mt-1 text-xs">Tag ID: {tag.tag_id}</p>
						</div>

						<div class="flex gap-2">
							<button class="secondary-action" type="button" onclick={() => openEditTag(tag)}>Edit</button>
							<button class="danger-action" type="button" onclick={() => removeTag(tag)}>Delete</button>
						</div>
					</div>
				{:else}
					<p class="text-muted p-6 text-sm">No tags yet.</p>
				{/each}
			</div>
		{/if}
	</div>
</section>

{#if showTagModal}
	<TagModal
		bind:name={tagName}
		error={modalError}
		{saving}
		title={editingTag ? 'Edit tag' : 'New tag'}
		submitLabel={editingTag ? 'Save tag' : 'Create tag'}
		savingLabel={editingTag ? 'Saving...' : 'Creating...'}
		onClose={closeTagModal}
		onSubmit={submitTag}
	/>
{/if}
