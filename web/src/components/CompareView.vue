<template>
  <div class="compare-view" v-if="course1 && course2">
    <div class="header">
      <button @click="goBack" class="back-btn">← Back</button>
      <h1>Course Comparison</h1>
    </div>

    <div class="course-info">
      <div class="course-card" :style="{ borderColor: colors[0] }">
        <h2 :style="{ color: colors[0] }">{{ course1.course_code }}</h2>
        <p>{{ course1.name }}</p>
      </div>
      <div class="vs">VS</div>
      <div class="course-card" :style="{ borderColor: colors[1] }">
        <h2 :style="{ color: colors[1] }">{{ course2.course_code }}</h2>
        <p>{{ course2.name }}</p>
      </div>
    </div>

    <div class="latest-comparison" v-if="latestScores1 && latestScores2">
      <h2>Latest Scores Comparison</h2>
      <div class="comparison-table">
        <div class="table-header">
          <span>Metric</span>
          <span :style="{ color: colors[0] }">{{ course1.course_code }}</span>
          <span :style="{ color: colors[1] }">{{ course2.course_code }}</span>
          <span>Difference</span>
        </div>
        <div v-for="key in scoreKeys" :key="key" class="table-row">
          <span class="metric">{{ formatLabel(key) }}</span>
          <span>
            {{ latestScores1[key]?.score?.toFixed(2) || '-' }}
            <small class="std">(±{{ latestScores1[key]?.std?.toFixed(2) || '-' }})</small>
          </span>
          <span>
            {{ latestScores2[key]?.score?.toFixed(2) || '-' }}
            <small class="std">(±{{ latestScores2[key]?.std?.toFixed(2) || '-' }})</small>
          </span>
          <span :class="getDiffClass(latestScores1[key]?.score, latestScores2[key]?.score)">
            {{ getDiff(latestScores1[key]?.score, latestScores2[key]?.score) }}
          </span>
        </div>
      </div>
    </div>

    <footer class="footer">
      <p>All course and CEQ information comes from official LTH websites.</p>
      <a href="https://github.com/nightingalecen/LTH-CEQ" target="_blank" rel="noopener">View on GitHub ↗</a>
    </footer>
  </div>
  <div v-else-if="loading">Loading...</div>
  <div v-else>Courses not found</div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseData } from '../composables/useCourseData.js'

const props = defineProps({
  code1: { type: String, required: true },
  code2: { type: String, required: true }
})

const router = useRouter()
const { loading, getCourse } = useCourseData()

const colors = ['#3498db', '#e74c3c']
const scoreKeys = [
  'good_teaching',
  'clear_goals_and_standards',
  'appropriate_assessment',
  'appropriate_workload',
  'important_for_education',
  'overall_satisfaction'
]

const course1 = computed(() => getCourse(props.code1))
const course2 = computed(() => getCourse(props.code2))

const latestScores1 = computed(() => {
  if (!course1.value?.evaluations?.length) return null
  return course1.value.evaluations[0].scores
})

const latestScores2 = computed(() => {
  if (!course2.value?.evaluations?.length) return null
  return course2.value.evaluations[0].scores
})

const formatLabel = (key) => {
  const labels = {
    good_teaching: 'Good Teaching',
    clear_goals_and_standards: 'Clear Goals & Standards',
    appropriate_assessment: 'Appropriate Assessment',
    appropriate_workload: 'Appropriate Workload',
    important_for_education: 'Important for Education',
    overall_satisfaction: 'Overall Satisfaction'
  }
  return labels[key] || key
}

const getDiff = (val1, val2) => {
  if (val1 == null || val2 == null) return '-'
  const diff = val1 - val2
  return (diff > 0 ? '+' : '') + diff.toFixed(2)
}

const getDiffClass = (val1, val2) => {
  if (val1 == null || val2 == null) return ''
  const diff = val1 - val2
  return diff > 0 ? 'positive' : diff < 0 ? 'negative' : ''
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.compare-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  padding: 8px 16px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.back-btn:hover {
  background: #e0e0e0;
}

.course-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-bottom: 40px;
}

.course-card {
  flex: 1;
  max-width: 400px;
  padding: 20px;
  border: 3px solid;
  border-radius: 10px;
  text-align: center;
}

.course-card h2 {
  margin: 0 0 10px 0;
  font-size: 1.8em;
}

.course-card p {
  margin: 0;
  color: #666;
}

.vs {
  font-size: 1.5em;
  font-weight: bold;
  color: #999;
}

.latest-comparison {
  margin-top: 40px;
}

.comparison-table {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: minmax(200px, 2fr) 140px 140px 80px;
  gap: 15px;
  padding: 12px 15px;
  align-items: center;
}

.table-header span:nth-child(2),
.table-header span:nth-child(3),
.table-header span:nth-child(4),
.table-row span:nth-child(2),
.table-row span:nth-child(3),
.table-row span:nth-child(4) {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.table-header {
  background: #2c3e50;
  color: white;
  font-weight: bold;
  border-radius: 6px;
}

.table-row {
  background: #f8f9fa;
  border-radius: 6px;
}

.table-row:nth-child(even) {
  background: #e9ecef;
}

.metric {
  font-weight: 500;
}

.std {
  color: #888;
  font-size: 0.85em;
}

.positive {
  color: #27ae60;
  font-weight: bold;
}

.negative {
  color: #e74c3c;
  font-weight: bold;
}

/* Mobile styles */
@media (max-width: 768px) {
  .compare-view {
    padding: 16px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .header h1 {
    font-size: 1.4em;
    margin: 0;
  }

  .back-btn {
    min-height: 44px;
    padding: 10px 20px;
  }

  .course-info {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 30px;
  }

  .course-card {
    width: 100%;
    max-width: none;
    padding: 16px;
  }

  .course-card h2 {
    font-size: 1.4em;
  }

  .vs {
    font-size: 1.2em;
    padding: 8px 0;
  }

  .comparison-table {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .table-header {
    display: none;
  }

  .table-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 16px;
    padding: 16px;
  }

  .table-row .metric {
    grid-column: 1 / -1;
    font-weight: 600;
    font-size: 1em;
    margin-bottom: 4px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 8px;
  }

  .table-row span:nth-child(2),
  .table-row span:nth-child(3),
  .table-row span:nth-child(4) {
    text-align: left;
    font-size: 0.95em;
  }

  .table-row span:nth-child(2)::before {
    content: 'Course 1: ';
    font-weight: 500;
    font-size: 0.85em;
    color: #666;
    display: block;
    margin-bottom: 2px;
  }

  .table-row span:nth-child(3)::before {
    content: 'Course 2: ';
    font-weight: 500;
    font-size: 0.85em;
    color: #666;
    display: block;
    margin-bottom: 2px;
  }

  .table-row span:nth-child(4)::before {
    content: 'Diff: ';
    font-weight: 500;
    font-size: 0.85em;
    color: #666;
    display: block;
    margin-bottom: 2px;
  }
}

.footer {
  margin-top: 80px;
  padding-top: 30px;
  border-top: 1px solid #ddd;
  text-align: center;
  color: #888;
  font-size: 0.9em;
}

.footer p {
  margin: 0 0 10px 0;
}

.footer a {
  color: #3498db;
  text-decoration: none;
}

.footer a:hover {
  text-decoration: underline;
}
</style>
