<script>
  import { onMount } from 'svelte'

  let goals = []
  let allAccounts = []
  let allCategories = []
  let allTxns = []
  let accountMap = {}
  let loading = true

  // create/edit goal modal
  let showGoalModal = false
  let editingGoal = null
  let goalForm = { name: '', target_amount: '', target_date: '', account_id: '' }
  let goalFormError = ''
  let savingGoal = false

  // fund modal
  let showFundModal = false
  let fundingGoal = null
  let fundForm = { account_id: '', category_id: '', amount: '', txn_date: '' }
  let fundFormError = ''
  let saving = false

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
          { category_id: 1, name: 'Groceries' },
          { category_id: 7, name: 'Emergency Fund' },
          { category_id: 8, name: 'Investment' },
        ]
        allTxns = [
          { transaction_id: 10, goal_id: 1, amount: -2000, account_id: 1, category_id: 7, txn_date: '2026-06-01' },
          { transaction_id: 11, goal_id: 1, amount: -1500, account_id: 1, category_id: 7, txn_date: '2026-06-05' },
          { transaction_id: 12, goal_id: 2, amount: -5000, account_id: 1, category_id: 8, txn_date: '2026-06-03' },
        ]
        goals = [
          { goal_id: 1, user_id: 1, account_id: 1, name: 'Emergency Fund', target_amount: 30000, target_date: '2026-12-31', status: 'active' },
          { goal_id: 2, user_id: 1, account_id: 1, name: 'New Laptop', target_amount: 60000, target_date: '2026-10-01', status: 'active' },
          { goal_id: 3, user_id: 1, account_id: 2, name: 'Vacation Fund', target_amount: 15000, target_date: null, status: 'completed' },
        ]
        buildMaps()
        loading = false
        return
      }

      const [g, accounts, categories, txns] = await Promise.all([
        py.get_goals(1),
        py.get_accounts(1),
        py.get_all_categories(1),
        py.get_transactions_by_user(1),
      ])

      goals = g
      allAccounts = accounts
      allCategories = categories
      allTxns = txns

      buildMaps()

    } catch (e) {
      console.error(e)
    } finally {
      loading = false
    }
  }

  function buildMaps() {
    accountMap = {}
    for (const a of allAccounts) accountMap[a.account_id] = a
  }

  function progressFor(goalId) {
    return allTxns
      .filter(t => t.goal_id === goalId)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0)
  }

  function pct(goal) {
    const progress = progressFor(goal.goal_id)
    if (!goal.target_amount) return 0
    return Math.min((progress / goal.target_amount) * 100, 100)
  }

  function fmt(n) {
    return '₱' + Math.abs(n ?? 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })
  }

  function todayStr() {
    return new Date().toISOString().split('T')[0]
  }

  $: activeGoals = goals.filter(g => g.status !== 'completed')
  $: completedGoals = goals.filter(g => g.status === 'completed')

  // goal create/edit
  function openCreateGoal() {
    editingGoal = null
    goalForm = { name: '', target_amount: '', target_date: '', account_id: allAccounts[0]?.account_id ?? '' }
    goalFormError = ''
    showGoalModal = true
  }

  function openEditGoal(goal) {
    editingGoal = goal
    goalForm = {
      name: goal.name,
      target_amount: goal.target_amount,
      target_date: goal.target_date ?? '',
      account_id: goal.account_id ?? '',
    }
    goalFormError = ''
    showGoalModal = true
  }

  function closeGoalModal() {
    showGoalModal = false
    editingGoal = null
  }

  async function submitGoal() {
    goalFormError = ''
    if (!goalForm.name.trim()) { goalFormError = 'Please enter a goal name.'; return }
    if (goalForm.target_amount === '' || isNaN(Number(goalForm.target_amount)) || Number(goalForm.target_amount) <= 0) {
      goalFormError = 'Please enter a valid target amount.'; return
    }
    if (!goalForm.account_id) { goalFormError = 'Please select an account.'; return }

    savingGoal = true
    try {
      const py = window.py

      if (!py) {
        if (editingGoal) {
          goals = goals.map(g => g.goal_id === editingGoal.goal_id
            ? { ...g, name: goalForm.name, target_amount: Number(goalForm.target_amount), target_date: goalForm.target_date || null, account_id: Number(goalForm.account_id) }
            : g)
        } else {
          const newId = Math.max(0, ...goals.map(g => g.goal_id)) + 1
          goals = [...goals, {
            goal_id: newId, user_id: 1,
            account_id: Number(goalForm.account_id),
            name: goalForm.name,
            target_amount: Number(goalForm.target_amount),
            target_date: goalForm.target_date || null,
            status: 'active',
          }]
        }
        showGoalModal = false
        savingGoal = false
        return
      }

      if (editingGoal) {
        await py.update_goal(editingGoal.goal_id, goalForm.name, Number(goalForm.target_amount), goalForm.target_date || null, Number(goalForm.account_id))
      } else {
        await py.create_goal(1, goalForm.name, Number(goalForm.target_amount), goalForm.target_date || null, Number(goalForm.account_id))
      }

      await loadData()
      showGoalModal = false

    } catch (e) {
      console.error(e)
      goalFormError = 'Something went wrong saving this goal.'
    } finally {
      savingGoal = false
    }
  }

  async function markComplete(goal) {
    if (!confirm(`Mark "${goal.name}" as completed?`)) return
    try {
      const py = window.py
      if (py) await py.complete_goal(goal.goal_id)
      goals = goals.map(g => g.goal_id === goal.goal_id ? { ...g, status: 'completed' } : g)
    } catch (e) {
      console.error(e)
    }
  }

  // fund modal
  function openFundModal(goal) {
    fundingGoal = goal
    const savingsCat = allCategories.find(c => c.name === 'Emergency Fund' || c.name === 'Investment')
    fundForm = {
      account_id: goal.account_id ?? allAccounts[0]?.account_id ?? '',
      category_id: savingsCat?.category_id ?? '',
      amount: '',
      txn_date: todayStr(),
    }
    fundFormError = ''
    showFundModal = true
  }

  function closeFundModal() {
    showFundModal = false
    fundingGoal = null
  }

  async function submitFund() {
    fundFormError = ''
    if (fundForm.amount === '' || isNaN(Number(fundForm.amount)) || Number(fundForm.amount) <= 0) {
      fundFormError = 'Please enter a valid amount.'; return
    }
    if (!fundForm.account_id) { fundFormError = 'Please select an account.'; return }
    if (!fundForm.category_id) { fundFormError = 'Please select a category.'; return }
    if (!fundForm.txn_date) { fundFormError = 'Please select a date.'; return }

    saving = true
    try {
      const py = window.py

      if (!py) {
        allTxns = [...allTxns, {
          transaction_id: Math.max(0, ...allTxns.map(t => t.transaction_id)) + 1,
          goal_id: fundingGoal.goal_id,
          amount: -Number(fundForm.amount),
          account_id: Number(fundForm.account_id),
          category_id: Number(fundForm.category_id),
          txn_date: fundForm.txn_date,
        }]
        showFundModal = false
        saving = false
        return
      }

      await py.fund_goal(fundingGoal.goal_id, Number(fundForm.account_id), Number(fundForm.amount), fundForm.txn_date, Number(fundForm.category_id))
      await loadData()
      showFundModal = false

    } catch (e) {
      console.error(e)
      fundFormError = 'Something went wrong recording this contribution.'
    } finally {
      saving = false
    }
  }
