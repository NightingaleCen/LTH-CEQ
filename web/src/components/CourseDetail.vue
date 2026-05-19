<template>
  <div class="course-detail" v-if="course">
    <div class="header">
      <router-link :to="`/programme/${programmeCode}`" class="back-link">← Back to {{ programmeCode }}</router-link>
      <h1>{{ course.course_code }} - {{ course.name }}</h1>
    </div>

    <div class="info">
      <p><strong>Credits:</strong> {{ course.credits }} | <strong>Grading:</strong> {{ course.grading_scale }} | <a
          :href="course.course_syllabus_url" target="_blank" rel="noopener">Course Syllabus ↗</a> | <a
          :href="course.course_evaluation_archive_url" target="_blank" rel="noopener">Evaluation Archive ↗</a></p>
    </div>

    <div class="latest-scores" v-if="latestEvaluation">
      <h2>Latest CEQ Scores ({{ latestEvaluation.academic_year }} {{ latestEvaluation.semester }} {{
        latestEvaluation.period }})</h2>
      <p class="score-note">Values show mean ± standard deviation</p>
      <div class="scores-grid">
        <div v-for="(value, key) in latestEvaluation.scores" :key="key" class="score-item">
          <span class="score-label">{{ formatLabel(key) }}</span>
          <span class="score-value">{{ value.score.toFixed(2) }}</span>
          <span class="score-std">±{{ value.std.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <div class="compare-section">
      <h2>Compare with Another Course</h2>
      <select v-model="compareCourse" @change="goToCompare">
        <option value="">Select a course...</option>
        <option v-for="c in otherCourses" :key="c.course_code" :value="c.course_code">
          {{ c.course_code }} - {{ c.name }}
        </option>
      </select>
    </div>

    <div class="chart-section">
      <h2>Historical Trends</h2>
      <TrendChart :evaluations="course.evaluations" />
    </div>

    <footer class="footer">
      <p>All course and CEQ information comes from official LTH websites.</p>
      <a href="https://github.com/nightingalecen/LTH-CEQ" target="_blank" rel="noopener">View on GitHub ↗</a>
    </footer>
  </div>
  <div v-else-if="loading">Loading...</div>
  <div v-else>Course not found</div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseData } from '../composables/useCourseData.js'
import TrendChart from './TrendChart.vue'

const props = defineProps({
  programmeCode: {
    type: String,
    required: true,
  },
  code: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const { loading, getCourse, getProgrammeCourses } = useCourseData()
const compareCourse = ref('')

const course = computed(() => getCourse(props.code))

const latestEvaluation = computed(() => {
  if (!course.value || !course.value.evaluations.length) return null
  return course.value.evaluations[0]
})

const otherCourses = computed(() => {
  return getProgrammeCourses(props.programmeCode).filter(c => c.course_code !== props.code)
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

const goToCompare = () => {
  if (compareCourse.value) {
    router.push(`/programme/${props.programmeCode}/compare/${props.code}/${compareCourse.value}`)
  }
}
</script>

<style scoped>
.course-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  margin: 10px 0 0 0;
}

.back-link {
  display: inline-block;
  color: #666;
  font-size: 0.9em;
  margin-bottom: 8px;
}

.back-link:hover {
  color: #3498db;
}

.latest-scores {
  margin: 30px 0;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
  margin-top: 15px;
}

.score-item {
  display: grid;
  grid-template-columns: 1fr 70px 70px;
  align-items: center;
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 6px;
  gap: 10px;
}

.score-label {
  font-weight: 500;
}

.score-value {
  font-size: 1.2em;
  font-weight: bold;
  color: #2c3e50;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.score-std {
  color: #666;
  font-size: 0.9em;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.score-note {
  color: #888;
  font-size: 0.9em;
  margin: -10px 0 15px 0;
  font-style: italic;
}

.chart-section {
  margin: 40px 0 80px 0;
}

.links {
  margin-top: 15px;
  display: flex;
  gap: 20px;
}

.links a {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
}

.links a:hover {
  text-decoration: underline;
}

.compare-section {
  margin: 40px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.compare-section select {
  width: 100%;
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 10px;
  min-height: 44px;
}

.footer {
  margin-top: 60px;
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

/* Mobile styles */
@media (max-width: 768px) {
  .course-detail {
    padding: 16px;
  }

  .header h1 {
    font-size: 1.4em;
    line-height: 1.3;
  }

  .info p {
    font-size: 0.9em;
    line-height: 1.6;
  }

  .scores-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .score-item {
    padding: 16px;
    grid-template-columns: 1fr auto auto;
    gap: 8px;
  }

  .score-label {
    font-size: 0.95em;
  }

  .score-value {
    font-size: 1.1em;
  }

  .compare-section {
    padding: 16px;
  }

  .compare-section select {
    padding: 12px;
    font-size: 16px;
  }

  .chart-section h2 {
    font-size: 1.3em;
  }

  .chart-section {
    margin: 30px 0 60px 0;
  }
}
</style>
