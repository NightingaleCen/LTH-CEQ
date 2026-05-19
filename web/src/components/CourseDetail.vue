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
      <div class="autocomplete-wrapper">
        <input
          v-model="compareSearchQuery"
          type="text"
          class="compare-input"
          :placeholder="`Search ${programmeCode} courses...`"
          @focus="compareDropdownOpen = true"
          @blur="onCompareBlur"
          @keydown="onCompareKeydown"
        />
        <div v-if="compareDropdownOpen && filteredCompareOptions.length" class="compare-dropdown">
          <div
            v-for="(c, idx) in filteredCompareOptions"
            :key="c.course_code"
            class="compare-option"
            :class="{ highlighted: idx === compareHighlightIndex }"
            @mousedown.prevent="selectCompareCourse(c.course_code, `${c.course_code} - ${c.name}`)"
          >
            <span class="compare-option-code">{{ c.course_code }}</span>
            <span class="compare-option-name">{{ c.name }}</span>
          </div>
        </div>
      </div>
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
import { computed, ref, watch } from 'vue'
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
const compareSearchQuery = ref('')
const compareDropdownOpen = ref(false)
const compareHighlightIndex = ref(-1)

const course = computed(() => getCourse(props.code))

const latestEvaluation = computed(() => {
  if (!course.value || !course.value.evaluations.length) return null
  return course.value.evaluations[0]
})

const otherCourses = computed(() => {
  return getProgrammeCourses(props.programmeCode).filter(c => c.course_code !== props.code)
})

const filteredCompareOptions = computed(() => {
  const query = compareSearchQuery.value.toLowerCase()
  if (!query) return otherCourses.value
  return otherCourses.value.filter(c =>
    c.course_code.toLowerCase().includes(query) ||
    c.name.toLowerCase().includes(query)
  )
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

const selectCompareCourse = (code, label) => {
  compareSearchQuery.value = label
  compareDropdownOpen.value = false
  router.push(`/programme/${props.programmeCode}/compare/${props.code}/${code}`)
}

const onCompareBlur = () => {
  setTimeout(() => {
    compareDropdownOpen.value = false
    compareHighlightIndex.value = -1
  }, 150)
}

const onCompareKeydown = (e) => {
  if (!compareDropdownOpen.value) {
    if (e.key === 'ArrowDown') {
      compareDropdownOpen.value = true
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    compareHighlightIndex.value = Math.min(compareHighlightIndex.value + 1, filteredCompareOptions.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    compareHighlightIndex.value = Math.max(compareHighlightIndex.value - 1, 0)
  } else if (e.key === 'Enter' && compareHighlightIndex.value >= 0) {
    e.preventDefault()
    const c = filteredCompareOptions.value[compareHighlightIndex.value]
    selectCompareCourse(c.course_code, `${c.course_code} - ${c.name}`)
  } else if (e.key === 'Escape') {
    compareDropdownOpen.value = false
    compareHighlightIndex.value = -1
  }
}

watch(compareSearchQuery, () => {
  compareHighlightIndex.value = -1
  compareDropdownOpen.value = true
})
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

.autocomplete-wrapper {
  position: relative;
  margin-top: 10px;
}

.compare-input {
  width: 100%;
  padding: 10px 12px;
  font-size: 1em;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  min-height: 44px;
}

.compare-input:focus {
  border-color: #3498db;
}

.compare-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 240px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 6px 6px;
  z-index: 100;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.compare-option {
  padding: 10px 12px;
  cursor: pointer;
  display: flex;
  gap: 10px;
  align-items: baseline;
}

.compare-option:hover,
.compare-option.highlighted {
  background-color: #e3f2fd;
}

.compare-option-code {
  font-weight: 600;
  font-size: 13px;
  color: #2c3e50;
  flex-shrink: 0;
}

.compare-option-name {
  font-size: 13px;
  color: #666;
  line-height: 1.3;
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

  .chart-section h2 {
    font-size: 1.3em;
  }

  .chart-section {
    margin: 30px 0 60px 0;
  }
}
</style>
