<script lang="ts">
	type ComboboxOption = {
		value: string;
		label: string;
	};

	let {
		id,
		value = $bindable(''),
		options = [],
		placeholder = 'Select an option',
		searchPlaceholder = 'Type to filter...',
		disabled = false,
		onChange
	} = $props<{
		id: string;
		value: string;
		options: ComboboxOption[];
		placeholder?: string;
		searchPlaceholder?: string;
		disabled?: boolean;
		onChange?: (value: string) => void;
	}>();

	let open = $state(false);
	let inputValue = $state('');
	let hasTyped = $state(false);
	let highlightedIndex = $state(0);

	let selectedOption = $derived(options.find((option) => option.value === value));
	let selectedLabel = $derived(selectedOption?.label ?? '');
	let normalizedQuery = $derived(inputValue.trim().toLowerCase());
	let filteredOptions = $derived(
		hasTyped && normalizedQuery
			? options.filter((option) => option.label.toLowerCase().includes(normalizedQuery))
			: options
	);

	$effect(() => {
		if (!open) {
			hasTyped = false;
			highlightedIndex = 0;
		}
	});

	$effect(() => {
		if (highlightedIndex >= filteredOptions.length) {
			highlightedIndex = Math.max(filteredOptions.length - 1, 0);
		}
	});

	function openList() {
		if (disabled) return;
		open = true;
		inputValue = selectedLabel;
		hasTyped = false;
	}

	function selectOption(option: ComboboxOption) {
		value = option.value;
		inputValue = option.label;
		open = false;
		hasTyped = false;
		onChange?.(option.value);
	}

	function handleInput(event: Event) {
		inputValue = (event.currentTarget as HTMLInputElement).value;
		hasTyped = true;
		open = true;
		highlightedIndex = 0;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (disabled) return;

		if (event.key === 'ArrowDown') {
			event.preventDefault();
			open = true;
			highlightedIndex = Math.min(highlightedIndex + 1, Math.max(filteredOptions.length - 1, 0));
		}

		if (event.key === 'ArrowUp') {
			event.preventDefault();
			highlightedIndex = Math.max(highlightedIndex - 1, 0);
		}

		if (event.key === 'Enter' && open) {
			event.preventDefault();
			const option = filteredOptions[highlightedIndex];
			if (option) selectOption(option);
		}

		if (event.key === 'Escape') {
			open = false;
		}
	}
</script>

<div class="relative">
	<input
		{id}
		role="combobox"
		aria-autocomplete="list"
		aria-expanded={open}
		aria-controls={`${id}-listbox`}
		aria-activedescendant={open && filteredOptions[highlightedIndex] ? `${id}-option-${highlightedIndex}` : undefined}
		value={open ? inputValue : selectedLabel}
		placeholder={selectedLabel || placeholder || searchPlaceholder}
		disabled={disabled}
		autocomplete="off"
		onfocus={openList}
		onclick={openList}
		oninput={handleInput}
		onkeydown={handleKeydown}
		onblur={() => {
			setTimeout(() => {
				open = false;
			}, 120);
		}}
	/>

	{#if open && !disabled}
		<div
			id={`${id}-listbox`}
			role="listbox"
			class="absolute z-30 mt-2 max-h-64 w-full overflow-auto rounded-2xl border bg-[var(--app-surface)] p-1 shadow-xl"
			style="border-color: var(--app-border)"
		>
			{#each filteredOptions as option, index}
				<button
					id={`${id}-option-${index}`}
					role="option"
					aria-selected={option.value === value}
					class={`w-full rounded-xl px-3 py-2 text-left text-sm transition-colors ${
						index === highlightedIndex ? 'bg-black/[0.04]' : ''
					}`}
					type="button"
					onmousedown={(event) => event.preventDefault()}
					onmouseenter={() => highlightedIndex = index}
					onclick={() => selectOption(option)}
				>
					{option.label}
				</button>
			{:else}
				<p class="text-muted px-3 py-2 text-sm">No matches.</p>
			{/each}
		</div>
	{/if}
</div>
