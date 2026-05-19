<template>
  <div class="course-sidebar">
    <div v-if="!programmeCode" class="no-programme">
      Select a programme to view courses
    </div>
    <template v-else>
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          :placeholder="searchPlaceholder"
          class="search-input"
        />
      </div>
      <div class="period-filter">
        <button
          v-for="p in periods"
          :key="p.value"
          class="period-chip"
          :class="{ active: selectedPeriod === p.value }"
          @click="selectedPeriod = p.value"
        >{{ p.label }}</button>
      </div>
      <div class="course-list" v-if="filteredCourses.length">
        <div 
          v-for="course in filteredCourses" 
          :key="course.course_code"
          class="course-item"
          :class="{ active: isActive(course.course_code) }"
          @click="selectCourse(course.course_code)"
        >
          <div class="course-code">{{ course.course_code }}</div>
          <div class="course-name">{{ course.name }}</div>
        </div>
      </div>
      <div v-else class="no-results">
        No courses found
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseData } from '../composables/useCourseData.js'

const props = defineProps({
  programmeCode: {
    type: String,
    default: '',
  },
})

const router = useRouter()
const route = useRoute()
const { getProgrammeCourses } = useCourseData()
const searchQuery = ref('')
const selectedPeriod = ref(0)

const periods = [
  { label: 'All', value: 0 },
  { label: 'LP1', value: 1 },
  { label: 'LP2', value: 2 },
  { label: 'LP3', value: 3 },
  { label: 'LP4', value: 4 },
]

const searchPlaceholder = computed(() =>
  `Search ${props.programmeCode} courses...`
)

const emit = defineEmits(['course-selected'])

const courses = computed(() => getProgrammeCourses(props.programmeCode))

const filteredCourses = computed(() => {
  let result = courses.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.course_code.toLowerCase().includes(query) ||
      c.name.toLowerCase().includes(query)
    )
  }

  if (selectedPeriod.value > 0) {
    const period = selectedPeriod.value
    result = result.filter(c =>
      (c.offerings || []).some(o => o.start_period <= period && period <= o.end_period)
    )
  }

  return result
})

const isActive = (code) => {
  return route.params.code === code || 
         route.params.code1 === code || 
         route.params.code2 === code
}

const selectCourse = (code) => {
  router.push(`/programme/${props.programmeCode}/course/${code}`)
  emit('course-selected')
}
</script>

<style scoped>
.course-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.no-programme {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.search-box {
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}

.search-input:focus {
  border-color: #3498db;
}

.period-filter {
  display: flex;
  gap: 6px;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
}

.period-chip {
  flex: 1;
  text-align: center;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #ddd;
  border-radius: 14px;
  background: white;
  color: #666;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}

.period-chip:hover {
  background: #f0f7ff;
  border-color: #3498db;
  color: #3498db;
}

.period-chip.active {
  background: #3498db;
  border-color: #3498db;
  color: white;
}

.course-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.course-item {
  padding: 12px 15px;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: background-color 0.2s;
}

.course-item:hover {
  background-color: #f0f7ff;
}

.course-item.active {
  background-color: #e3f2fd;
  border-left-color: #3498db;
}

.course-code {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 2px;
}

.course-name {
  font-size: 13px;
  color: #666;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.no-results {
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* Mobile styles */
@media (max-width: 768px) {
  .search-box {
    padding: 20px;
  }

  .search-input {
    padding: 12px 16px;
    font-size: 16px;
    min-height: 44px;
  }

  .course-item {
    padding: 16px 20px;
    min-height: 44px;
  }

  .course-code {
    font-size: 15px;
  }

  .course-name {
    font-size: 14px;
  }
}
</style>
