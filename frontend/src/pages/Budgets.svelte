<script>
  import { onMount } from 'svelte'

  let budgets = []
  let allCategories = []
  let allTxns = []
  let categoryMap = {}
  let loading = true

  let selectedBudgetId = null
  let budgetItems = []
  let itemsLoading = false

  // create/edit budget modal
  let showBudgetModal = false
  let editingBudget = null
  let budgetForm = { name: '', period: 'monthly', start_date: '', end_date: '' }
  let budgetFormError = ''
  let savingBudget = false

  // add/edit budget item modal
  let showItemModal = false
  let editingItem = null
  let itemForm = { category_id: '', planned_amount: '', rollover_enabled: false }
  let itemFormError = ''
  let savingItem = false

  onMount(async () => {
    await loadBudgets()
  })

  async function loadBudgets() {
    loading = true
    try {
      const py = window.py

      if (!py) {
        allCategories = [
          { category_id: 1, name: 'Groceries', group_id: 1, color: '#4f46e5' },
          { category_id: 2, name: 'Dining Out', group_id: 1, color: '#4f46e5' },
          { category_id: 3, name: 'Rent', group_id: 2, color: '#10b981' },
          { category_id: 4, name: 'Electricity', group_id: 2, color: '#10b981' },
          { category_id: 5, name: 'Fare', group_id: 3, color: '#f59e0b' },
          { category_id: 6, name: 'Salary', group_id: 4, color: '#10b981' },
        ]
        allTxns = [
          { transaction_id: 1, category_id: 1, amount: -4300, txn_date: '2026-06-09', transfer_pair_id: null },
          { transaction_id: 2, category_id: 2, amount: -1800, txn_date: '2026-06-08', transfer_pair_id: null },
          { transaction_id: 3, category_id: 4, amount: -800, txn_date: '2026-06-07', transfer_pair_id: null },
          { transaction_id: 4, category_id: 6, amount: 30000, txn_date: '2026-06-05', transfer_pair_id: null },
          { transaction_id: 5, category_id: 3, amount: -10000, txn_date: '2026-06-01', transfer_pair_id: null },
          { transaction_id: 6, category_id: 5, amount: -950, txn_date: '2026-06-05', transfer_pair_id: null },
        ]
        budgets = [
          { budget_id: 1, name: 'June 2026', period: 'monthly', start_date: '2026-06-01', end_date: '2026-06-30' },
          { budget_id: 2, name: 'May 2026', period: 'monthly', start_date: '2026-05-01', end_date: '2026-05-31' },
        ]
        buildCategoryMap()
        loading = false
        return
      }

      const [b, categories, groups, txns] = await Promise.all([
        py.get_budgets(1),
        py.get_all_categories(1),
        py.get_category_groups(1),
        py.get_transactions_by_user(1),
      ])

      budgets = b
      allTxns = txns

      const groupNameMap = {}
      for (const g of groups) groupNameMap[g.group_id] = g.name
      allCategories = categories.map(c => ({ ...c, groupName: groupNameMap[c.group_id] ?? 'Other' }))

      buildCategoryMap()

    } catch (e) {
      console.error(e)
    } finally {
      loading = false
    }
  }

  function buildCategoryMap() {
    categoryMap = {}
    for (const c of allCategories) categoryMap[c.category_id] = c
  }

  async function openBudget(budget) {
    selectedBudgetId = budget.budget_id
    await loadItems(budget)
  }

  async function loadItems(budget) {
    itemsLoading = true
    try {
      const py = window.py

      if (!py) {
        const mockItems = {
          1: [
            { budget_item_id: 1, budget_id: 1, category_id: 1, planned_amount: 5000, rollover_enabled: false },
            { budget_item_id: 2, budget_id: 1, category_id: 2, planned_amount: 2000, rollover_enabled: false },
            { budget_item_id: 3, budget_id: 1, category_id: 3, planned_amount: 10000, rollover_enabled: false },
            { budget_item_id: 4, budget_id: 1, category_id: 4, planned_amount: 1500, rollover_enabled: true },
            { budget_item_id: 5, budget_id: 1, category_id: 5, planned_amount: 1000, rollover_enabled: false },
          ],
          2: [
            { budget_item_id: 6, budget_id: 2, category_id: 1, planned_amount: 4500, rollover_enabled: false },
          ],
        }
        budgetItems = mockItems[budget.budget_id] ?? []
        itemsLoading = false
        return
      }

      budgetItems = await py.get_budget_items(budget.budget_id)

    } catch (e) {
      console.error(e)
    } finally {
      itemsLoading = false
    }
  }

  function backToList() {
    selectedBudgetId = null
    budgetItems = []
  }

  $: selectedBudget = budgets.find(b => b.budget_id === selectedBudgetId)

  function actualForCategory(categoryId, budget) {
    return allTxns
      .filter(t =>
        t.category_id === categoryId &&
        t.transfer_pair_id == null &&
        t.txn_date >= budget.start_date &&
        (!budget.end_date || t.txn_date <= budget.end_date)
      )
      .reduce((sum, t) => sum + Math.abs(t.amount), 0)
  }

  function budgetTotals(budget) {
    const items = budget.budget_id === selectedBudgetId
      ? budgetItems
      : (budgetItemsCache[budget.budget_id] ?? [])
    const planned = items.reduce((s, i) => s + i.planned_amount, 0)
    const actual = items.reduce((s, i) => s + actualForCategory(i.category_id, budget), 0)
    return { planned, actual }
  }

  // simple cache so list cards can show totals without re-fetching constantly
  let budgetItemsCache = {}

  async function preloadAllItems() {
    const py = window.py
    if (!py) {
      const mockItems = {
        1: [
          { budget_item_id: 1, budget_id: 1, category_id: 1, planned_amount: 5000, rollover_enabled: false },
          { budget_item_id: 2, budget_id: 1, category_id: 2, planned_amount: 2000, rollover_enabled: false },
          { budget_item_id: 3, budget_id: 1, category_id: 3, planned_amount: 10000, rollover_enabled: false },
          { budget_item_id: 4, budget_id: 1, category_id: 4, planned_amount: 1500, rollover_enabled: true },
          { budget_item_id: 5, budget_id: 1, category_id: 5, planned_amount: 1000, rollover_enabled: false },
        ],
        2: [
          { budget_item_id: 6, budget_id: 2, category_id: 1, planned_amount: 4500, rollover_enabled: false },
        ],
      }
      budgetItemsCache = mockItems
      return
    }
    const results = await Promise.all(budgets.map(b => py.get_budget_items(b.budget_id)))
    budgetItemsCache = {}
    budgets.forEach((b, i) => { budgetItemsCache[b.budget_id] = results[i] })
  }

  $: if (budgets.length > 0 && Object.keys(budgetItemsCache).length === 0) {
    preloadAllItems()
  }

  function fmt(n) {
    return '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }

  function pct(actual, planned) {
    if (!planned) return 0
    return Math.min((actual / planned) * 100, 100)
  }

  // budget create/edit
  function openCreateBudget() {
    editingBudget = null
    budgetForm = { name: '', period: 'monthly', start_date: '', end_date: '' }
    budgetFormError = ''
    showBudgetModal = true
  }

  function openEditBudget(budget) {
    editingBudget = budget
    budgetForm = { name: budget.name, period: budget.period, start_date: budget.start_date, end_date: budget.end_date ?? '' }
    budgetFormError = ''
    showBudgetModal = true
  }

  function closeBudgetModal() {
    showBudgetModal = false
    editingBudget = null
  }

  async function submitBudget() {
    budgetFormError = ''
    if (!budgetForm.name.trim()) { budgetFormError = 'Please enter a budget name.'; return }
    if (!budgetForm.start_date) { budgetFormError = 'Please select a start date.'; return }

    savingBudget = true
    try {
      const py = window.py

      if (!py) {
        if (editingBudget) {
          budgets = budgets.map(b => b.budget_id === editingBudget.budget_id
            ? { ...b, ...budgetForm, end_date: budgetForm.end_date || null }
            : b)
        } else {
          const newId = Math.max(0, ...budgets.map(b => b.budget_id)) + 1
          budgets = [{ budget_id: newId, ...budgetForm, end_date: budgetForm.end_date || null }, ...budgets]
          budgetItemsCache[newId] = []
        }
        showBudgetModal = false
        savingBudget = false
        return
      }

      if (editingBudget) {
        await py.update_budget(editingBudget.budget_id, budgetForm.name, budgetForm.period, budgetForm.start_date, budgetForm.end_date || null)
      } else {
        await py.create_budget(1, budgetForm.name, budgetForm.period, budgetForm.start_date, budgetForm.end_date || null)
      }

      await loadBudgets()
      await preloadAllItems()
      showBudgetModal = false

    } catch (e) {
      console.error(e)
      budgetFormError = 'Something went wrong saving this budget.'
    } finally {
      savingBudget = false
    }
  }

  async function deleteBudget(budget) {
    if (!confirm(`Delete "${budget.name}"? This cannot be undone.`)) return
    try {
      const py = window.py
      if (py) await py.delete_budget(budget.budget_id)
      budgets = budgets.filter(b => b.budget_id !== budget.budget_id)
      if (selectedBudgetId === budget.budget_id) backToList()
    } catch (e) {
      console.error(e)
    }
  }

  // budget item create/edit
  function openCreateItem() {
    editingItem = null
    itemForm = { category_id: '', planned_amount: '', rollover_enabled: false }
    itemFormError = ''
    showItemModal = true
  }

  function openEditItem(item) {
    editingItem = item
    itemForm = { category_id: item.category_id, planned_amount: item.planned_amount, rollover_enabled: item.rollover_enabled }
    itemFormError = ''
    showItemModal = true
  }

  function closeItemModal() {
    showItemModal = false
    editingItem = null
  }

  async function submitItem() {
    itemFormError = ''
    if (!itemForm.category_id) { itemFormError = 'Please select a category.'; return }
    if (itemForm.planned_amount === '' || isNaN(Number(itemForm.planned_amount)) || Number(itemForm.planned_amount) <= 0) {
      itemFormError = 'Please enter a valid planned amount.'; return
    }

    savingItem = true
    try {
      const py = window.py

      if (!py) {
        if (editingItem) {
          budgetItems = budgetItems.map(i => i.budget_item_id === editingItem.budget_item_id
            ? { ...i, category_id: Number(itemForm.category_id), planned_amount: Number(itemForm.planned_amount), rollover_enabled: itemForm.rollover_enabled }
            : i)
        } else {
          const newId = Math.max(0, ...budgetItems.map(i => i.budget_item_id), 0) + 100
          budgetItems = [...budgetItems, {
            budget_item_id: newId,
            budget_id: selectedBudgetId,
            category_id: Number(itemForm.category_id),
            planned_amount: Number(itemForm.planned_amount),
            rollover_enabled: itemForm.rollover_enabled,
          }]
        }
        budgetItemsCache[selectedBudgetId] = budgetItems
        showItemModal = false
        savingItem = false
        return
      }

      if (editingItem) {
        await py.update_budget_item(editingItem.budget_item_id, Number(itemForm.planned_amount), itemForm.rollover_enabled)
      } else {
        await py.create_budget_item(selectedBudgetId, Number(itemForm.category_id), Number(itemForm.planned_amount), itemForm.rollover_enabled)
      }

      budgetItems = await py.get_budget_items(selectedBudgetId)
      budgetItemsCache[selectedBudgetId] = budgetItems
      showItemModal = false

    } catch (e) {
      console.error(e)
      itemFormError = 'Something went wrong saving this item.'
    } finally {
      savingItem = false
    }
  }

  async function deleteItem(item) {
    if (!confirm('Remove this budget item?')) return
    try {
      const py = window.py
      if (py) await py.delete_budget_item(item.budget_item_id)
      budgetItems = budgetItems.filter(i => i.budget_item_id !== item.budget_item_id)
      budgetItemsCache[selectedBudgetId] = budgetItems
    } catch (e) {
      console.error(e)
    }
  }
</script>

{#if loading}
  <div class="loading-state">
    <div class="spinner"></div>
    <span>Loading budgets…</span>
  </div>
{:else if !selectedBudget}
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Budgets</h1>
        <p class="page-sub">{budgets.length} budget{budgets.length === 1 ? '' : 's'}</p>
      </div>
      <button class="btn-primary" on:click={openCreateBudget}>+ New Budget</button>
    </div>

    {#if budgets.length === 0}
      <div class="card">
        <p class="muted-center">No budgets yet. Create one to start tracking.</p>
      </div>
    {:else}
      <div class="budget-grid">
        {#each budgets as budget}
          {@const totals = budgetTotals(budget)}
          {@const p = pct(totals.actual, totals.planned)}
          <div class="card budget-card" on:click={() => openBudget(budget)}>
            <div class="budget-card-top">
              <div>
                <p class="budget-name">{budget.name}</p>
                <p class="budget-dates">{budget.start_date} – {budget.end_date ?? 'ongoing'}</p>
              </div>
              <span class="period-pill">{budget.period}</span>
            </div>
            <div class="budget-totals">
              <span class="amt-actual">{fmt(totals.actual)}</span>
              <span class="amt-sep">/</span>
              <span class="amt-planned">{fmt(totals.planned)}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" class:bar-over={totals.actual > totals.planned} style="width:{p}%"></div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{:else}
  <div class="page">
    <div class="page-header">
      <div>
        <button class="back-link" on:click={backToList}>← All Budgets</button>
        <h1 class="page-title">{selectedBudget.name}</h1>
        <p class="page-sub">{selectedBudget.start_date} – {selectedBudget.end_date ?? 'ongoing'} &nbsp;·&nbsp; {selectedBudget.period}</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" on:click={() => openEditBudget(selectedBudget)}>Edit</button>
        <button class="btn-danger" on:click={() => deleteBudget(selectedBudget)}>Delete</button>
        <button class="btn-primary" on:click={openCreateItem}>+ Add Item</button>
      </div>
    </div>

    {#if itemsLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <span>Loading items…</span>
      </div>
    {:else if budgetItems.length === 0}
      <div class="card">
        <p class="muted-center">No budget items yet. Add a category to get started.</p>
      </div>
    {:else}
      <div class="card table-card">
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Rollover</th>
              <th class="amt-col">Spent / Planned</th>
              <th class="progress-col">Progress</th>
              <th class="actions-col"></th>
            </tr>
          </thead>
          <tbody>
            {#each budgetItems as item}
              {@const cat = categoryMap[item.category_id]}
              {@const actual = actualForCategory(item.category_id, selectedBudget)}
              {@const p = pct(actual, item.planned_amount)}
              <tr>
                <td>
                  {#if cat}
                    <span class="cat-pill" style="background:{cat.color}1a; color:{cat.color}">{cat.name}</span>
                  {:else}
                    <span class="cat-pill muted">Unknown</span>
                  {/if}
                </td>
                <td>
                  <span class="rollover-pill" class:on={item.rollover_enabled}>
                    {item.rollover_enabled ? 'Enabled' : 'Off'}
                  </span>
                </td>
                <td class="amt-col">
                  <span class:over-text={actual > item.planned_amount}>{fmt(actual)}</span>
                  <span class="amt-sep">/</span>
                  <span class="amt-planned">{fmt(item.planned_amount)}</span>
                </td>
                <td class="progress-col">
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      class:bar-warn={p >= 85 && p < 100}
                      class:bar-over={actual > item.planned_amount}
                      style="width:{p}%"
                    ></div>
                  </div>
                </td>
                <td class="actions-col">
                  <button class="action-btn" on:click={() => openEditItem(item)}>Edit</button>
                  <button class="action-btn danger" on:click={() => deleteItem(item)}>Remove</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
{/if}

{#if showBudgetModal}
  <div class="modal-overlay" on:click={closeBudgetModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingBudget ? 'Edit Budget' : 'New Budget'}</h2>
        <button class="modal-close" on:click={closeBudgetModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if budgetFormError}
          <div class="form-error">{budgetFormError}</div>
        {/if}
        <div class="form-field">
          <label for="bname">Name</label>
          <input id="bname" type="text" placeholder="e.g. July 2026" bind:value={budgetForm.name} />
        </div>
        <div class="form-row two-col">
          <div class="form-field">
            <label for="bperiod">Period</label>
            <select id="bperiod" bind:value={budgetForm.period}>
              <option value="monthly">Monthly</option>
              <option value="weekly">Weekly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
        </div>
        <div class="form-row two-col">
          <div class="form-field">
            <label for="bstart">Start Date</label>
            <input id="bstart" type="date" bind:value={budgetForm.start_date} />
          </div>
          <div class="form-field">
            <label for="bend">End Date (optional)</label>
            <input id="bend" type="date" bind:value={budgetForm.end_date} />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeBudgetModal}>Cancel</button>
        <button class="btn-primary" on:click={submitBudget} disabled={savingBudget}>
          {savingBudget ? 'Saving…' : editingBudget ? 'Save Changes' : 'Create Budget'}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showItemModal}
  <div class="modal-overlay" on:click={closeItemModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingItem ? 'Edit Budget Item' : 'Add Budget Item'}</h2>
        <button class="modal-close" on:click={closeItemModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if itemFormError}
          <div class="form-error">{itemFormError}</div>
        {/if}
        <div class="form-field">
          <label for="icategory">Category</label>
          <select id="icategory" bind:value={itemForm.category_id} disabled={!!editingItem}>
            <option value="">Select a category</option>
            {#each allCategories as cat}
              <option value={cat.category_id}>{cat.name}</option>
            {/each}
          </select>
        </div>
        <div class="form-field">
          <label for="iamount">Planned Amount</label>
          <input id="iamount" type="number" step="0.01" placeholder="e.g. 5000" bind:value={itemForm.planned_amount} />
        </div>
        <label class="checkbox-field">
          <input type="checkbox" bind:checked={itemForm.rollover_enabled} />
          <span>Enable rollover (unspent amounts carry to next period)</span>
        </label>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeItemModal}>Cancel</button>
        <button class="btn-primary" on:click={submitItem} disabled={savingItem}>
          {savingItem ? 'Saving…' : editingItem ? 'Save Changes' : 'Add Item'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .page { display: flex; flex-direction: column; gap: 24px; }

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

  .page-header { display: flex; justify-content: space-between; align-items: flex-start; }
  .page-title { font-size: 26px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; }
  .page-sub { font-size: 13px; color: #9ca3af; margin-top: 4px; }

  .back-link {
    background: none; border: none; padding: 0;
    font-size: 13px; color: #4f46e5; font-weight: 600;
    cursor: pointer; margin-bottom: 6px; display: block;
  }

  .header-actions { display: flex; gap: 8px; }

  .btn-primary {
    background: #4f46e5; color: #fff; padding: 10px 18px;
    border-radius: 8px; font-size: 14px; font-weight: 600;
    border: none; cursor: pointer; transition: background 0.2s;
  }

  .btn-primary:hover { background: #4338ca; }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

  .btn-secondary {
    background: #f3f4f6; color: #374151; padding: 10px 18px;
    border-radius: 8px; font-size: 14px; font-weight: 600;
    border: none; cursor: pointer; transition: background 0.2s;
  }

  .btn-secondary:hover { background: #e5e7eb; }

  .btn-danger {
    background: #fef2f2; color: #ef4444; padding: 10px 18px;
    border-radius: 8px; font-size: 14px; font-weight: 600;
    border: none; cursor: pointer; transition: background 0.2s;
  }

  .btn-danger:hover { background: #fee2e2; }

  .card {
    background: #fff;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 8px rgba(0,0,0,0.04);
  }

  .muted-center { color: #9ca3af; font-size: 14px; text-align: center; padding: 24px 0; }

  .budget-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }

  .budget-card { cursor: pointer; display: flex; flex-direction: column; gap: 14px; transition: box-shadow 0.15s; }
  .budget-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

  .budget-card-top { display: flex; justify-content: space-between; align-items: flex-start; }
  .budget-name { font-size: 15px; font-weight: 700; color: #1a1a2e; }
  .budget-dates { font-size: 12px; color: #9ca3af; margin-top: 2px; }

  .period-pill {
    font-size: 11px; font-weight: 700; color: #4f46e5;
    background: #ede9fe; padding: 4px 10px; border-radius: 99px;
    text-transform: capitalize;
  }

  .budget-totals { display: flex; gap: 6px; align-items: baseline; }
  .amt-actual { font-size: 18px; font-weight: 700; color: #1a1a2e; }
  .amt-sep { color: #d1d5db; }
  .amt-planned { font-size: 14px; color: #9ca3af; }

  .table-card { padding: 8px; overflow-x: auto; }

  table { width: 100%; border-collapse: collapse; font-size: 14px; }

  thead th {
    text-align: left; padding: 14px 16px;
    font-size: 11px; font-weight: 700; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.06em;
    border-bottom: 1px solid #f3f4f6;
  }

  .amt-col { text-align: right; }
  .progress-col { width: 180px; }
  .actions-col { text-align: right; width: 140px; }

  tbody td { padding: 14px 16px; border-bottom: 1px solid #f9fafb; vertical-align: middle; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: #f9fafb; }

  .cat-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 10px; border-radius: 99px;
  }

  .cat-pill.muted { background: #f3f4f6; color: #9ca3af; }

  .rollover-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 10px; border-radius: 99px;
    background: #f3f4f6; color: #9ca3af;
  }

  .rollover-pill.on { background: #f0fdf4; color: #16a34a; }

  .over-text { color: #ef4444; font-weight: 600; }

  .bar-track { height: 6px; background: #f3f4f6; border-radius: 99px; overflow: hidden; }
  .bar-fill { height: 100%; background: #4f46e5; border-radius: 99px; transition: width 0.5s ease; }
  .bar-fill.bar-warn { background: #f59e0b; }
  .bar-fill.bar-over { background: #ef4444; }

  .action-btn {
    background: none; border: none; font-size: 13px; font-weight: 600;
    color: #4f46e5; cursor: pointer; padding: 4px 8px; border-radius: 6px;
  }

  .action-btn:hover { background: #f5f3ff; }
  .action-btn.danger { color: #ef4444; }
  .action-btn.danger:hover { background: #fef2f2; }

  /* Modal */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(15, 17, 23, 0.45);
    display: flex; align-items: center; justify-content: center;
    z-index: 100; padding: 20px;
  }

  .modal {
    background: #fff; border-radius: 16px;
    width: 100%; max-width: 480px;
    max-height: 90vh; overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  }

  .modal-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 24px; border-bottom: 1px solid #f3f4f6;
  }

  .modal-header h2 { font-size: 18px; font-weight: 700; color: #1a1a2e; }

  .modal-close {
    background: none; border: none; font-size: 16px; color: #9ca3af;
    cursor: pointer; padding: 4px; border-radius: 6px; transition: all 0.15s;
  }

  .modal-close:hover { background: #f3f4f6; color: #1a1a2e; }

  .modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }

  .form-error {
    background: #fef2f2; color: #ef4444; font-size: 13px;
    padding: 10px 14px; border-radius: 8px; font-weight: 500;
  }

  .form-row { display: flex; gap: 12px; }
  .form-row.two-col > * { flex: 1; }

  .form-field { display: flex; flex-direction: column; gap: 6px; }
  .form-field label { font-size: 12px; font-weight: 600; color: #6b7280; }

  .form-field input, .form-field select {
    padding: 10px 12px; border-radius: 8px;
    border: 1px solid #e5e7eb; font-size: 14px;
    background: #fff; color: #1a1a2e;
    font-family: inherit;
  }

  .form-field input:focus, .form-field select:focus { outline: none; border-color: #4f46e5; }
  .form-field select:disabled { background: #f9fafb; color: #9ca3af; }

  .checkbox-field {
    display: flex; align-items: center; gap: 10px;
    font-size: 13px; color: #374151; cursor: pointer;
  }

  .checkbox-field input { width: 16px; height: 16px; }

  .modal-footer {
    display: flex; justify-content: flex-end; gap: 10px;
    padding: 16px 24px; border-top: 1px solid #f3f4f6;
  }
</style>