<script>
  import Router from 'svelte-spa-router'
  import Sidebar from './lib/Sidebar.svelte'
  import Dashboard from './pages/Dashboard.svelte'
  import Transactions from './pages/Transactions.svelte'
  import Budgets from './pages/Budgets.svelte'
  import Goals from './pages/Goals.svelte'
  import Recurring from './pages/Recurring.svelte'
  import Settings from './pages/Settings.svelte'

  const routes = {
    '/': Dashboard,
    '/transactions': Transactions,
    '/budgets': Budgets,
    '/goals': Goals,
    '/recurring': Recurring,
    '/settings': Settings,
  }
</script>

<div class="app">
  <Sidebar />
  <main class="content">
    <Router {routes} />
  </main>
</div>

<style>
  .app {
    display: flex;
    background: #f7f8fa;
    min-height: 100vh;
  }

  .content {
    margin-left: 220px;
    padding: 32px;
    width: 100%;
    color: #1a1a2e;
  }
</style>
