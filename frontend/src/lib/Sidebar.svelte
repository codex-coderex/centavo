<script>
  const links = [
    { path: '/', label: 'Dashboard', icon: '▦' },
    { path: '/transactions', label: 'Transactions', icon: '↕' },
    { path: '/budgets', label: 'Budgets', icon: '◫' },
    { path: '/goals', label: 'Goals', icon: '◎' },
    { path: '/recurring', label: 'Recurring', icon: '↻' },
    { path: '/settings', label: 'Settings', icon: '⚙' },
  ]

  let currentHash = window.location.hash.replace('#', '') || '/'

  window.addEventListener('hashchange', () => {
    currentHash = window.location.hash.replace('#', '') || '/'
  })
</script>

<nav class="sidebar">
  <div class="logo">
    <span class="logo-icon">C</span>
    <span class="logo-text">Centavo</span>
  </div>
  <ul>
    {#each links as link}
      <li class:active={currentHash === link.path}>
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
    background: #ffffff;
    display: flex;
    flex-direction: column;
    padding: 24px 16px;
    position: fixed;
    left: 0;
    top: 0;
    border-right: 1px solid #f0f0f0;
  }

  .logo {
    margin-bottom: 36px;
    padding-left: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .logo-icon {
    background: #4f46e5;
    color: #fff;
    width: 32px;
    height: 32px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    font-weight: 800;
    font-family: Georgia, 'Times New Roman', serif;
    flex-shrink: 0;
  }

  .logo-text {
    font-size: 19px;
    font-weight: 800;
    color: #1a1a2e;
    letter-spacing: -0.03em;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  li a {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    color: #6b7280;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.15s;
  }

  li a:hover {
    background: #f5f3ff;
    color: #4f46e5;
  }

  li.active a {
    background: #ede9fe;
    color: #4f46e5;
    font-weight: 600;
  }

  .icon {
    font-size: 15px;
    width: 20px;
    text-align: center;
  }
</style>