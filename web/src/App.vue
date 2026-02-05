<template>
  <div class="app">
    <nav class="navbar">
      <router-link to="/" class="nav-brand">MMSR Course Stats</router-link>
      <button class="menu-btn" @click="toggleSidebar" aria-label="Toggle menu">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </nav>
    <div class="layout">
      <aside class="sidebar" :class="{ open: sidebarOpen }">
        <CourseSidebar @course-selected="closeSidebarOnMobile" />
      </aside>
      <div v-if="sidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import CourseSidebar from './components/CourseSidebar.vue'

const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

const closeSidebarOnMobile = () => {
  if (window.innerWidth <= 768) {
    sidebarOpen.value = false
  }
}

const handleResize = () => {
  if (window.innerWidth > 768) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
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
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.menu-btn {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.menu-btn span {
  display: block;
  width: 25px;
  height: 3px;
  background: white;
  border-radius: 2px;
  transition: transform 0.3s, opacity 0.3s;
}

.layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #ddd;
  flex-shrink: 0;
  height: calc(100vh - 60px);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.sidebar-backdrop {
  display: none;
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

/* Mobile styles */
@media (max-width: 768px) {
  .navbar {
    padding: 15px 20px;
  }

  .nav-brand {
    font-size: 1.2em;
  }

  .menu-btn {
    display: flex;
  }

  .sidebar {
    position: fixed;
    top: 60px;
    left: 0;
    z-index: 1000;
    width: 80%;
    max-width: 300px;
    transform: translateX(-100%);
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }

  .content {
    padding: 16px;
    height: calc(100vh - 60px);
  }
}
</style>
