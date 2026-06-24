<script lang="ts">
	import type { Account } from '$lib/api/accounts';
	import type { Category, CategoryGroup, CategoryGroupType } from '$lib/api/categories';

	let {
		selectedAccountIds = $bindable(),
		selectedTypes = $bindable(),
		selectedCategoryGroupIds = $bindable(),
		selectedCategoryIds = $bindable(),
		amountMin = $bindable(),
		amountMax = $bindable(),
		accounts,
		categoryGroups,
		categories,
		filterCount,
		onClear,
		onClose
	} = $props<{
		selectedAccountIds: number[];
		selectedTypes: CategoryGroupType[];
		selectedCategoryGroupIds: number[];
		selectedCategoryIds: number[];
		amountMin: string;
		amountMax: string;
		accounts: Account[];
		categoryGroups: CategoryGroup[];
		categories: Category[];
		filterCount: number;
		onClear: () => void;
		onClose: () => void;
	}>();

	type FilterSection = 'categories' | 'accounts' | 'amount';

	let activeSection: FilterSection = $state('categories');
	let categorySearch = $state('');
	let accountSearch = $state('');
	let openTypes: CategoryGroupType[] = $state(['expense']);

	const typeOptions: { value: CategoryGroupType; label: string }[] = [
		{ value: 'expense', label: 'Expense' },
		{ value: 'income', label: 'Income' },
		{ value: 'transfer', label: 'Transfer' }
	];

	let visibleCategoryGroups = $derived(
		categoryGroups.filter((group: CategoryGroup) => {
			const query = categorySearch.trim().toLowerCase();
			if (!query) return true;

			return (
				group.name.toLowerCase().includes(query)
				|| categories.some(
					(category: Category) =>
						category.group_id === group.group_id
						&& category.name.toLowerCase().includes(query)
				)
			);
		})
	);
	let visibleAccounts = $derived(
		accounts.filter((account: Account) =>
			account.name.toLowerCase().includes(accountSearch.trim().toLowerCase())
		)
	);
	let selectedLabels = $derived([
		...selectedTypes.map((type: CategoryGroupType) => type[0].toUpperCase() + type.slice(1)),
		...selectedCategoryGroupIds.map((groupId: number) =>
			categoryGroups.find((group: CategoryGroup) => group.group_id === groupId)?.name ?? `Group ${groupId}`
		),
		...selectedCategoryIds.map((categoryId: number) =>
			categories.find((category: Category) => category.category_id === categoryId)?.name ?? `Category ${categoryId}`
		),
		...selectedAccountIds.map((accountId: number) =>
			accounts.find((account: Account) => account.account_id === accountId)?.name ?? `Account ${accountId}`
		),
		...(amountMin ? [`Min ${amountMin}`] : []),
		...(amountMax ? [`Max ${amountMax}`] : [])
	]);

	function toggleValue(list: number[], value: number) {
		return list.includes(value)
			? list.filter((item) => item !== value)
			: [...list, value];
	}

	function toggleType(type: CategoryGroupType) {
		const typeGroups = categoryGroups.filter((group: CategoryGroup) => group.type === type);
		const typeGroupIds = typeGroups.map((group: CategoryGroup) => group.group_id);
		const typeCategoryIds = categories
			.filter((category: Category) => typeGroupIds.includes(category.group_id))
			.map((category: Category) => category.category_id);

		if (selectedTypes.includes(type)) {
			selectedTypes = selectedTypes.filter((item: CategoryGroupType) => item !== type);
			selectedCategoryGroupIds = selectedCategoryGroupIds.filter((groupId: number) => !typeGroupIds.includes(groupId));
			selectedCategoryIds = selectedCategoryIds.filter((categoryId: number) => !typeCategoryIds.includes(categoryId));
			return;
		}

		selectedTypes = [...new Set([...selectedTypes, type])];
		selectedCategoryGroupIds = [...new Set([...selectedCategoryGroupIds, ...typeGroupIds])];
		selectedCategoryIds = [...new Set([...selectedCategoryIds, ...typeCategoryIds])];
		openTypes = [...new Set([...openTypes, type])];
	}

	function toggleTypeOpen(type: CategoryGroupType) {
		openTypes = openTypes.includes(type)
			? openTypes.filter((item: CategoryGroupType) => item !== type)
			: [...openTypes, type];
	}

	function groupsForType(type: CategoryGroupType) {
		return visibleCategoryGroups.filter((group: CategoryGroup) => group.type === type);
	}

	function categoriesForGroup(groupId: number) {
		const query = categorySearch.trim().toLowerCase();
		const group = categoryGroups.find((row: CategoryGroup) => row.group_id === groupId);

		return categories.filter((category: Category) => {
			if (category.group_id !== groupId) return false;
			if (!query || group?.name.toLowerCase().includes(query)) return true;

			return category.name.toLowerCase().includes(query);
		});
	}

	function categoryIdsForGroup(groupId: number) {
		return categories
			.filter((category: Category) => category.group_id === groupId)
			.map((category: Category) => category.category_id);
	}

	function isGroupChecked(groupId: number) {
		const childCategoryIds = categoryIdsForGroup(groupId);

		return (
			selectedCategoryGroupIds.includes(groupId)
			|| (
				childCategoryIds.length > 0
				&& childCategoryIds.every((categoryId: number) => selectedCategoryIds.includes(categoryId))
			)
		);
	}

	function toggleCategoryGroup(groupId: number) {
		const childCategoryIds = categoryIdsForGroup(groupId);

		if (isGroupChecked(groupId)) {
			selectedCategoryGroupIds = selectedCategoryGroupIds.filter((id: number) => id !== groupId);
			selectedCategoryIds = selectedCategoryIds.filter((id: number) => !childCategoryIds.includes(id));
			return;
		}

		selectedCategoryGroupIds = [...new Set([...selectedCategoryGroupIds, groupId])];
		selectedCategoryIds = [...new Set([...selectedCategoryIds, ...childCategoryIds])];
	}

	function toggleCategory(categoryId: number) {
		selectedCategoryIds = toggleValue(selectedCategoryIds, categoryId);
	}

	function toggleAccount(accountId: number) {
		selectedAccountIds = toggleValue(selectedAccountIds, accountId);
	}
