<script lang="ts">
	import type { DashboardPeriod } from '../utils/dashboardFormat';
	import { formatMoney, periodRange, spendingForPeriod, spendingSeries } from '../utils/dashboardFormat';
	import type { Transaction } from '$lib/api/transactions';

	let {
		transactions,
		period = $bindable()
	} = $props<{
		transactions: Transaction[];
		period: DashboardPeriod;
	}>();

	let range = $derived(periodRange(period));
	let total = $derived(spendingForPeriod(transactions, period));
	let series = $derived(spendingSeries(transactions, period));
	let maxValue = $derived(Math.max(...series.map((point) => point.value), 1));
	let width = 760;
	let height = 230;
	let chartTop = 18;
	let chartHeight = 145;
	let chartLeft = 96;
	let chartWidth = 620;
	let barGap = $derived(period === 'month' ? 4 : 12);
	let barWidth = $derived(series.length ? Math.max((chartWidth - barGap * (series.length - 1)) / series.length, 4) : 0);
	let bars = $derived(
		series.map((point, index) => {
			const height = point.value > 0 ? Math.max((point.value / maxValue) * chartHeight, 2) : 0;
			const x = chartLeft + index * (barWidth + barGap);
			const y = chartTop + chartHeight - height;
			return { ...point, x, y, height };
		})
	);
	let labelEvery = $derived(period === 'month' ? Math.ceil(series.length / 6) : 1);
</script>

<div class="dashboard-card p-5">
	<div class="flex flex-wrap items-start justify-between gap-4">
		<div>
			<h2 class="text-lg font-semibold">Spending</h2>
			<p class="text-muted mt-1 text-sm">{formatMoney(total)} spent in {range.label}</p>
		</div>

		<div class="flex rounded-lg border p-1" style="border-color: var(--app-border)">
			<button
				class={period === 'month' ? 'primary-action' : 'secondary-action'}
				type="button"
				onclick={() => period = 'month'}
			>
				Month
			</button>
			<button
				class={period === 'year' ? 'primary-action' : 'secondary-action'}
				type="button"
				onclick={() => period = 'year'}
			>
				Year
			</button>
		</div>
	</div>

	<div class="mt-5 overflow-hidden rounded-xl border px-2 py-3" style="border-color: var(--app-border); background: var(--app-surface-strong)">
		<svg viewBox={`0 0 ${width} ${height}`} class="h-[230px] w-full">
			{#each [0, 0.25, 0.5, 0.75, 1] as tick}
				<line
					x1={chartLeft}
					x2={chartLeft + chartWidth}
					y1={chartTop + chartHeight - tick * chartHeight}
					y2={chartTop + chartHeight - tick * chartHeight}
					stroke="var(--app-border)"
					stroke-width="1"
				/>
				<text
					x={chartLeft - 12}
					y={chartTop + chartHeight - tick * chartHeight + 4}
					text-anchor="end"
					fill="var(--app-muted)"
					font-size="11"
				>
					{formatMoney(maxValue * tick)}
				</text>
			{/each}

			{#if total > 0}
				{#each bars as bar}
					<rect
						x={bar.x}
						y={bar.y}
						width={barWidth}
						height={bar.height}
						rx="5"
						fill={bar.value > 0 ? 'var(--app-orange)' : 'transparent'}
					/>
				{/each}
			{:else}
				<text x={width / 2} y={height / 2} text-anchor="middle" fill="var(--app-muted)" font-size="14">
					No spending recorded for this period
				</text>
			{/if}

			{#each bars as bar, index}
				{#if index % labelEvery === 0 || index === bars.length - 1}
					<text
						x={bar.x + barWidth / 2}
						y={height - 22}
						text-anchor="middle"
						fill="var(--app-muted)"
						font-size="11"
					>
						{bar.label}
					</text>
				{/if}
			{/each}
		</svg>
	</div>
</div>
