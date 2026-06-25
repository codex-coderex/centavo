<script lang="ts">
	let {
		name = $bindable(),
		error,
		saving,
		title,
		submitLabel,
		savingLabel,
		onClose,
		onSubmit
	} = $props<{
		name: string;
		error: string;
		saving: boolean;
		title: string;
		submitLabel: string;
		savingLabel: string;
		onClose: () => void;
		onSubmit: () => void | Promise<void>;
	}>();
</script>

<div class="modal-backdrop">
	<form
		class="modal-card"
		onsubmit={(event) => {
			event.preventDefault();
			onSubmit();
		}}
	>
		<div class="flex items-start justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">Tags</p>
				<h2 class="mt-1 text-xl font-bold">{title}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<label class="mt-6 grid gap-2">
			<span class="text-sm font-medium">Tag name</span>
			<input bind:value={name} placeholder="Urgent, reimbursable, shared" />
		</label>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<button class="primary-action mt-6 w-full" type="submit" disabled={saving}>
			{saving ? savingLabel : submitLabel}
		</button>
	</form>
</div>
