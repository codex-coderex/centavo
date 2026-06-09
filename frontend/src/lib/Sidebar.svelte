<script>
  const links = [
    { path: '/', label: 'Dashboard', icon: '▦' },
    { path: '/transactions', label: 'Transactions', icon: '↕' },
    { path: '/budgets', label: 'Budgets', icon: '◫' },
    { path: '/goals', label: 'Goals', icon: '◎' },
    { path: '/recurring', label: 'Recurring', icon: '↻' },
    { path: '/settings', label: 'Settings', icon: '⚙' },
  ]
</script>

<nav class="sidebar">
  <div class="logo">Centavo</div>
  <ul>
    {#each links as link}
      <li>
        <a href="#{link.path}">
          <span class="icon">{link.icon}</span>
          <span>{link.label}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>

<style>
  .sidebar {
    width: 220px;
    height: 100vh;
    background: #1a1f2e;
    display: flex;
    flex-direction: column;
    padding: 24px 16px;
    position: fixed;
    left: 0;
    top: 0;
  }

  .logo {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 40px;
    padding-left: 12px;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li a {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    color: #8b92a5;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.2s;
  }

  li a:hover {
    background: #252b3b;
    color: #ffffff;
  }

  .icon {
    font-size: 16px;
    width: 20px;
    text-align: center;
  }
</style>