</script>

{#if loading}
  <div class="loading-state">
    <div class="spinner"></div>
    <span>Loading goals…</span>
  </div>
{:else}
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Goals</h1>
        <p class="page-sub">{activeGoals.length} active &nbsp;·&nbsp; {completedGoals.length} completed</p>
      </div>
      <button class="btn-primary" on:click={openCreateGoal}>+ New Goal</button>
    </div>

    {#if goals.length === 0}
      <div class="card">
        <p class="muted-center">No savings goals yet. Create one to start tracking progress.</p>
      </div>
    {:else}
      {#if activeGoals.length > 0}
        <div class="goals-grid">
          {#each activeGoals as goal}
            {@const progress = progressFor(goal.goal_id)}
            {@const p = pct(goal)}
            {@const acc = accountMap[goal.account_id]}
            <div class="card goal-card">
              <div class="goal-top">
                <div>
                  <p class="goal-name">{goal.name}</p>
                  <p class="goal-meta">{acc?.name ?? '—'} {#if goal.target_date}&nbsp;·&nbsp; due {goal.target_date}{/if}</p>
                </div>
                <span class="progress-pct">{Math.round(p)}%</span>
              </div>

              <div class="goal-amounts">
                <span class="amt-current">{fmt(progress)}</span>
                <span class="amt-sep">/</span>
                <span class="amt-target">{fmt(goal.target_amount)}</span>
              </div>

              <div class="bar-track">
                <div class="bar-fill" class:bar-complete={p >= 100} style="width:{p}%"></div>
              </div>

              <div class="goal-actions">
                <button class="btn-secondary" on:click={() => openFundModal(goal)}>+ Add Funds</button>
                <button class="action-btn" on:click={() => openEditGoal(goal)}>Edit</button>
                {#if p >= 100}
                  <button class="action-btn complete" on:click={() => markComplete(goal)}>Mark Complete</button>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}

      {#if completedGoals.length > 0}
        <div class="section-header" style="margin-top: 8px;">
          <span class="section-title">Completed</span>
        </div>
        <div class="goals-grid">
          {#each completedGoals as goal}
            {@const progress = progressFor(goal.goal_id)}
            {@const acc = accountMap[goal.account_id]}
            <div class="card goal-card completed">
              <div class="goal-top">
                <div>
                  <p class="goal-name">{goal.name}</p>
                  <p class="goal-meta">{acc?.name ?? '—'}</p>
                </div>
                <span class="completed-badge">✓ Done</span>
              </div>
              <div class="goal-amounts">
                <span class="amt-current">{fmt(progress)}</span>
                <span class="amt-sep">/</span>
                <span class="amt-target">{fmt(goal.target_amount)}</span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  </div>
{/if}

{#if showGoalModal}
  <div class="modal-overlay" on:click={closeGoalModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingGoal ? 'Edit Goal' : 'New Goal'}</h2>
        <button class="modal-close" on:click={closeGoalModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if goalFormError}
          <div class="form-error">{goalFormError}</div>
        {/if}
        <div class="form-field">
          <label for="gname">Goal Name</label>
          <input id="gname" type="text" placeholder="e.g. New Laptop" bind:value={goalForm.name} />
        </div>
        <div class="form-row two-col">
          <div class="form-field">
            <label for="gtarget">Target Amount</label>
            <input id="gtarget" type="number" step="0.01" placeholder="e.g. 60000" bind:value={goalForm.target_amount} />
          </div>
          <div class="form-field">
            <label for="gdate">Target Date (optional)</label>
            <input id="gdate" type="date" bind:value={goalForm.target_date} />
          </div>
        </div>
        <div class="form-field">
          <label for="gaccount">Linked Account</label>
          <select id="gaccount" bind:value={goalForm.account_id}>
            {#each allAccounts as acc}
              <option value={acc.account_id}>{acc.name}</option>
            {/each}
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeGoalModal}>Cancel</button>
        <button class="btn-primary" on:click={submitGoal} disabled={savingGoal}>
          {savingGoal ? 'Saving…' : editingGoal ? 'Save Changes' : 'Create Goal'}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showFundModal}
  <div class="modal-overlay" on:click={closeFundModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Add Funds — {fundingGoal.name}</h2>
        <button class="modal-close" on:click={closeFundModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if fundFormError}
          <div class="form-error">{fundFormError}</div>
        {/if}
        <div class="form-row two-col">
          <div class="form-field">
            <label for="famount">Amount</label>
            <input id="famount" type="number" step="0.01" placeholder="e.g. 1000" bind:value={fundForm.amount} />
          </div>
          <div class="form-field">
            <label for="fdate">Date</label>
            <input id="fdate" type="date" bind:value={fundForm.txn_date} />
          </div>
        </div>
        <div class="form-row two-col">
          <div class="form-field">
            <label for="faccount">From Account</label>
            <select id="faccount" bind:value={fundForm.account_id}>
              {#each allAccounts as acc}
                <option value={acc.account_id}>{acc.name}</option>
              {/each}
            </select>
          </div>
          <div class="form-field">
            <label for="fcategory">Category</label>
            <select id="fcategory" bind:value={fundForm.category_id}>
              <option value="">Select a category</option>
              {#each allCategories as cat}
                <option value={cat.category_id}>{cat.name}</option>
              {/each}
            </select>
          </div>
        </div>
        <p class="field-hint">This will create a transaction linked to this goal.</p>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeFundModal}>Cancel</button>
        <button class="btn-primary" on:click={submitFund} disabled={saving}>
          {saving ? 'Saving…' : 'Add Funds'}
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

  .section-header { display: flex; justify-content: space-between; align-items: center; }
  .section-title { font-size: 14px; font-weight: 600; color: #1a1a2e; }

  .btn-primary {
    background: #4f46e5; color: #fff; padding: 10px 18px;
    border-radius: 8px; font-size: 14px; font-weight: 600;
    border: none; cursor: pointer; transition: background 0.2s;
  }

  .btn-primary:hover { background: #4338ca; }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

  .btn-secondary {
    background: #f3f4f6; color: #374151; padding: 8px 14px;
    border-radius: 8px; font-size: 13px; font-weight: 600;
    border: none; cursor: pointer; transition: background 0.2s;
  }

  .btn-secondary:hover { background: #e5e7eb; }

  .card {
    background: #fff;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 8px rgba(0,0,0,0.04);
  }

  .muted-center { color: #9ca3af; font-size: 14px; text-align: center; padding: 24px 0; }

  .goals-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }

  .goal-card { display: flex; flex-direction: column; gap: 14px; }
  .goal-card.completed { opacity: 0.7; }

  .goal-top { display: flex; justify-content: space-between; align-items: flex-start; }
  .goal-name { font-size: 15px; font-weight: 700; color: #1a1a2e; }
  .goal-meta { font-size: 12px; color: #9ca3af; margin-top: 2px; }

  .progress-pct {
    font-size: 13px; font-weight: 700; color: #4f46e5;
    background: #ede9fe; padding: 4px 10px; border-radius: 99px;
  }

  .completed-badge {
    font-size: 12px; font-weight: 700; color: #16a34a;
    background: #f0fdf4; padding: 4px 10px; border-radius: 99px;
  }

  .goal-amounts { display: flex; gap: 6px; align-items: baseline; }
  .amt-current { font-size: 20px; font-weight: 700; color: #1a1a2e; }
  .amt-sep { color: #d1d5db; }
  .amt-target { font-size: 14px; color: #9ca3af; }

  .bar-track { height: 6px; background: #f3f4f6; border-radius: 99px; overflow: hidden; }
  .bar-fill { height: 100%; background: #4f46e5; border-radius: 99px; transition: width 0.5s ease; }
  .bar-fill.bar-complete { background: #10b981; }

  .goal-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }

  .action-btn {
    background: none; border: none; font-size: 13px; font-weight: 600;
    color: #4f46e5; cursor: pointer; padding: 6px 10px; border-radius: 6px;
  }

  .action-btn:hover { background: #f5f3ff; }
  .action-btn.complete { color: #10b981; }
  .action-btn.complete:hover { background: #f0fdf4; }

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

  .field-hint { font-size: 12px; color: #9ca3af; }

  .modal-footer {
    display: flex; justify-content: flex-end; gap: 10px;
    padding: 16px 24px; border-top: 1px solid #f3f4f6;
  }
</style>