</script>

<div class="absolute right-0 top-full z-40 mt-3 w-full max-w-3xl rounded-2xl border bg-(--app-surface) shadow-2xl" style="border-color: var(--app-border)">
	<div class="transaction-filter-grid grid gap-0">
		<div class="border-b p-3 md:border-b-0 md:border-r" style="border-color: var(--app-border)">
			<p class="dashboard-eyebrow px-2 text-xs font-semibold uppercase tracking-widest">Filters</p>
			<div class="mt-3 grid gap-1 text-sm">
				<button
					class={`rounded-xl px-3 py-2 text-left font-semibold ${activeSection === 'categories' ? 'bg-(--app-orange-soft) text-(--app-orange-dark)' : 'text-muted'}`}
					type="button"
					onclick={() => activeSection = 'categories'}
				>
					Categories
				</button>
				<button
					class={`rounded-xl px-3 py-2 text-left font-semibold ${activeSection === 'accounts' ? 'bg-(--app-orange-soft) text-(--app-orange-dark)' : 'text-muted'}`}
					type="button"
					onclick={() => activeSection = 'accounts'}
				>
					Accounts
				</button>
				<button
					class={`rounded-xl px-3 py-2 text-left font-semibold ${activeSection === 'amount' ? 'bg-(--app-orange-soft) text-(--app-orange-dark)' : 'text-muted'}`}
					type="button"
					onclick={() => activeSection = 'amount'}
				>
					Amount
				</button>
			</div>
		</div>

		<div class="max-h-96 overflow-y-auto p-4">
			{#if activeSection === 'categories'}
				<input class="w-full" bind:value={categorySearch} placeholder="Search categories..." />

				<div class="mt-4 grid gap-2">
					{#each typeOptions as option}
						<div>
							<div class="flex items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-black/3">
								<input
									checked={selectedTypes.includes(option.value)}
									type="checkbox"
									onchange={() => toggleType(option.value)}
								/>
								<button
									class="flex flex-1 items-center justify-between text-left text-sm font-semibold"
									type="button"
									onclick={() => toggleTypeOpen(option.value)}
								>
									<span>{option.label}</span>
									<span class="text-muted">{openTypes.includes(option.value) ? '⌄' : '›'}</span>
								</button>
							</div>

							{#if openTypes.includes(option.value)}
								<div class="ml-4 mt-2 grid gap-2">
									{#each groupsForType(option.value) as group}
										<div>
											<label class="flex cursor-pointer items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-black/3">
												<input
													checked={isGroupChecked(group.group_id)}
													type="checkbox"
													onchange={() => toggleCategoryGroup(group.group_id)}
												/>
												<span class="text-sm font-semibold">{group.name}</span>
											</label>

											<div class="ml-6 grid gap-1">
												{#each categoriesForGroup(group.group_id) as category}
													<label class="flex cursor-pointer items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-black/3">
														<input
															checked={selectedCategoryIds.includes(category.category_id)}
															type="checkbox"
															onchange={() => toggleCategory(category.category_id)}
														/>
														<span class="text-sm">{category.name}</span>
													</label>
												{/each}
											</div>
										</div>
									{:else}
										<p class="text-muted px-2 py-1 text-xs">No matching {option.label.toLowerCase()} categories.</p>
									{/each}
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{:else if activeSection === 'accounts'}
				<input class="w-full" bind:value={accountSearch} placeholder="Search accounts..." />

				<div class="mt-4 grid gap-1">
					{#each visibleAccounts as account}
						<label class="flex cursor-pointer items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-black/3">
							<input
								checked={selectedAccountIds.includes(account.account_id)}
								type="checkbox"
								onchange={() => toggleAccount(account.account_id)}
							/>
							<span class="text-sm">{account.name}</span>
						</label>
					{/each}
				</div>
			{:else}
				<div class="grid gap-4">
					<label class="grid gap-2">
						<span class="text-xs font-semibold uppercase tracking-widest text-muted">Minimum amount</span>
						<input bind:value={amountMin} inputmode="decimal" placeholder="0.00" />
					</label>

					<label class="grid gap-2">
						<span class="text-xs font-semibold uppercase tracking-widest text-muted">Maximum amount</span>
						<input bind:value={amountMax} inputmode="decimal" placeholder="0.00" />
					</label>

					<p class="text-muted text-xs">
						Amount filters use the absolute value, so income and expenses can both match.
					</p>
				</div>
			{/if}
		</div>

		<div class="border-t p-4 md:border-l md:border-t-0" style="border-color: var(--app-border)">
			<p class="text-sm font-semibold">{filterCount} filters selected</p>
			<p class="text-muted mt-1 text-xs">Filters apply instantly.</p>

			<div class="mt-4 grid max-h-64 gap-2 overflow-y-auto pr-1">
				{#each selectedLabels as label}
					<span class="rounded-full bg-(--app-orange-soft) px-3 py-1 text-xs font-semibold text-(--app-orange-dark)">
						{label}
					</span>
				{:else}
					<p class="text-muted text-xs">No filters selected.</p>
				{/each}
			</div>

			<div class="mt-5 flex flex-wrap gap-2 md:grid">
				<button class="secondary-action" type="button" onclick={onClear}>Clear</button>
				<button class="primary-action" type="button" onclick={onClose}>Apply</button>
			</div>
		</div>
	</div>
</div>
