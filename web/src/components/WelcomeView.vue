<template>
  <div class="welcome-view">
    <h1>Welcome to MMSR Course Stats</h1>
    <p>Select a course from the list on the left to view its evaluation data.</p>
    <div class="stats" v-if="courseData">
      <div class="stat-card">
        <div class="stat-number">{{ courseData.metadata.total_courses }}</div>
        <div class="stat-label">Courses</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ courseData.metadata.total_evaluations }}</div>
        <div class="stat-label">Evaluations</div>
      </div>
    </div>

    <footer class="footer">
      <p>All course and CEQ information comes from official LTH websites.</p>
      <a href="https://github.com/NightingaleCen/LTH-CEQ" target="_blank" rel="noopener">View on GitHub ↗</a>
    </footer>
  </div>
</template>

<script setup>
import { useCourseData } from '../composables/useCourseData.js'

const { courseData } = useCourseData()
</script>

<style scoped>
.welcome-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 40px;
  overflow: hidden;
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
  margin-top: 60px;
  padding-top: 30px;
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
</style>
