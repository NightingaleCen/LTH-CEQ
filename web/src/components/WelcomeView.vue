<template>
  <div class="welcome-view">
    <!-- Programme selection grid (home page) -->
    <template v-if="!programmeCode">
      <h1>LTH CEQ Stats</h1>
      <p>Select a programme to view its course evaluation data.</p>
      <div class="programme-grid">
        <router-link
          v-for="p in programmes"
          :key="p.code"
          :to="`/programme/${p.code}`"
          class="programme-card"
        >
          <div class="programme-code">{{ p.code }}</div>
          <div class="programme-name">{{ p.name_en }}</div>
          <div class="programme-count">{{ p.course_count }} courses</div>
        </router-link>
      </div>
    </template>

    <!-- Programme-specific stats -->
    <template v-else>
      <h1>{{ programmeName }}</h1>
      <p>Select a course from the list on the left to view its evaluation data.</p>
      <div class="stats">
        <div class="stat-card">
          <div class="stat-number">{{ metadata.total_courses }}</div>
          <div class="stat-label">Courses</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ metadata.total_evaluations }}</div>
          <div class="stat-label">Evaluations</div>
        </div>
      </div>
    </template>

    <footer class="footer">
      <p>All course and CEQ information comes from official LTH websites.</p>
      <a href="https://github.com/NightingaleCen/LTH-CEQ" target="_blank" rel="noopener">View on GitHub ↗</a>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCourseData } from '../composables/useCourseData.js'

const route = useRoute()
const { programmes, getProgrammeMetadata } = useCourseData()

const programmeCode = computed(() => route.params.programmeCode)

const programmeName = computed(() => {
  if (!programmeCode.value) return ''
  const prog = programmes.value.find(p => p.code === programmeCode.value)
  return prog ? `${prog.code} - ${prog.name_en}` : programmeCode.value
})

const metadata = computed(() => {
  if (!programmeCode.value) return { total_courses: 0, total_evaluations: 0 }
  return getProgrammeMetadata(programmeCode.value)
})
</script>

<style scoped>
.welcome-view {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 40px;
  overflow-y: auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

p {
  color: #666;
  font-size: 1.1em;
  margin-bottom: 40px;
}

.programme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  width: 100%;
  max-width: 900px;
  margin-bottom: 40px;
}

.programme-card {
  background: white;
  padding: 24px 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
  text-align: left;
  border: 2px solid transparent;
}

.programme-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: #3498db;
}

.programme-code {
  font-size: 1.3em;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 6px;
}

.programme-name {
  font-size: 0.95em;
  color: #555;
  line-height: 1.4;
  margin-bottom: 10px;
}

.programme-count {
  font-size: 0.85em;
  color: #3498db;
  font-weight: 500;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 40px;
}

.stat-card {
  background: white;
  padding: 30px 50px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 3em;
  font-weight: bold;
  color: #3498db;
}

.stat-label {
  color: #666;
  font-size: 1.1em;
  margin-top: 5px;
}

.footer {
  margin-top: auto;
  padding-top: 60px;
  padding-bottom: 20px;
  border-top: 1px solid #ddd;
  color: #888;
  font-size: 0.9em;
  width: 100%;
  max-width: 600px;
}

.footer p {
  margin: 0 0 10px 0;
  font-size: 0.9em;
}

.footer a {
  color: #3498db;
  text-decoration: none;
}

.footer a:hover {
  text-decoration: underline;
}

/* Mobile styles */
@media (max-width: 768px) {
  .welcome-view {
    padding: 20px 16px;
    justify-content: flex-start;
    padding-top: 40px;
  }

  h1 {
    font-size: 1.6em;
    margin-bottom: 16px;
  }

  p {
    font-size: 1em;
    margin-bottom: 30px;
  }

  .programme-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    max-width: 100%;
  }

  .programme-card {
    padding: 18px 16px;
  }

  .stats {
    flex-direction: column;
    gap: 20px;
    margin-top: 30px;
    width: 100%;
    max-width: 300px;
  }

  .stat-card {
    padding: 24px 30px;
  }

  .stat-number {
    font-size: 2.5em;
  }

  .stat-label {
    font-size: 1em;
  }

  .footer {
    margin-top: auto;
    padding-top: 40px;
    padding-bottom: 20px;
    font-size: 0.85em;
  }
}
</style>
