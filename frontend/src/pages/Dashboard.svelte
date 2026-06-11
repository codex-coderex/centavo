<script>
  import { onMount } from 'svelte'

  let budget = null
  let enrichedItems = []
  let recentTxns = []
  let categoryMap = {}
  let loading = true

  onMount(async () => {
    try {
      const py = window.py

      if (!py) {
        budget = { budget_id: 1, name: 'June 2026', period: 'monthly', start_date: '2026-06-01', end_date: '2026-06-30' }
        categoryMap = {
          1: { name: 'Groceries', group: 'Food', color: '#4f46e5' },
          2: { name: 'Dining Out', group: 'Food', color: '#4f46e5' },
          3: { name: 'Rent', group: 'Housing', color: '#10b981' },
          4: { name: 'Electricity', group: 'Housing', color: '#10b981' },
          5: { name: 'Fare', group: 'Transport', color: '#f59e0b' },
          6: { name: 'Salary', group: 'Income', color: '#10b981' },
        }
        enrichedItems = [
          { name: 'Groceries', group: 'Food', planned_amount: 5000, actual_amount: 4300, color: '#4f46e5' },
          { name: 'Dining Out', group: 'Food', planned_amount: 2000, actual_amount: 1800, color: '#4f46e5' },
          { name: 'Rent', group: 'Housing', planned_amount: 10000, actual_amount: 10000, color: '#10b981' },
          { name: 'Electricity', group: 'Housing', planned_amount: 1500, actual_amount: 800, color: '#10b981' },
          { name: 'Fare', group: 'Transport', planned_amount: 1000, actual_amount: 950, color: '#f59e0b' },
          { name: 'Salary', group: 'Income', planned_amount: 30000, actual_amount: 30000, color: '#10b981' },
        ]
        recentTxns = [
          { transaction_id: 1, merchant: 'SM Supermarket', amount: -1200, txn_date: '2026-06-09', category_id: 1 },
          { transaction_id: 2, merchant: 'Jollibee', amount: -350, txn_date: '2026-06-08', category_id: 2 },
          { transaction_id: 3, merchant: 'Meralco', amount: -800, txn_date: '2026-06-07', category_id: 4 },
          { transaction_id: 4, merchant: 'Salary', amount: 30000, txn_date: '2026-06-05', category_id: 6 },
          { transaction_id: 5, merchant: 'Grab', amount: -150, txn_date: '2026-06-05', category_id: 5 },
        ]
        loading = false
        return
      }

      const [budgets, categories, groups, txns] = await Promise.all([
        py.get_budgets(1),
        py.get_all_categories(1),
        py.get_category_groups(1),
        py.get_transactions_by_user(1),
      ])

      if (budgets.length === 0) { loading = false; return }
      budget = budgets[0]

      const groupNameMap = {}
      for (const g of groups) groupNameMap[g.group_id] = g.name

      for (const c of categories) {
        categoryMap[c.category_id] = {
          name: c.name,
          group: groupNameMap[c.group_id] ?? 'Other',
          color: c.color ?? '#4f46e5',
        }
      }

      const items = await py.get_budget_items(budget.budget_id)
      enrichedItems = items.map(item => {
        const cat = categoryMap[item.category_id] ?? { name: 'Unknown', group: 'Other', color: '#6b7280' }
        const actual = txns
          .filter(t => t.category_id === item.category_id && t.transfer_pair_id == null)
          .reduce((sum, t) => sum + t.amount, 0)
        return { ...item, name: cat.name, group: cat.group, color: cat.color, actual_amount: actual }
      })

      recentTxns = txns.slice(0, 5)

    } catch (e) {
      console.error(e)
    } finally {
      loading = false
    }
  })

  $: totalIncome = enrichedItems.filter(i => i.group === 'Income').reduce((s, i) => s + (i.actual_amount ?? 0), 0)
  $: totalSpent = enrichedItems.filter(i => i.group !== 'Income').reduce((s, i) => s + Math.abs(i.actual_amount ?? 0), 0)
  $: remaining = totalIncome - totalSpent
  $: overBudget = enrichedItems.filter(i => i.actual_amount > i.planned_amount).length

  $: groups = enrichedItems.reduce((acc, item) => {
    if (!acc[item.group]) acc[item.group] = []
    acc[item.group].push(item)
    return acc
  }, {})

  const chartColors = ['#4f46e5','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316']

  $: spendingGroups = Object.entries(groups)
    .filter(([name]) => name !== 'Income')
    .map(([name, items], i) => ({
      name,
      total: items.reduce((s, i) => s + Math.abs(i.actual_amount ?? 0), 0),
      color: chartColors[i % chartColors.length],
    }))
    .filter(g => g.total > 0)

  $: chartTotal = spendingGroups.reduce((s, g) => s + g.total, 0)

  $: donutSegments = (() => {
    const r = 70
    const circ = 2 * Math.PI * r
    let offset = 0
    return spendingGroups.map(g => {
      const frac = chartTotal ? g.total / chartTotal : 0
      const dash = frac * circ
      const seg = { ...g, dash, offset }
      offset += dash
      return seg
    })
  })()

  function pct(item) {
    if (!item.planned_amount) return 0
    return Math.min((item.actual_amount / item.planned_amount) * 100, 100)
  }

  function fmt(n) {
    return '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }

  function fmtSigned(n) {
    return (n >= 0 ? '+' : '−') + '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }
</script>

{#if loading}
  <div class="loading-state">
    <div class="spinner"></div>
    <span>Loading your budget…</span>
  </div>
{:else if !budget}
  <div class="empty-state">
    <p class="empty-title">No active budget</p>
    <p class="empty-sub">Create a budget to start tracking your spending.</p>
    <a href="#/budgets" class="btn-primary">Create Budget</a>
  </div>
{:else}
  <div class="page">

    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-sub">{budget.name} budget &nbsp;·&nbsp; {budget.start_date} to {budget.end_date ?? 'ongoing'}</p>
      </div>
    </div>

    <div class="top-row">
      <div class="card balance-card">
        <span class="balance-label">Remaining Balance</span>
        <span class="balance-amount" class:negative={remaining < 0}>{fmt(remaining)}</span>
        <div class="balance-meta">
          <span class="meta-income">↑ {fmt(totalIncome)} income</span>
          <span class="meta-spent">↓ {fmt(totalSpent)} spent</span>
        </div>
      </div>

      <div class="card stat-card">
        <span class="stat-label">Income</span>
        <span class="stat-val income">{fmt(totalIncome)}</span>
      </div>
      <div class="card stat-card">
        <span class="stat-label">Expenses</span>
        <span class="stat-val expenses">{fmt(totalSpent)}</span>
      </div>
      <div class="card stat-card">
        <span class="stat-label">Over Budget</span>
        <span class="stat-val" class:warn={overBudget > 0}>{overBudget}</span>
        <span class="stat-sub">{overBudget === 1 ? 'category' : 'categories'}</span>
      </div>
    </div>

    <div class="mid-row">
      <div class="card donut-card">
        <div class="section-header">
          <span class="section-title"><span class="title-badge">◐</span> Spending Breakdown</span>
          <a href="#/budgets" class="link-sm">View Budget →</a>
        </div>
        {#if chartTotal === 0}
          <p class="muted-center">No spending recorded yet.</p>
        {:else}
          <div class="donut-layout">
            <div class="donut-fig">
              <svg viewBox="0 0 160 160" width="170" height="170">
                {#each donutSegments as seg}
                  <circle
                    cx="80" cy="80" r="70"
                    fill="none"
                    stroke={seg.color}
                    stroke-width="18"
                    stroke-dasharray="{seg.dash} {2 * Math.PI * 70 - seg.dash}"
                    stroke-dashoffset={-(seg.offset - 2 * Math.PI * 70 * 0.25)}
                  />
                {/each}
                <text x="80" y="74" text-anchor="middle" class="donut-center-label">Total Spent</text>
                <text x="80" y="94" text-anchor="middle" class="donut-center-amount">₱{Math.round(totalSpent / 1000)}k</text>
              </svg>
            </div>
            <div class="donut-legend">
              {#each donutSegments as seg}
                <div class="legend-item">
                  <span class="legend-dot" style="background:{seg.color}"></span>
                  <div class="legend-text">
                    <span class="legend-name" style="color:{seg.color}">{seg.name}</span>
                    <span class="legend-amt">{fmt(seg.total)}</span>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <div class="card txn-card">
        <div class="section-header">
          <span class="section-title"><span class="title-badge">↕</span> Recent Transactions</span>
          <a href="#/transactions" class="link-sm">See all →</a>
        </div>
        {#if recentTxns.length === 0}
          <p class="muted-center">No transactions yet.</p>
        {:else}
          <div class="txn-list">
            {#each recentTxns as txn}
              {@const cat = categoryMap[txn.category_id]}
              <div class="txn-row">
                <div class="txn-info">
                  <span class="txn-merchant">{txn.merchant ?? 'Unknown'}</span>
                  <span class="txn-meta">{cat?.name ?? '—'} &nbsp;·&nbsp; {txn.txn_date}</span>
                </div>
                <span class="txn-amt" class:pos={txn.amount > 0} class:neg={txn.amount < 0}>
                  {fmtSigned(txn.amount)}
                </span>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <div class="section-header" style="margin-bottom: 12px;">
      <span class="section-title"><span class="title-badge">◫</span> Budget Categories</span>
    </div>
    <div class="groups-grid">
      {#each Object.entries(groups) as [groupName, items]}
        <div class="card group-card">
          <p class="group-name">{groupName}</p>
          {#each items as item}
            {@const p = pct(item)}
            <div class="bitem">
              <div class="bitem-top">
                <span class="bitem-name">{item.name}</span>
                <span class="bitem-right">
                  <span class:over-text={item.actual_amount > item.planned_amount}>{fmt(item.actual_amount)}</span>
                  <span class="bitem-sep">/</span>
                  <span class="bitem-planned">{fmt(item.planned_amount)}</span>
                </span>
              </div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  class:bar-warn={p >= 85 && p < 100}
                  class:bar-over={item.actual_amount > item.planned_amount}
                  style="width:{p}%"
                ></div>
              </div>
            </div>
          {/each}
        </div>
      {/each}
    </div>

  </div>
{/if}

<style>
  .page { display: flex; flex-direction: column; gap: 28px; }

  .loading-state {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 60vh; gap: 12px; color: #9ca3af;
    font-size: 14px;
  }

  .spinner {
    width: 28px; height: 28px;
    border: 3px solid #e5e7eb;
    border-top-color: #4f46e5;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .empty-state {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 60vh; gap: 8px; text-align: center;
  }

  .empty-title { font-size: 18px; font-weight: 600; color: #1a1a2e; }
  .empty-sub { font-size: 14px; color: #9ca3af; margin-bottom: 8px; }

  .btn-primary {
    background: #4f46e5; color: #fff; padding: 10px 20px;
    border-radius: 8px; font-size: 14px; font-weight: 500;
    text-decoration: none; transition: background 0.2s;
  }

  .btn-primary:hover { background: #4338ca; }

  .page-header { display: flex; justify-content: space-between; align-items: flex-start; }
  .page-title { font-size: 26px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; }
  .page-sub { font-size: 13px; color: #9ca3af; margin-top: 4px; }

  .top-row { display: grid; grid-template-columns: 1.6fr 1fr 1fr 1fr; gap: 16px; }

  .card {
    background: #fff;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 8px rgba(0,0,0,0.04);
  }

  .balance-card {
    display: flex; flex-direction: column; gap: 6px;
    background: linear-gradient(135deg, #eef2ff 0%, #ffffff 60%);
    border: 1px solid #e0e7ff;
  }

  .balance-label { font-size: 12px; font-weight: 500; color: #6366f1; text-transform: uppercase; letter-spacing: 0.06em; }
  .balance-amount { font-size: 32px; font-weight: 700; color: #1a1a2e; letter-spacing: -1px; }
  .balance-amount.negative { color: #ef4444; }
  .balance-meta { display: flex; gap: 16px; margin-top: 4px; }
  .meta-income { font-size: 13px; color: #10b981; font-weight: 500; }
  .meta-spent { font-size: 13px; color: #ef4444; font-weight: 500; }

  .stat-card { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
  .stat-label { font-size: 12px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; }
  .stat-val { font-size: 22px; font-weight: 700; color: #1a1a2e; }
  .stat-val.income { color: #10b981; }
  .stat-val.expenses { color: #ef4444; }
  .stat-val.warn { color: #f59e0b; }
  .stat-sub { font-size: 12px; color: #9ca3af; }

  .mid-row { display: grid; grid-template-columns: 360px 1fr; gap: 16px; }

  .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
  .section-title { font-size: 14px; font-weight: 600; color: #1a1a2e; display: flex; align-items: center; gap: 8px; }
  .title-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 6px;
    background: #ede9fe; color: #4f46e5;
    font-size: 12px;
  }
  .link-sm { font-size: 13px; color: #4f46e5; text-decoration: none; font-weight: 500; }
  .link-sm:hover { text-decoration: underline; }

  .muted-center { color: #9ca3af; font-size: 14px; text-align: center; padding: 24px 0; }

  .donut-layout { display: flex; align-items: center; gap: 20px; }
  .donut-fig { flex-shrink: 0; }

  .donut-center-label {
    font-size: 10px; fill: #9ca3af;
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }

  .donut-center-amount {
    font-size: 16px; font-weight: 700; fill: #1a1a2e;
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }

  .donut-legend { display: flex; flex-direction: column; gap: 14px; flex: 1; min-width: 0; }
  .legend-item { display: flex; align-items: flex-start; gap: 10px; min-width: 0; }
  .legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
  .legend-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
  .legend-name { font-size: 13px; font-weight: 600; }
  .legend-amt { font-size: 14px; font-weight: 700; color: #1a1a2e; }

  .txn-list { display: flex; flex-direction: column; gap: 4px; }

  .txn-row {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 12px 8px; border-radius: 8px;
    border-bottom: 1px solid #f3f4f6;
    transition: background 0.15s;
  }

  .txn-row:last-child { border-bottom: none; }
  .txn-row:hover { background: #f9fafb; }

  .txn-info { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
  .txn-merchant { font-size: 14px; font-weight: 600; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .txn-meta { font-size: 12px; color: #9ca3af; }
  .txn-amt { font-size: 14px; font-weight: 700; flex-shrink: 0; }
  .txn-amt.pos { color: #10b981; }
  .txn-amt.neg { color: #ef4444; }

  .groups-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }

  .group-card { display: flex; flex-direction: column; gap: 14px; }
  .group-name { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; }

  .bitem { display: flex; flex-direction: column; gap: 6px; }
  .bitem-top { display: flex; justify-content: space-between; align-items: center; }
  .bitem-name { font-size: 14px; color: #374151; }
  .bitem-right { display: flex; gap: 4px; font-size: 13px; align-items: center; }
  .over-text { color: #ef4444; font-weight: 600; }
  .bitem-sep { color: #e5e7eb; }
  .bitem-planned { color: #9ca3af; }

  .bar-track { height: 5px; background: #f3f4f6; border-radius: 99px; overflow: hidden; }
  .bar-fill { height: 100%; background: #4f46e5; border-radius: 99px; transition: width 0.5s ease; }
  .bar-fill.bar-warn { background: #f59e0b; }
  .bar-fill.bar-over { background: #ef4444; }
</style>