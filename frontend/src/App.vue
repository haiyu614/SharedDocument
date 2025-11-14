<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>协同文档系统 MVP</h1>
      <nav>
        <RouterLink to="/">工作台</RouterLink>
        <RouterLink to="/documents">文档列表</RouterLink>
        <RouterLink to="/versions">版本管理</RouterLink>
        <RouterLink to="/login">登录</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-surface);
  padding: 1rem 2rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.app-header nav {
  display: flex;
  gap: 1rem;
}

.app-main {
  flex: 1;
  padding: 2rem;
  background: var(--color-background);
}
</style>

