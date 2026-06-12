<script>
  import { onMount } from 'svelte'

  let recurringList = []
  let allAccounts = []
  let allCategories = []
  let accountMap = {}
  let categoryMap = {}
  let loading = true

  let showModal = false
  let editingRule = null
  let form = { account_id: '', category_id: '', merchant: '', amount: '', interval: 1, frequency_unit: 'month', next_due: '', end_date: '' }
  let formError = ''
  let saving = false

  let actionLoading = {}

  onMount(async () => {
    await loadData()
  })

  async function loadData() {
    loading = true
    try {
      const py = window.py

      if (!py) {
        allAccounts = [
          { account_id: 1, name: 'BPI Savings', type: 'bank', currency_code: 'PHP', status: 'active' },
          { account_id: 2, name: 'GCash', type: 'ewallet', currency_code: 'PHP', status: 'active' },
        ]
        allCategories = [
          { category_id: 3, name: 'Rent', color: '#10b981' },
          { category_id: 4, name: 'Electricity', color: '#10b981' },
          { category_id: 9, name: 'Subscriptions', color: '#8b5cf6' },
          { category_id: 6, name: 'Salary', color: '#10b981' },
        ]
        recurringList = [
          { recurring_id: 1, account_id: 1, category_id: 3, merchant: 'Landlord', amount: -10000, interval: 1, frequency_unit: 'month', next_due: '2026-07-01', end_date: null, status: 'active' },
          { recurring_id: 2, account_id: 2, category_id: 9, merchant: 'Netflix', amount: -549, interval: 1, frequency_unit: 'month', next_due: '2026-06-15', end_date: null, status: 'active' },
          { recurring_id: 3, account_id: 1, category_id: 6, merchant: 'Salary', amount: 30000, interval: 2, frequency_unit: 'week', next_due: '2026-06-19', end_date: null, status: 'active' },
          { recurring_id: 4, account_id: 1, category_id: 4, merchant: 'Meralco', amount: -800, interval: 1, frequency_unit: 'month', next_due: '2026-06-07', end_date: '2026-12-31', status: 'paused' },
        ]
        buildMaps()
        loading = false
        return
      }

      const [r, accounts, categories] = await Promise.all([
        py.get_recurring(1),
        py.get_accounts(1),
        py.get_all_categories(1),
      ])

      recurringList = r
      allAccounts = accounts
      allCategories = categories

      buildMaps()

    } catch (e) {
      console.error(e)
    } finally {
      loading = false
    }
  }

  function buildMaps() {
    accountMap = {}
    categoryMap = {}
    for (const a of allAccounts) accountMap[a.account_id] = a
    for (const c of allCategories) categoryMap[c.category_id] = c
  }

  function fmt(n) {
    return '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }

  function fmtSigned(n) {
    return (n >= 0 ? '+' : '−') + '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }

  function frequencyLabel(interval, unit) {
    const u = interval === 1 ? unit : unit + 's'
    return `Every ${interval} ${u}`
  }

  function isDue(rule) {
    if (rule.status !== 'active') return false
    const today = new Date().toISOString().split('T')[0]
    return rule.next_due <= today
  }

  function todayStr() {
    return new Date().toISOString().split('T')[0]
  }

  $: activeRules = recurringList.filter(r => r.status === 'active')
  $: pausedRules = recurringList.filter(r => r.status === 'paused')
  $: inactiveRules = recurringList.filter(r => r.status === 'inactive')

  // create/edit
  function openCreate() {
    editingRule = null
    form = { account_id: allAccounts[0]?.account_id ?? '', category_id: '', merchant: '', amount: '', interval: 1, frequency_unit: 'month', next_due: todayStr(), end_date: '' }
    formError = ''
    showModal = true
  }

  function openEdit(rule) {
    editingRule = rule
    form = {
      account_id: rule.account_id,
      category_id: rule.category_id ?? '',
      merchant: rule.merchant ?? '',
      amount: rule.amount,
      interval: rule.interval,
      frequency_unit: rule.frequency_unit,
      next_due: rule.next_due,
      end_date: rule.end_date ?? '',
    }
    formError = ''
    showModal = true
  }

  function closeModal() {
    showModal = false
    editingRule = null
  }

  async function submitForm() {
    formError = ''
    if (!form.account_id) { formError = 'Please select an account.'; return }
    if (!form.merchant.trim()) { formError = 'Please enter a merchant name.'; return }
    if (form.amount === '' || isNaN(Number(form.amount)) || Number(form.amount) === 0) {
      formError = 'Please enter a valid non-zero amount.'; return
    }
    if (!form.interval || Number(form.interval) <= 0) { formError = 'Please enter a valid interval.'; return }
    if (!form.next_due) { formError = 'Please select a next due date.'; return }

    saving = true
    try {
      const py = window.py

      if (!py) {
        if (editingRule) {
          recurringList = recurringList.map(r => r.recurring_id === editingRule.recurring_id
            ? { ...r, ...form, category_id: form.category_id ? Number(form.category_id) : null, account_id: Number(form.account_id), amount: Number(form.amount), interval: Number(form.interval), end_date: form.end_date || null }
            : r)
        } else {
          const newId = Math.max(0, ...recurringList.map(r => r.recurring_id)) + 1
          recurringList = [...recurringList, {
            recurring_id: newId,
            account_id: Number(form.account_id),
            category_id: form.category_id ? Number(form.category_id) : null,
            merchant: form.merchant,
            amount: Number(form.amount),
            interval: Number(form.interval),
            frequency_unit: form.frequency_unit,
            next_due: form.next_due,
            end_date: form.end_date || null,
            status: 'active',
          }]
        }
        showModal = false
        saving = false
        return
      }

      if (editingRule) {
        formError = 'Editing existing rules is not yet supported by the backend.'
        saving = false
        return
      } else {
        await py.create_recurring(
          Number(form.account_id),
          Number(form.amount),
          Number(form.interval),
          form.frequency_unit,
          form.next_due,
          form.category_id ? Number(form.category_id) : null,
          form.merchant,
          form.end_date || null
        )
      }

      await loadData()
      showModal = false

    } catch (e) {
      console.error(e)
      formError = 'Something went wrong saving this rule.'
    } finally {
      saving = false
    }
  }

  async function togglePause(rule) {
    actionLoading[rule.recurring_id] = true
    try {
      const py = window.py
      if (rule.status === 'active') {
        if (py) await py.pause_recurring(rule.recurring_id)
        recurringList = recurringList.map(r => r.recurring_id === rule.recurring_id ? { ...r, status: 'paused' } : r)
      } else if (rule.status === 'paused') {
        if (py) await py.resume_recurring(rule.recurring_id)
        recurringList = recurringList.map(r => r.recurring_id === rule.recurring_id ? { ...r, status: 'active' } : r)
      }
    } catch (e) {
      console.error(e)
    } finally {
      actionLoading[rule.recurring_id] = false
    }
  }

  async function generateNow(rule) {
    if (!confirm(`Generate a transaction for "${rule.merchant}" now?`)) return
    actionLoading[rule.recurring_id] = true
    try {
      const py = window.py
      if (py) {
        await py.generate_transaction(rule.recurring_id)
        await loadData()
      } else {
        alert('Transaction generated (mock mode — connect to backend to see real effect).')
      }
    } catch (e) {
      console.error(e)
    } finally {
      actionLoading[rule.recurring_id] = false
    }
  }
</script>

{#if loading}
  <div class="loading-state">
    <div class="spinner"></div>
    <span>Loading recurring rules…</span>
  </div>
{:else}
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Recurring</h1>
        <p class="page-sub">{activeRules.length} active &nbsp;·&nbsp; {pausedRules.length} paused</p>
      </div>
      <button class="btn-primary" on:click={openCreate}>+ New Recurring</button>
    </div>

    {#if recurringList.length === 0}
      <div class="card">
        <p class="muted-center">No recurring rules yet. Add one to automate regular transactions.</p>
      </div>
    {:else}
      <div class="card table-card">
        <table>
          <thead>
            <tr>
              <th>Merchant</th>
              <th>Category</th>
              <th>Account</th>
              <th>Frequency</th>
              <th>Next Due</th>
              <th>Status</th>
              <th class="amt-col">Amount</th>
              <th class="actions-col"></th>
            </tr>
          </thead>
          <tbody>
            {#each recurringList as rule}
              {@const cat = categoryMap[rule.category_id]}
              {@const acc = accountMap[rule.account_id]}
              <tr class:due={isDue(rule)}>
                <td>
                  <div class="merchant-cell">
                    <span class="merchant-name">{rule.merchant ?? 'Unknown'}</span>
                    {#if isDue(rule)}
                      <span class="due-badge">Due</span>
                    {/if}
                  </div>
                </td>
                <td>
                  {#if cat}
                    <span class="cat-pill" style="background:{cat.color}1a; color:{cat.color}">{cat.name}</span>
                  {:else}
                    <span class="cat-pill muted">Uncategorized</span>
                  {/if}
                </td>
                <td class="acc-cell">{acc?.name ?? '—'}</td>
                <td class="freq-cell">{frequencyLabel(rule.interval, rule.frequency_unit)}</td>
                <td class="date-cell">
                  {rule.next_due}
                  {#if rule.end_date}<span class="end-date">until {rule.end_date}</span>{/if}
                </td>
                <td>
                  <span class="status-pill" class:paused={rule.status === 'paused'} class:inactive={rule.status === 'inactive'}>
                    {rule.status}
                  </span>
                </td>
                <td class="amt-col">
                  <span class="amt" class:pos={rule.amount > 0} class:neg={rule.amount < 0}>
                    {fmtSigned(rule.amount)}
                  </span>
                </td>
                <td class="actions-col">
                  {#if rule.status !== 'inactive'}
                    <button class="action-btn" disabled={actionLoading[rule.recurring_id]} on:click={() => togglePause(rule)}>
                      {rule.status === 'active' ? 'Pause' : 'Resume'}
                    </button>
                    <button class="action-btn" disabled={actionLoading[rule.recurring_id]} on:click={() => generateNow(rule)}>
                      Generate Now
                    </button>
                  {/if}
                  <button class="action-btn" on:click={() => openEdit(rule)}>Edit</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
{/if}

{#if showModal}
  <div class="modal-overlay" on:click={closeModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingRule ? 'Edit Recurring Rule' : 'New Recurring Rule'}</h2>
        <button class="modal-close" on:click={closeModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if formError}
          <div class="form-error">{formError}</div>
        {/if}

        <div class="form-row two-col">
          <div class="form-field">
            <label for="merchant">Merchant</label>
            <input id="merchant" type="text" placeholder="e.g. Netflix" bind:value={form.merchant} />
          </div>
          <div class="form-field">
            <label for="amount">Amount</label>
            <input id="amount" type="number" step="0.01" placeholder="e.g. -549 or 30000" bind:value={form.amount} />
          </div>
        </div>

        <p class="field-hint">Use a negative amount for expenses, positive for income.</p>

        <div class="form-row two-col">
          <div class="form-field">
            <label for="account">Account</label>
            <select id="account" bind:value={form.account_id}>
              {#each allAccounts as acc}
                <option value={acc.account_id}>{acc.name}</option>
              {/each}
            </select>
          </div>
          <div class="form-field">
            <label for="category">Category</label>
            <select id="category" bind:value={form.category_id}>
              <option value="">Uncategorized</option>
              {#each allCategories as cat}
                <option value={cat.category_id}>{cat.name}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-row two-col">
          <div class="form-field">
            <label for="interval">Repeat Every</label>
            <input id="interval" type="number" min="1" bind:value={form.interval} />
          </div>
          <div class="form-field">
            <label for="unit">Unit</label>
            <select id="unit" bind:value={form.frequency_unit}>
              <option value="day">Day(s)</option>
              <option value="week">Week(s)</option>
              <option value="month">Month(s)</option>
              <option value="year">Year(s)</option>
            </select>
          </div>
        </div>

        <div class="form-row two-col">
          <div class="form-field">
            <label for="nextdue">Next Due Date</label>
            <input id="nextdue" type="date" bind:value={form.next_due} />
          </div>
          <div class="form-field">
            <label for="enddate">End Date (optional)</label>
            <input id="enddate" type="date" bind:value={form.end_date} />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeModal}>Cancel</button>
        <button class="btn-primary" on:click={submitForm} disabled={saving}>
          {saving ? 'Saving…' : editingRule ? 'Save Changes' : 'Create Rule'}
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

  .card {
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 8px rgba(0,0,0,0.04);
  }

  .table-card { padding: 8px; overflow-x: auto; }

  .muted-center { color: #9ca3af; font-size: 14px; text-align: center; padding: 40px 0; }

  table { width: 100%; border-collapse: collapse; font-size: 14px; }

  thead th {
    text-align: left; padding: 14px 16px;
    font-size: 11px; font-weight: 700; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.06em;
    border-bottom: 1px solid #f3f4f6;
  }

  .amt-col { text-align: right; }
  .actions-col { text-align: right; white-space: nowrap; }

  tbody td { padding: 14px 16px; border-bottom: 1px solid #f9fafb; vertical-align: middle; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: #f9fafb; }
  tbody tr.due { background: #eff6ff; }
  tbody tr.due:hover { background: #dbeafe; }

  .merchant-cell { display: flex; align-items: center; gap: 8px; }
  .merchant-name { font-weight: 600; color: #1a1a2e; }

  .due-badge {
    font-size: 10px; font-weight: 700; color: #2563eb;
    background: #dbeafe; padding: 2px 8px; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.04em;
  }

  .cat-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 10px; border-radius: 99px;
  }

  .cat-pill.muted { background: #f3f4f6; color: #9ca3af; }

  .acc-cell { color: #6b7280; }
  .freq-cell { color: #374151; }
  .date-cell { color: #6b7280; white-space: nowrap; }
  .end-date { display: block; font-size: 11px; color: #d1d5db; }

  .status-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 10px; border-radius: 99px;
    background: #f0fdf4; color: #16a34a;
    text-transform: capitalize;
  }

  .status-pill.paused { background: #fef3c7; color: #d97706; }
  .status-pill.inactive { background: #f3f4f6; color: #9ca3af; }

  .amt { font-weight: 700; }
  .amt.pos { color: #10b981; }
  .amt.neg { color: #ef4444; }

  .action-btn {
    background: none; border: none; font-size: 13px; font-weight: 600;
    color: #4f46e5; cursor: pointer; padding: 4px 8px; border-radius: 6px;
  }

  .action-btn:hover { background: #f5f3ff; }
  .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Modal */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(15, 17, 23, 0.45);
    display: flex; align-items: center; justify-content: center;
    z-index: 100; padding: 20px;
  }

  .modal {
    background: #fff; border-radius: 16px;
    width: 100%; max-width: 520px;
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

  .field-hint { font-size: 12px; color: #9ca3af; margin-top: -8px; }

  .modal-footer {
    display: flex; justify-content: flex-end; gap: 10px;
    padding: 16px 24px; border-top: 1px solid #f3f4f6;
  }
</style>