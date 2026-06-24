<script lang="ts" module>
	let nextComboboxId = 0;
	let activeComboboxId = $state<string | null>(null);
</script>

<script lang="ts">
	import { tick } from 'svelte';

	type Option = {
		value: string;
		label: string;
	};

	let {
		value = $bindable(),
		options,
		placeholder = 'Select...',
		searchPlaceholder = 'Search...',
		disabled = false,
		onChange
	} = $props<{
		value: string;
		options: Option[];
		placeholder?: string;
		searchPlaceholder?: string;
		disabled?: boolean;
		onChange?: (value: string) => void;
	}>();

	const comboboxId = `combobox-${nextComboboxId++}`;

	let inputEl: HTMLInputElement | undefined = $state();
	let query = $state('');

	let selected = $derived(options.find((option: Option) => option.value === value));
	let open = $derived(activeComboboxId === comboboxId);
	let filteredOptions = $derived(
		options.filter((option: Option) => option.label.toLowerCase().includes(query.trim().toLowerCase()))
	);

	function openCombobox() {
		if (disabled) return;

		query = '';
		activeComboboxId = comboboxId;
	}

	function closeCombobox() {
		if (activeComboboxId === comboboxId) {
			activeComboboxId = null;
		}

		query = '';
	}

	function selectOption(nextValue: string) {
		value = nextValue;
		closeCombobox();
		onChange?.(nextValue);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			closeCombobox();
			return;
		}

		if (event.key === 'Enter' && filteredOptions[0]) {
			event.preventDefault();
			selectOption(filteredOptions[0].value);
		}
	}

	$effect(() => {
		if (disabled) {
			closeCombobox();
		}
	});

	$effect(() => {
		if (open && inputEl) {
			tick().then(() => inputEl?.focus());
		}
	});
</script>

<div
	class="searchable-combobox"
	onfocusout={(event) => {
		if (!event.currentTarget.contains(event.relatedTarget as Node)) {
			closeCombobox();
		}
	}}
>
	{#if open}
		<div class="searchable-combobox-input-wrap">
			<input
				bind:this={inputEl}
				bind:value={query}
				class="combobox searchable-combobox-input"
				placeholder={selected?.label ?? searchPlaceholder}
				onkeydown={handleKeydown}
			/>
			<span class="text-muted">⌄</span>
		</div>
	{:else}
		<button
			class="combobox searchable-combobox-trigger"
			type="button"
			{disabled}
			onclick={openCombobox}
		>
			<span>{selected?.label ?? placeholder}</span>
			<span class="text-muted">⌄</span>
		</button>
	{/if}

	{#if open}
		<div class="searchable-combobox-menu">
			<div class="searchable-combobox-options">
				{#each filteredOptions as option}
					<button
						class:active={option.value === value}
						class="searchable-combobox-option"
						type="button"
						onclick={() => selectOption(option.value)}
					>
						{option.label}
					</button>
				{:else}
					<p class="text-muted px-3 py-2 text-xs">No matches.</p>
				{/each}
			</div>
		</div>
	{/if}
</div>
