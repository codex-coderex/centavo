<script>
  import { onMount } from 'svelte'

  let user = null
  let allAccounts = []
  let allCategoryGroups = []
  let allCategories = []
  let allTags = []
  let allCurrencies = []
  let loading = true

  // profile
  let profileName = ''
  let savingProfile = false
  let profileSaved = false

  // account modal
  let showAccountModal = false
  let editingAccount = null
  let accountForm = { name: '', type: 'bank', currency_code: '' }
  let accountFormError = ''
  let savingAccount = false

  // category group modal
  let showGroupModal = false
  let groupForm = { name: '', type: 'Needs' }
  let groupFormError = ''
  let savingGroup = false

  // category modal
  let showCategoryModal = false
  let categoryForm = { group_id: '', name: '', color: '#4f46e5' }
  let categoryFormError = ''
  let savingCategory = false

  // tag modal
  let showTagModal = false
  let editingTag = null
  let tagForm = { name: '', color: '#4f46e5' }
  let tagFormError = ''
  let savingTag = false

  onMount(async () => {
    await loadData()
  })

  async function loadData() {
    loading = true
    try {
      const py = window.py

      if (!py) {
        user = { user_id: 1, name: 'Hoshi', created_at: '2026-01-01' }
        allAccounts = [
          { account_id: 1, name: 'BPI Savings', type: 'bank', currency_code: 'PHP', status: 'active' },
          { account_id: 2, name: 'GCash', type: 'ewallet', currency_code: 'PHP', status: 'active' },
          { account_id: 3, name: 'Cash', type: 'cash', currency_code: 'PHP', status: 'active' },
        ]
        allCategoryGroups = [
          { group_id: 1, user_id: 1, name: 'Food', type: 'Needs' },
          { group_id: 2, user_id: 1, name: 'Housing', type: 'Needs' },
          { group_id: 3, user_id: 1, name: 'Transport', type: 'Needs' },
          { group_id: 4, user_id: 1, name: 'Income', type: 'Income' },
        ]
        allCategories = [
          { category_id: 1, group_id: 1, name: 'Groceries', color: '#4f46e5', is_system: true, is_active: true },
          { category_id: 2, group_id: 1, name: 'Dining Out', color: '#4f46e5', is_system: true, is_active: true },
          { category_id: 3, group_id: 2, name: 'Rent', color: '#10b981', is_system: true, is_active: true },
          { category_id: 4, group_id: 2, name: 'Electricity', color: '#10b981', is_system: true, is_active: true },
          { category_id: 5, group_id: 3, name: 'Fare', color: '#f59e0b', is_system: true, is_active: true },
          { category_id: 6, group_id: 4, name: 'Salary', color: '#10b981', is_system: true, is_active: true },
        ]
        allTags = [
          { tag_id: 1, user_id: 1, name: 'Recurring', color: '#8b5cf6' },
          { tag_id: 2, user_id: 1, name: 'Reimbursable', color: '#06b6d4' },
        ]
        allCurrencies = [
          { code: 'PHP', name: 'Philippine Peso', symbol: '₱', decimal_places: 2 },
          { code: 'USD', name: 'US Dollar', symbol: '$', decimal_places: 2 },
          { code: 'EUR', name: 'Euro', symbol: '€', decimal_places: 2 },
          { code: 'GBP', name: 'British Pound', symbol: '£', decimal_places: 2 },
          { code: 'JPY', name: 'Japanese Yen', symbol: '¥', decimal_places: 0 },
        ]
        profileName = user.name
        loading = false
        return
      }

      const [u, accounts, groups, categories, tags, currencies] = await Promise.all([
        py.get_user(1),
        py.get_accounts(1),
        py.get_category_groups(1),
        py.get_all_categories(1),
        py.get_tags(1),
        py.get_currencies(),
      ])

      user = u
      allAccounts = accounts
      allCategoryGroups = groups
      allCategories = categories
      allTags = tags
      allCurrencies = currencies
      profileName = user?.name ?? ''

    } catch (e) {
      console.error(e)
    } finally {
      loading = false
    }
  }

  $: groupedCategories = allCategoryGroups.map(g => ({
    ...g,
    categories: allCategories.filter(c => c.group_id === g.group_id),
  }))

  $: activeAccounts = allAccounts.filter(a => a.status === 'active')
  $: archivedAccounts = allAccounts.filter(a => a.status === 'archived')

  // profile
  async function saveProfile() {
    if (!profileName.trim()) return
    savingProfile = true
    profileSaved = false
    try {
      const py = window.py
      if (py) await py.update_user(1, profileName.trim())
      user = { ...user, name: profileName.trim() }
      profileSaved = true
      setTimeout(() => profileSaved = false, 2000)
    } catch (e) {
      console.error(e)
    } finally {
      savingProfile = false
    }
  }

  // accounts
  function openCreateAccount() {
    editingAccount = null
    accountForm = { name: '', type: 'bank', currency_code: allCurrencies[0]?.code ?? 'PHP' }
    accountFormError = ''
    showAccountModal = true
  }

  function openEditAccount(account) {
    editingAccount = account
    accountForm = { name: account.name, type: account.type, currency_code: account.currency_code }
    accountFormError = ''
    showAccountModal = true
  }

  function closeAccountModal() {
    showAccountModal = false
    editingAccount = null
  }

  async function submitAccount() {
    accountFormError = ''
    if (!accountForm.name.trim()) { accountFormError = 'Please enter an account name.'; return }

    savingAccount = true
    try {
      const py = window.py

      if (!py) {
        if (editingAccount) {
          allAccounts = allAccounts.map(a => a.account_id === editingAccount.account_id
            ? { ...a, name: accountForm.name, type: accountForm.type, currency_code: accountForm.currency_code }
            : a)
        } else {
          const newId = Math.max(0, ...allAccounts.map(a => a.account_id)) + 1
          allAccounts = [...allAccounts, { account_id: newId, name: accountForm.name, type: accountForm.type, currency_code: accountForm.currency_code, status: 'active' }]
        }
        showAccountModal = false
        savingAccount = false
        return
      }

      if (editingAccount) {
        await py.update_account(editingAccount.account_id, accountForm.name, accountForm.type, accountForm.currency_code)
      } else {
        await py.create_account(1, accountForm.name, accountForm.type, accountForm.currency_code)
      }

      await loadData()
      showAccountModal = false

    } catch (e) {
      console.error(e)
      accountFormError = 'Something went wrong saving this account.'
    } finally {
      savingAccount = false
    }
  }

  async function archiveAccount(account) {
    if (!confirm(`Archive "${account.name}"? It will be hidden but transactions referencing it stay intact.`)) return
    try {
      const py = window.py
      if (py) await py.archive_account(account.account_id)
      allAccounts = allAccounts.map(a => a.account_id === account.account_id ? { ...a, status: 'archived' } : a)
    } catch (e) {
      console.error(e)
    }
  }

  // category groups
  function openCreateGroup() {
    groupForm = { name: '', type: 'Needs' }
    groupFormError = ''
    showGroupModal = true
  }

  function closeGroupModal() {
    showGroupModal = false
  }

  async function submitGroup() {
    groupFormError = ''
    if (!groupForm.name.trim()) { groupFormError = 'Please enter a group name.'; return }

    savingGroup = true
    try {
      const py = window.py

      if (!py) {
        const newId = Math.max(0, ...allCategoryGroups.map(g => g.group_id)) + 1
        allCategoryGroups = [...allCategoryGroups, { group_id: newId, user_id: 1, name: groupForm.name, type: groupForm.type }]
        showGroupModal = false
        savingGroup = false
        return
      }

      await py.create_category_group(1, groupForm.name, groupForm.type)
      await loadData()
      showGroupModal = false

    } catch (e) {
      console.error(e)
      groupFormError = 'Something went wrong saving this group.'
    } finally {
      savingGroup = false
    }
  }

  // categories
  function openCreateCategory(groupId = '') {
    categoryForm = { group_id: groupId, name: '', color: '#4f46e5' }
    categoryFormError = ''
    showCategoryModal = true
  }

  function closeCategoryModal() {
    showCategoryModal = false
  }

  async function submitCategory() {
    categoryFormError = ''
    if (!categoryForm.group_id) { categoryFormError = 'Please select a category group.'; return }
    if (!categoryForm.name.trim()) { categoryFormError = 'Please enter a category name.'; return }

    savingCategory = true
    try {
      const py = window.py

      if (!py) {
        const newId = Math.max(0, ...allCategories.map(c => c.category_id)) + 1
        allCategories = [...allCategories, { category_id: newId, group_id: Number(categoryForm.group_id), name: categoryForm.name, color: categoryForm.color, is_system: false, is_active: true }]
        showCategoryModal = false
        savingCategory = false
        return
      }

      await py.create_category(Number(categoryForm.group_id), categoryForm.name, categoryForm.color, false)
      await loadData()
      showCategoryModal = false

    } catch (e) {
      console.error(e)
      categoryFormError = 'Something went wrong saving this category.'
    } finally {
      savingCategory = false
    }
  }

  async function deactivateCategory(category) {
    if (category.is_system) {
      alert('System categories cannot be deactivated.')
      return
    }
    if (!confirm(`Deactivate "${category.name}"? Existing transactions keep this category, but it won't be selectable for new ones.`)) return
    try {
      const py = window.py
      if (py) await py.deactivate_category(category.category_id)
      allCategories = allCategories.map(c => c.category_id === category.category_id ? { ...c, is_active: false } : c)
    } catch (e) {
      console.error(e)
    }
  }

  // tags
  function openCreateTag() {
    editingTag = null
    tagForm = { name: '', color: '#4f46e5' }
    tagFormError = ''
    showTagModal = true
  }

  function openEditTag(tag) {
    editingTag = tag
    tagForm = { name: tag.name, color: tag.color ?? '#4f46e5' }
    tagFormError = ''
    showTagModal = true
  }

  function closeTagModal() {
    showTagModal = false
    editingTag = null
  }

  async function submitTag() {
    tagFormError = ''
    if (!tagForm.name.trim()) { tagFormError = 'Please enter a tag name.'; return }

    savingTag = true
    try {
      const py = window.py

      if (!py) {
        if (editingTag) {
          allTags = allTags.map(t => t.tag_id === editingTag.tag_id ? { ...t, name: tagForm.name, color: tagForm.color } : t)
        } else {
          const newId = Math.max(0, ...allTags.map(t => t.tag_id)) + 1
          allTags = [...allTags, { tag_id: newId, user_id: 1, name: tagForm.name, color: tagForm.color }]
        }
        showTagModal = false
        savingTag = false
        return
      }

      if (editingTag) {
        await py.update_tag(editingTag.tag_id, { name: tagForm.name, color: tagForm.color })
      } else {
        await py.create_tag(1, tagForm.name, tagForm.color)
      }

      await loadData()
      showTagModal = false

    } catch (e) {
      console.error(e)
      tagFormError = 'Something went wrong saving this tag.'
    } finally {
      savingTag = false
    }
  }

  async function deleteTag(tag) {
    if (!confirm(`Delete tag "${tag.name}"? It will be removed from all transactions.`)) return
    try {
      const py = window.py
      if (py) await py.delete_tag(tag.tag_id)
      allTags = allTags.filter(t => t.tag_id !== tag.tag_id)
    } catch (e) {
      console.error(e)
    }
  }
