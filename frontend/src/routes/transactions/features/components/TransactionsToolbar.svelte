<script lang="ts">
	let {
		search = $bindable(''),
		dateFrom = $bindable(''),
		dateTo = $bindable(''),
		filterCount,
		showSearch = $bindable(),
		showDate = $bindable(),
		showFilters = $bindable(),
		onAdd
	} = $props<{
		search: string;
		dateFrom: string;
		dateTo: string;
		filterCount: number;
		showSearch: boolean;
		showDate: boolean;
		showFilters: boolean;
		onAdd: () => void;
	}>();

	function toggleSearch() {
		showSearch = !showSearch;
		showDate = false;
		showFilters = false;
	}

	function toggleDate() {
		showDate = !showDate;
		showSearch = false;
		showFilters = false;
	}

	function toggleFilters() {
		showFilters = !showFilters;
		showSearch = false;
		showDate = false;
	}

	function clearDate() {
		dateFrom = '';
		dateTo = '';
	}
</script>

<div class="flex flex-wrap items-center justify-end gap-2">
	<div class="flex flex-wrap items-center gap-2">
		<button class="top-action" type="button" onclick={toggleSearch}>
			<span>⌕</span>
			Search
		</button>
		<button class="top-action" type="button" onclick={toggleDate}>
			<span>▣</span>
			Date
		</button>
		<button class="top-action" type="button" onclick={toggleFilters}>
			<span>☰</span>
			Filters
			{#if filterCount > 0}
				<span class="transaction-filter-count ml-1 text-(--app-orange-dark)">({filterCount})</span>
			{/if}
		</button>
	</div>

	<div class="h-8 w-px bg-(--app-border)"></div>
	<button class="primary-action" type="button" onclick={onAdd}>+ Add transaction</button>
</div>

{#if showSearch}
	<div class="absolute right-0 top-full z-30 mt-3 w-full max-w-md rounded-2xl border bg-(--app-surface) p-3 shadow-xl" style="border-color: var(--app-border)">
		<input class="w-full" bind:value={search} placeholder="Search payee, note, account, category" />
	</div>
{/if}

{#if showDate}
	<div class="absolute right-0 top-full z-30 mt-3 grid w-full max-w-xl gap-3 rounded-2xl border bg-(--app-surface) p-3 shadow-xl sm:grid-cols-2" style="border-color: var(--app-border)">
		<label class="grid gap-2">
			<span class="text-xs font-semibold uppercase tracking-widest text-muted">From</span>
			<input bind:value={dateFrom} type="date" />
		</label>

		<label class="grid gap-2">
			<span class="text-xs font-semibold uppercase tracking-widest text-muted">To</span>
			<input bind:value={dateTo} type="date" />
		</label>

		<div class="flex justify-end gap-2 sm:col-span-2">
			<button class="secondary-action" type="button" onclick={clearDate}>Clear date</button>
			<button class="primary-action" type="button" onclick={() => showDate = false}>Apply</button>
		</div>
	</div>
{/if}
