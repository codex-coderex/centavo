<script lang="ts">
	import accountsIcon from '$lib/assets/accounts.svg';
	import budgetsIcon from '$lib/assets/budgets.svg';
	import goalsIcon from '$lib/assets/goals.svg';
	import homeIcon from '$lib/assets/home.svg';
	import recurringIcon from '$lib/assets/recurring.svg';
	import settingsIcon from '$lib/assets/settings.svg';
	import transactionsIcon from '$lib/assets/transactions.svg';

	let { children } = $props();

	const navItems = [
		{ href: '/', label: 'Dashboard', icon: homeIcon },
		{ href: '/accounts', label: 'Accounts', icon: accountsIcon },
		{ href: '/transactions', label: 'Transactions', icon: transactionsIcon },
		{ href: '/budgets', label: 'Budgets', icon: budgetsIcon },
		{ href: '/goals', label: 'Goals', icon: goalsIcon },
		{ href: '/recurring', label: 'Recurring', icon: recurringIcon },
		{ href: '/settings', label: 'Settings', icon: settingsIcon },
	];
</script>

<div class="app-shell">
	<div class="flex min-h-screen">
		<aside class="app-sidebar px-4 py-5">
			<div class="mb-8 flex items-center gap-3">
				<div class="app-brand-mark">C</div>
				<div>
					<p class="text-lg font-bold leading-tight">Centavo</p>
					<p class="text-xs" style="color: var(--app-muted)">Offline finance</p>
				</div>
			</div>

			<nav class="space-y-1 text-sm">
				{#each navItems as item}
					<a class="app-nav-link" href={item.href}>
						<img class="app-nav-icon" src={item.icon} alt="" aria-hidden="true" />
						<span>{item.label}</span>
					</a>
				{/each}
			</nav>
		</aside>

		<main class="app-main">
			{@render children()}
		</main>
	</div>
</div>