</script>

{#if loading}
  <div class="loading-state">
    <div class="spinner"></div>
    <span>Loading settings…</span>
  </div>
{:else}
  <div class="page">

    <div class="page-header">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="page-sub">Manage your profile, accounts, categories, and tags</p>
      </div>
    </div>

    <!-- Profile -->
    <div class="card">
      <div class="section-header">
        <span class="section-title"><span class="title-badge">◑</span> Profile</span>
      </div>
      <div class="form-row two-col">
        <div class="form-field">
          <label for="pname">Display Name</label>
          <input id="pname" type="text" bind:value={profileName} />
        </div>
      </div>
      <div class="profile-footer">
        <button class="btn-primary" on:click={saveProfile} disabled={savingProfile}>
          {savingProfile ? 'Saving…' : 'Save Changes'}
        </button>
        {#if profileSaved}<span class="saved-msg">Saved ✓</span>{/if}
      </div>
    </div>

    <!-- Accounts -->
    <div class="card">
      <div class="section-header">
        <span class="section-title"><span class="title-badge">◫</span> Accounts</span>
        <button class="link-btn" on:click={openCreateAccount}>+ Add Account</button>
      </div>

      {#if activeAccounts.length === 0}
        <p class="muted-center">No accounts yet.</p>
      {:else}
        <div class="list">
          {#each activeAccounts as account}
            <div class="list-row">
              <div class="list-info">
                <span class="list-name">{account.name}</span>
                <span class="list-meta">{account.type} &nbsp;·&nbsp; {account.currency_code}</span>
              </div>
              <div class="list-actions">
                <button class="action-btn" on:click={() => openEditAccount(account)}>Edit</button>
                <button class="action-btn danger" on:click={() => archiveAccount(account)}>Archive</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}

      {#if archivedAccounts.length > 0}
        <p class="subsection-title">Archived</p>
        <div class="list">
          {#each archivedAccounts as account}
            <div class="list-row archived">
              <div class="list-info">
                <span class="list-name">{account.name}</span>
                <span class="list-meta">{account.type} &nbsp;·&nbsp; {account.currency_code}</span>
              </div>
              <span class="archived-pill">Archived</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Categories -->
    <div class="card">
      <div class="section-header">
        <span class="section-title"><span class="title-badge">▦</span> Categories</span>
        <button class="link-btn" on:click={openCreateGroup}>+ Add Group</button>
      </div>

      <div class="groups-list">
        {#each groupedCategories as group}
          <div class="group-block">
            <div class="group-block-header">
              <span class="group-name">{group.name}</span>
              <span class="group-type">{group.type}</span>
              <button class="link-btn small" on:click={() => openCreateCategory(group.group_id)}>+ Add Category</button>
            </div>
            <div class="tag-list">
              {#each group.categories as cat}
                <div class="cat-chip" class:inactive={!cat.is_active} style="background:{cat.color}1a; color:{cat.color}">
                  <span>{cat.name}</span>
                  {#if cat.is_system}<span class="system-badge">system</span>{/if}
                  {#if !cat.is_system}
                    <button class="chip-x" on:click={() => deactivateCategory(cat)} title="Deactivate">✕</button>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Tags -->
    <div class="card">
      <div class="section-header">
        <span class="section-title"><span class="title-badge">#</span> Tags</span>
        <button class="link-btn" on:click={openCreateTag}>+ Add Tag</button>
      </div>

      {#if allTags.length === 0}
        <p class="muted-center">No tags yet.</p>
      {:else}
        <div class="tag-list">
          {#each allTags as tag}
            <div class="cat-chip" style="background:{tag.color}1a; color:{tag.color}">
              <span>{tag.name}</span>
              <button class="chip-x" on:click={() => openEditTag(tag)} title="Edit">✎</button>
              <button class="chip-x" on:click={() => deleteTag(tag)} title="Delete">✕</button>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Currencies -->
    <div class="card">
      <div class="section-header">
        <span class="section-title"><span class="title-badge">₱</span> Currencies</span>
      </div>
      <div class="currency-grid">
        {#each allCurrencies as cur}
          <div class="currency-item">
            <span class="currency-symbol">{cur.symbol}</span>
            <div class="currency-info">
              <span class="currency-code">{cur.code}</span>
              <span class="currency-name">{cur.name}</span>
            </div>
          </div>
        {/each}
      </div>
    </div>

  </div>
{/if}

{#if showAccountModal}
  <div class="modal-overlay" on:click={closeAccountModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingAccount ? 'Edit Account' : 'New Account'}</h2>
        <button class="modal-close" on:click={closeAccountModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if accountFormError}<div class="form-error">{accountFormError}</div>{/if}
        <div class="form-field">
          <label for="aname">Account Name</label>
          <input id="aname" type="text" placeholder="e.g. BPI Savings" bind:value={accountForm.name} />
        </div>
        <div class="form-row two-col">
          <div class="form-field">
            <label for="atype">Type</label>
            <select id="atype" bind:value={accountForm.type}>
              <option value="bank">Bank</option>
              <option value="ewallet">E-Wallet</option>
              <option value="cash">Cash</option>
              <option value="credit">Credit Card</option>
            </select>
          </div>
          <div class="form-field">
            <label for="acurrency">Currency</label>
            <select id="acurrency" bind:value={accountForm.currency_code}>
              {#each allCurrencies as cur}
                <option value={cur.code}>{cur.code} ({cur.symbol})</option>
              {/each}
            </select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeAccountModal}>Cancel</button>
        <button class="btn-primary" on:click={submitAccount} disabled={savingAccount}>
          {savingAccount ? 'Saving…' : editingAccount ? 'Save Changes' : 'Add Account'}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showGroupModal}
  <div class="modal-overlay" on:click={closeGroupModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>New Category Group</h2>
        <button class="modal-close" on:click={closeGroupModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if groupFormError}<div class="form-error">{groupFormError}</div>{/if}
        <div class="form-field">
          <label for="gname">Group Name</label>
          <input id="gname" type="text" placeholder="e.g. Entertainment" bind:value={groupForm.name} />
        </div>
        <div class="form-field">
          <label for="gtype">Type</label>
          <select id="gtype" bind:value={groupForm.type}>
            <option value="Needs">Needs</option>
            <option value="Wants">Wants</option>
            <option value="Savings">Savings</option>
            <option value="Income">Income</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeGroupModal}>Cancel</button>
        <button class="btn-primary" on:click={submitGroup} disabled={savingGroup}>
          {savingGroup ? 'Saving…' : 'Create Group'}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showCategoryModal}
  <div class="modal-overlay" on:click={closeCategoryModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>New Category</h2>
        <button class="modal-close" on:click={closeCategoryModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if categoryFormError}<div class="form-error">{categoryFormError}</div>{/if}
        <div class="form-field">
          <label for="cgroup">Category Group</label>
          <select id="cgroup" bind:value={categoryForm.group_id}>
            <option value="">Select a group</option>
            {#each allCategoryGroups as g}
              <option value={g.group_id}>{g.name}</option>
            {/each}
          </select>
        </div>
        <div class="form-field">
          <label for="cname">Category Name</label>
          <input id="cname" type="text" placeholder="e.g. Streaming Services" bind:value={categoryForm.name} />
        </div>
        <div class="form-field">
          <label for="ccolor">Color</label>
          <input id="ccolor" type="color" bind:value={categoryForm.color} />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeCategoryModal}>Cancel</button>
        <button class="btn-primary" on:click={submitCategory} disabled={savingCategory}>
          {savingCategory ? 'Saving…' : 'Create Category'}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showTagModal}
  <div class="modal-overlay" on:click={closeTagModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingTag ? 'Edit Tag' : 'New Tag'}</h2>
        <button class="modal-close" on:click={closeTagModal}>✕</button>
      </div>
      <div class="modal-body">
        {#if tagFormError}<div class="form-error">{tagFormError}</div>{/if}
        <div class="form-field">
          <label for="tname">Tag Name</label>
          <input id="tname" type="text" placeholder="e.g. Reimbursable" bind:value={tagForm.name} />
        </div>
        <div class="form-field">
          <label for="tcolor">Color</label>
          <input id="tcolor" type="color" bind:value={tagForm.color} />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeTagModal}>Cancel</button>
        <button class="btn-primary" on:click={submitTag} disabled={savingTag}>
          {savingTag ? 'Saving…' : editingTag ? 'Save Changes' : 'Create Tag'}
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

  .card {
    background: #fff;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 8px rgba(0,0,0,0.04);
    display: flex; flex-direction: column; gap: 16px;
  }

  .section-header { display: flex; justify-content: space-between; align-items: center; }
  .section-title { font-size: 14px; font-weight: 600; color: #1a1a2e; display: flex; align-items: center; gap: 8px; }

  .title-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 6px;
    background: #ede9fe; color: #4f46e5;
    font-size: 12px;
  }

  .link-btn {
    background: none; border: none; font-size: 13px; font-weight: 600;
    color: #4f46e5; cursor: pointer; padding: 4px 8px; border-radius: 6px;
  }

  .link-btn:hover { background: #f5f3ff; }
  .link-btn.small { font-size: 12px; margin-left: auto; }

  .muted-center { color: #9ca3af; font-size: 14px; text-align: center; padding: 16px 0; }

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

  .form-field input[type="color"] { padding: 4px; height: 40px; cursor: pointer; }

  .profile-footer { display: flex; align-items: center; gap: 12px; }
  .saved-msg { font-size: 13px; color: #10b981; font-weight: 600; }

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

  .list { display: flex; flex-direction: column; gap: 4px; }

  .list-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 8px; border-radius: 8px;
    border-bottom: 1px solid #f3f4f6;
  }

  .list-row:last-child { border-bottom: none; }
  .list-row.archived { opacity: 0.6; }

  .list-info { display: flex; flex-direction: column; gap: 2px; }
  .list-name { font-size: 14px; font-weight: 600; color: #1a1a2e; }
  .list-meta { font-size: 12px; color: #9ca3af; text-transform: capitalize; }

  .list-actions { display: flex; gap: 4px; }

  .action-btn {
    background: none; border: none; font-size: 13px; font-weight: 600;
    color: #4f46e5; cursor: pointer; padding: 4px 10px; border-radius: 6px;
  }

  .action-btn:hover { background: #f5f3ff; }
  .action-btn.danger { color: #ef4444; }
  .action-btn.danger:hover { background: #fef2f2; }

  .archived-pill {
    font-size: 12px; font-weight: 600; color: #9ca3af;
    background: #f3f4f6; padding: 4px 10px; border-radius: 99px;
  }

  .subsection-title {
    font-size: 11px; font-weight: 700; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-top: 8px;
  }

  .groups-list { display: flex; flex-direction: column; gap: 16px; }

  .group-block { display: flex; flex-direction: column; gap: 10px; }

  .group-block-header { display: flex; align-items: center; gap: 8px; }
  .group-name { font-size: 13px; font-weight: 700; color: #1a1a2e; }
  .group-type {
    font-size: 11px; font-weight: 600; color: #9ca3af;
    background: #f3f4f6; padding: 2px 8px; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.04em;
  }

  .tag-list { display: flex; gap: 8px; flex-wrap: wrap; }

  .cat-chip {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 12px; font-weight: 600;
    padding: 5px 10px; border-radius: 99px;
  }

  .cat-chip.inactive { opacity: 0.4; }

  .system-badge {
    font-size: 9px; font-weight: 700; color: #9ca3af;
    background: #fff; padding: 1px 6px; border-radius: 99px;
    text-transform: uppercase;
  }

  .chip-x {
    background: none; border: none; cursor: pointer;
    font-size: 11px; color: inherit; opacity: 0.6;
    padding: 0; line-height: 1;
  }

  .chip-x:hover { opacity: 1; }

  .currency-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }

  .currency-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px; border-radius: 10px; background: #f9fafb;
  }

  .currency-symbol {
    font-size: 18px; font-weight: 700; color: #4f46e5;
    width: 32px; height: 32px; border-radius: 8px;
    background: #ede9fe; display: flex; align-items: center; justify-content: center;
  }

  .currency-info { display: flex; flex-direction: column; gap: 2px; }
  .currency-code { font-size: 13px; font-weight: 700; color: #1a1a2e; }
  .currency-name { font-size: 11px; color: #9ca3af; }

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

  .modal-footer {
    display: flex; justify-content: flex-end; gap: 10px;
    padding: 16px 24px; border-top: 1px solid #f3f4f6;
  }
</style>