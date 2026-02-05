<template>
  <div class="app">
    <nav class="navbar">
      <router-link to="/" class="nav-brand">MMSR Course Stats</router-link>
    </nav>
    <div class="layout">
      <aside class="sidebar">
        <CourseSidebar />
      </aside>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import CourseSidebar from './components/CourseSidebar.vue'
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  background: #f5f5f5;
  color: #333;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #2c3e50;
  padding: 15px 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.nav-brand {
  color: white;
  font-size: 1.5em;
  font-weight: bold;
  text-decoration: none;
}

.nav-brand:hover {
  opacity: 0.9;
}

.layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #ddd;
  flex-shrink: 0;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  height: calc(100vh - 60px);
}

a {
  color: #3498db;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
