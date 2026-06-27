<script lang="ts">
	let {
		eyebrow,
		title,
		message,
		detail,
		confirmLabel,
		savingLabel,
		saving,
		error = '',
		variant = 'danger',
		onClose,
		onConfirm
	} = $props<{
		eyebrow: string;
		title: string;
		message: string;
		detail: string;
		confirmLabel: string;
		savingLabel: string;
		saving: boolean;
		error?: string;
		variant?: 'danger' | 'warning' | 'success';
		onClose: () => void;
		onConfirm: () => void | Promise<void>;
	}>();

	let borderColor = $derived(
		variant === 'success' ? 'rgba(66, 142, 91, 0.3)' : variant === 'warning' ? 'rgba(214, 139, 67, 0.35)' : 'rgba(189, 74, 63, 0.3)'
	);
	let backgroundColor = $derived(
		variant === 'success' ? 'rgba(66, 142, 91, 0.08)' : variant === 'warning' ? 'rgba(214, 139, 67, 0.09)' : 'rgba(189, 74, 63, 0.08)'
	);
	let messageClass = $derived(
		variant === 'success' ? 'money-positive' : variant === 'warning' ? '' : 'money-negative'
	);
	let buttonClass = $derived(variant === 'danger' ? 'danger-action' : 'primary-action');
</script>

<div class="modal-backdrop">
	<div class="modal-card">
		<div class="flex items-start justify-between gap-4">
			<div>
				<p class="dashboard-eyebrow text-xs font-semibold uppercase tracking-widest">{eyebrow}</p>
				<h2 class="mt-1 text-xl font-bold">{title}</h2>
			</div>
			<button class="secondary-action" type="button" onclick={onClose}>Close</button>
		</div>

		<div class="mt-6 rounded-xl border p-4 text-sm" style={`border-color: ${borderColor}; background: ${backgroundColor}`}>
			<p class={`font-semibold ${messageClass}`}>{message}</p>
			<p class="text-muted mt-2">{detail}</p>
		</div>

		{#if error}
			<div class="mt-4 rounded-xl border p-3 text-sm money-negative" style="border-color: rgba(189, 74, 63, 0.3); background: rgba(189, 74, 63, 0.08)">
				{error}
			</div>
		{/if}

		<div class="mt-6 flex justify-end gap-2">
			<button class="secondary-action" type="button" onclick={onClose}>Cancel</button>
			<button class={buttonClass} type="button" disabled={saving} onclick={onConfirm}>
				{saving ? savingLabel : confirmLabel}
			</button>
		</div>
	</div>
</div>
