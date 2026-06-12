<script>
  import { onMount } from 'svelte'

  let transactions = []
  let categoryMap = {}
  let accountMap = {}
  let tagMap = {}
  let txnTags = {}
  let loading = true

  let searchQuery = ''
  let filterCategory = 'all'
  let filterAccount = 'all'
  let filterStatus = 'all'

  let allCategories = []
  let allAccounts = []
  let allTags = []

  // modal state
  let showModal = false
  let editingTxn = null
  let saving = false
  let formError = ''

  let form = {
    account_id: '',
    category_id: '',
    merchant: '',
    amount: '',
    txn_date: '',
    note: '',
    selectedTags: [],
  }

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
          { account_id: 3, name: 'Cash', type: 'cash', currency_code: 'PHP', status: 'active' },
        ]
        allCategories = [
          { category_id: 1, name: 'Groceries', group_id: 1, color: '#4f46e5' },
          { category_id: 2, name: 'Dining Out', group_id: 1, color: '#4f46e5' },
          { category_id: 4, name: 'Electricity', group_id: 2, color: '#10b981' },
          { category_id: 5, name: 'Fare', group_id: 3, color: '#f59e0b' },
          { category_id: 6, name: 'Salary', group_id: 4, color: '#10b981' },
        ]
        allTags = [
          { tag_id: 1, name: 'Recurring', color: '#8b5cf6' },
          { tag_id: 2, name: 'Reimbursable', color: '#06b6d4' },
        ]
        transactions = [
          { transaction_id: 1, account_id: 1, merchant: 'SM Supermarket', amount: -1200, txn_date: '2026-06-09', category_id: 1, status: 'cleared', needs_review: false, note: '', updated_at: '2026-06-09' },
          { transaction_id: 2, account_id: 2, merchant: 'Jollibee', amount: -350, txn_date: '2026-06-08', category_id: 2, status: 'cleared', needs_review: false, note: '', updated_at: '2026-06-08' },
          { transaction_id: 3, account_id: 1, merchant: 'Meralco', amount: -800, txn_date: '2026-06-07', category_id: 4, status: 'cleared', needs_review: true, note: 'Higher than usual', updated_at: '2026-06-07' },
          { transaction_id: 4, account_id: 1, merchant: 'Salary', amount: 30000, txn_date: '2026-06-05', category_id: 6, status: 'cleared', needs_review: false, note: '', updated_at: '2026-06-05' },
          { transaction_id: 5, account_id: 3, merchant: 'Grab', amount: -150, txn_date: '2026-06-05', category_id: 5, status: 'pending', needs_review: false, note: '', updated_at: '2026-06-05' },
        ]
        txnTags = { 1: [allTags[0]], 3: [allTags[1]] }
        buildMaps()
        loading = false
        return
      }

      const [accounts, categories, tags, txns] = await Promise.all([
        py.get_accounts(1),
        py.get_all_categories(1),
        py.get_tags(1),
        py.get_transactions_by_user(1),
      ])

      allAccounts = accounts
      allCategories = categories
      allTags = tags
      transactions = txns

      const tagResults = await Promise.all(
        txns.map(t => py.get_transaction_tags(t.transaction_id))
      )
      txnTags = {}
      txns.forEach((t, i) => { txnTags[t.transaction_id] = tagResults[i] })

      buildMaps()

    } catch (e) {
      console.error(e)
    } finally {
      loading = false
    }
  }

  function buildMaps() {
    categoryMap = {}
    accountMap = {}
    tagMap = {}
    for (const c of allCategories) categoryMap[c.category_id] = c
    for (const a of allAccounts) accountMap[a.account_id] = a
    for (const t of allTags) tagMap[t.tag_id] = t
  }

  $: filtered = transactions.filter(t => {
    if (filterCategory !== 'all' && t.category_id !== Number(filterCategory)) return false
    if (filterAccount !== 'all' && t.account_id !== Number(filterAccount)) return false
    if (filterStatus !== 'all' && t.status !== filterStatus) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const merchant = (t.merchant ?? '').toLowerCase()
      const note = (t.note ?? '').toLowerCase()
      if (!merchant.includes(q) && !note.includes(q)) return false
    }
    return true
  })

  function fmtSigned(n) {
    return (n >= 0 ? '+' : '−') + '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }

  function todayStr() {
    const d = new Date()
    return d.toISOString().split('T')[0]
  }

  function openAddModal() {
    editingTxn = null
    form = {
      account_id: allAccounts[0]?.account_id ?? '',
      category_id: '',
      merchant: '',
      amount: '',
      txn_date: todayStr(),
      note: '',
      selectedTags: [],
    }
    formError = ''
    showModal = true
  }

  function openEditModal(txn) {
    editingTxn = txn
    const existingTags = (txnTags[txn.transaction_id] ?? []).map(t => t.tag_id)
    form = {
      account_id: txn.account_id,
      category_id: txn.category_id ?? '',
      merchant: txn.merchant ?? '',
      amount: txn.amount,
      txn_date: txn.txn_date,
      note: txn.note ?? '',
      selectedTags: existingTags,
    }
    formError = ''
    showModal = true
  }

  function closeModal() {
    showModal = false
    editingTxn = null
  }

  function toggleTag(tagId) {
    if (form.selectedTags.includes(tagId)) {
      form.selectedTags = form.selectedTags.filter(id => id !== tagId)
    } else {
      form.selectedTags = [...form.selectedTags, tagId]
    }
  }

  async function handleSubmit() {
    formError = ''

    if (!form.account_id) { formError = 'Please select an account.'; return }
    if (!form.merchant.trim()) { formError = 'Please enter a merchant.'; return }
    if (form.amount === '' || isNaN(Number(form.amount)) || Number(form.amount) === 0) {
      formError = 'Please enter a valid non-zero amount.'; return
    }
    if (!form.txn_date) { formError = 'Please select a date.'; return }
    if (!form.category_id) { formError = 'Please select a category.'; return }

    saving = true
    try {
      const py = window.py

      if (!py) {
        // mock save
        if (editingTxn) {
          transactions = transactions.map(t =>
            t.transaction_id === editingTxn.transaction_id
              ? { ...t, account_id: Number(form.account_id), category_id: Number(form.category_id), merchant: form.merchant, amount: Number(form.amount), txn_date: form.txn_date, note: form.note }
              : t
          )
          txnTags[editingTxn.transaction_id] = form.selectedTags.map(id => tagMap[id])
        } else {
          const newId = Math.max(0, ...transactions.map(t => t.transaction_id)) + 1
          transactions = [{
            transaction_id: newId,
            account_id: Number(form.account_id),
            category_id: Number(form.category_id),
            merchant: form.merchant,
            amount: Number(form.amount),
            txn_date: form.txn_date,
            note: form.note,
            status: 'cleared',
            needs_review: false,
            updated_at: form.txn_date,
          }, ...transactions]
          txnTags[newId] = form.selectedTags.map(id => tagMap[id])
        }
        showModal = false
        saving = false
        return
      }

      if (editingTxn) {
        await py.update_transaction(editingTxn.transaction_id, {
          merchant: form.merchant,
          amount: Number(form.amount),
          category_id: Number(form.category_id),
          note: form.note || null,
          txn_date: form.txn_date,
        })

        const oldTags = (txnTags[editingTxn.transaction_id] ?? []).map(t => t.tag_id)
        const newTags = form.selectedTags

        const toAdd = newTags.filter(id => !oldTags.includes(id))
        const toRemove = oldTags.filter(id => !newTags.includes(id))

        await Promise.all([
          ...toAdd.map(id => py.add_tag_to_transaction(editingTxn.transaction_id, id)),
          ...toRemove.map(id => py.remove_tag_from_transaction(editingTxn.transaction_id, id)),
        ])
      } else {
        const result = await py.create_transaction(
          Number(form.account_id),
          Number(form.amount),
          form.txn_date,
          form.merchant,
          Number(form.category_id),
          form.note || null,
          null,
          null
        )
        const newId = result.transaction_id

        await Promise.all(
          form.selectedTags.map(id => py.add_tag_to_transaction(newId, id))
        )
      }

      await loadData()
      showModal = false

    } catch (e) {
      console.error(e)
      formError = 'Something went wrong saving this transaction.'
    } finally {
      saving = false
    }
  }
</script>

{#if loading}
  <div class="loading-state">
    <div class="spinner"></div>
    <span>Loading transactions…</span>
  </div>
{:else}
  <div class="page">

    <div class="page-header">
      <div>
        <h1 class="page-title">Transactions</h1>
        <p class="page-sub">{filtered.length} of {transactions.length} transactions</p>
      </div>
      <button class="btn-primary" on:click={openAddModal}>+ Add Transaction</button>
    </div>

    <div class="filters">
      <input class="search-input" type="text" placeholder="Search merchant or note…" bind:value={searchQuery} />

      <select class="filter-select" bind:value={filterCategory}>
        <option value="all">All Categories</option>
        {#each allCategories as cat}
          <option value={cat.category_id}>{cat.name}</option>
        {/each}
      </select>

      <select class="filter-select" bind:value={filterAccount}>
        <option value="all">All Accounts</option>
        {#each allAccounts as acc}
          <option value={acc.account_id}>{acc.name}</option>
        {/each}
      </select>

      <select class="filter-select" bind:value={filterStatus}>
        <option value="all">All Statuses</option>
        <option value="cleared">Cleared</option>
        <option value="pending">Pending</option>
      </select>
    </div>

    <div class="card table-card">
      {#if filtered.length === 0}
        <p class="muted-center">No transactions match your filters.</p>
      {:else}
        <table>
          <thead>
            <tr>
              <th>Merchant</th>
              <th>Category</th>
              <th>Account</th>
              <th>Tags</th>
              <th>Date</th>
              <th>Status</th>
              <th class="amt-col">Amount</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered as txn}
              {@const cat = categoryMap[txn.category_id]}
              {@const acc = accountMap[txn.account_id]}
              {@const tags = txnTags[txn.transaction_id] ?? []}
              <tr class="txn-row" class:review={txn.needs_review} on:click={() => openEditModal(txn)}>
                <td>
                  <div class="merchant-cell">
                    <span class="merchant-name">{txn.merchant ?? 'Unknown'}</span>
                    {#if txn.needs_review}
                      <span class="review-badge">Needs Review</span>
                    {/if}
                  </div>
                  {#if txn.note}
                    <span class="note-text">{txn.note}</span>
                  {/if}
                </td>
                <td>
                  {#if cat}
                    <span class="cat-pill" style="background:{cat.color}1a; color:{cat.color}">{cat.name}</span>
                  {:else}
                    <span class="cat-pill muted">Uncategorized</span>
                  {/if}
                </td>
                <td class="acc-cell">{acc?.name ?? '—'}</td>
                <td>
                  <div class="tag-list">
                    {#each tags as tag}
                      <span class="tag-pill" style="background:{tag.color}1a; color:{tag.color}">{tag.name}</span>
                    {/each}
                  </div>
                </td>
                <td class="date-cell">{txn.txn_date}</td>
                <td>
                  <span class="status-pill" class:pending={txn.status === 'pending'}>{txn.status}</span>
                </td>
                <td class="amt-col">
                  <span class="amt" class:pos={txn.amount > 0} class:neg={txn.amount < 0}>
                    {fmtSigned(txn.amount)}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>

  </div>
{/if}

{#if showModal}
  <div class="modal-overlay" on:click={closeModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingTxn ? 'Edit Transaction' : 'Add Transaction'}</h2>
        <button class="modal-close" on:click={closeModal}>✕</button>
      </div>

      <div class="modal-body">
        {#if formError}
          <div class="form-error">{formError}</div>
        {/if}

        <div class="form-row two-col">
          <div class="form-field">
            <label for="merchant">Merchant</label>
            <input id="merchant" type="text" placeholder="e.g. SM Supermarket" bind:value={form.merchant} />
          </div>
          <div class="form-field">
            <label for="amount">Amount</label>
            <input id="amount" type="number" step="0.01" placeholder="e.g. -500 or 30000" bind:value={form.amount} />
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
              <option value="">Select a category</option>
              {#each allCategories as cat}
                <option value={cat.category_id}>{cat.name}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-row two-col">
          <div class="form-field">
            <label for="date">Date</label>
            <input id="date" type="date" bind:value={form.txn_date} />
          </div>
          <div class="form-field">
            <label for="note">Note (optional)</label>
            <input id="note" type="text" placeholder="Add a note…" bind:value={form.note} />
          </div>
        </div>

        <div class="form-field">
          <label>Tags</label>
          <div class="tag-picker">
            {#if allTags.length === 0}
              <span class="field-hint">No tags created yet.</span>
            {:else}
              {#each allTags as tag}
                <button
                  type="button"
                  class="tag-toggle"
                  class:selected={form.selectedTags.includes(tag.tag_id)}
                  style={form.selectedTags.includes(tag.tag_id) ? `background:${tag.color}1a; color:${tag.color}; border-color:${tag.color}` : ''}
                  on:click={() => toggleTag(tag.tag_id)}
                >
                  {tag.name}
                </button>
              {/each}
            {/if}
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeModal}>Cancel</button>
        <button class="btn-primary" on:click={handleSubmit} disabled={saving}>
          {saving ? 'Saving…' : editingTxn ? 'Save Changes' : 'Add Transaction'}
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

  .filters { display: flex; gap: 10px; flex-wrap: wrap; }

  .search-input {
    flex: 1; min-width: 220px;
    padding: 10px 14px; border-radius: 8px;
    border: 1px solid #e5e7eb; font-size: 14px;
    background: #fff; color: #1a1a2e;
  }

  .search-input:focus { outline: none; border-color: #4f46e5; }

  .filter-select {
    padding: 10px 12px; border-radius: 8px;
    border: 1px solid #e5e7eb; font-size: 14px;
    background: #fff; color: #374151; cursor: pointer;
  }

  .filter-select:focus { outline: none; border-color: #4f46e5; }

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

  tbody td { padding: 14px 16px; border-bottom: 1px solid #f9fafb; vertical-align: top; }
  .txn-row { cursor: pointer; }
  .txn-row:last-child td { border-bottom: none; }
  .txn-row:hover { background: #f9fafb; }
  .txn-row.review { background: #fffbeb; }
  .txn-row.review:hover { background: #fef3c7; }

  .merchant-cell { display: flex; align-items: center; gap: 8px; }
  .merchant-name { font-weight: 600; color: #1a1a2e; }

  .review-badge {
    font-size: 10px; font-weight: 700; color: #d97706;
    background: #fef3c7; padding: 2px 8px; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.04em;
  }

  .note-text { display: block; font-size: 12px; color: #9ca3af; margin-top: 2px; }

  .cat-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 10px; border-radius: 99px;
  }

  .cat-pill.muted { background: #f3f4f6; color: #9ca3af; }

  .acc-cell { color: #6b7280; }
  .date-cell { color: #6b7280; white-space: nowrap; }

  .tag-list { display: flex; gap: 4px; flex-wrap: wrap; }

  .tag-pill {
    display: inline-block; font-size: 11px; font-weight: 600;
    padding: 3px 8px; border-radius: 99px;
  }

  .status-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 10px; border-radius: 99px;
    background: #f0fdf4; color: #16a34a;
    text-transform: capitalize;
  }

  .status-pill.pending { background: #fef3c7; color: #d97706; }

  .amt { font-weight: 700; }
  .amt.pos { color: #10b981; }
  .amt.neg { color: #ef4444; }

  /* Modal */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(15, 17, 23, 0.45);
    display: flex; align-items: center; justify-content: center;
    z-index: 100;
    padding: 20px;
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

  .form-field input:focus, .form-field select:focus {
    outline: none; border-color: #4f46e5;
  }

  .field-hint { font-size: 12px; color: #9ca3af; margin-top: -8px; }

  .tag-picker { display: flex; gap: 8px; flex-wrap: wrap; }

  .tag-toggle {
    padding: 6px 14px; border-radius: 99px;
    border: 1px solid #e5e7eb; background: #fff;
    font-size: 13px; font-weight: 600; color: #6b7280;
    cursor: pointer; transition: all 0.15s;
  }

  .tag-toggle:hover { border-color: #c7c9ff; }

  .tag-toggle.selected { border-width: 1px; }

  .modal-footer {
    display: flex; justify-content: flex-end; gap: 10px;
    padding: 16px 24px; border-top: 1px solid #f3f4f6;
  }
</style>