<script lang="ts">
	let { children } = $props();
</script>

<div class="min-h-screen bg-slate-950 text-slate-100">
	<div class="flex min-h-screen">
		<aside class="w-64 border-r border-slate-800 bg-slate-950 px-4 py-5">
			<div class="mb-8">
				<p class="text-lg font-bold">Centavo</p>
				<p class="text-xs text-slate-500">Offline finance</p>
			</div>

			<nav class="space-y-1 text-sm">
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/">
					Dashboard
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/accounts">
					Accounts
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/transactions">
					Transactions
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/categories">
					Categories
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/budgets">
					Budgets
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/goals">
					Goals
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/recurring">
					Recurring
				</a>
				<a class="block rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-900 hover:text-white" href="/settings">
					Settings
				</a>
			</nav>
		</aside>

		<main class="flex-1 overflow-auto">
			{@render children()}
		</main>
	</div>
</div>