<template>
  <div class="app">
    <nav class="navbar">
      <router-link to="/" class="nav-brand">LTH CEQ Stats</router-link>
      <div class="nav-controls">
        <select
          v-if="programmes.length"
          class="programme-select"
          :value="currentProgramme"
          @change="onProgrammeChange"
        >
          <option value="">All Programmes</option>
          <option v-for="p in programmes" :key="p.code" :value="p.code">
            {{ p.code }} - {{ p.name_en }}
          </option>
        </select>
        <button class="menu-btn" @click="toggleSidebar" aria-label="Toggle menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </nav>
    <div class="layout">
      <aside class="sidebar" :class="{ open: sidebarOpen }">
        <CourseSidebar
          :programme-code="currentProgramme"
          @course-selected="closeSidebarOnMobile"
        />
      </aside>
      <div v-if="sidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>
      <main class="content">
        <router-view :key="$route.fullPath" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseData } from './composables/useCourseData.js'
import CourseSidebar from './components/CourseSidebar.vue'

const router = useRouter()
const route = useRoute()
const { programmes } = useCourseData()

const sidebarOpen = ref(false)

const currentProgramme = computed(() => {
  return route.params.programmeCode || ''
})

watch(currentProgramme, (code) => {
  if (code) {
    const prog = programmes.value.find(p => p.code === code)
    document.title = prog ? `${prog.code} - LTH CEQ Stats` : 'LTH CEQ Stats'
  } else {
    document.title = 'LTH CEQ Stats'
  }
}, { immediate: true })

const onProgrammeChange = (e) => {
  const code = e.target.value
  if (code) {
    router.push(`/programme/${code}`)
  } else {
    router.push('/')
  }
}

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

.nav-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.programme-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  cursor: pointer;
  min-width: 220px;
  max-width: 350px;
  outline: none;
}

.programme-select option {
  color: #333;
  background: white;
}

.programme-select:hover {
  background: rgba(255, 255, 255, 0.2);
}

.programme-select:focus {
  border-color: rgba(255, 255, 255, 0.6);
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

  .programme-select {
    min-width: 0;
    max-width: 180px;
    font-size: 12px;
    padding: 6px 8px;
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
