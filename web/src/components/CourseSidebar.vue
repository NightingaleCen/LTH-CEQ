<template>
  <div class="course-sidebar">
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search courses..."
        class="search-input"
      />
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
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseData } from '../composables/useCourseData.js'

const router = useRouter()
const route = useRoute()
const { getAllCourses } = useCourseData()
const searchQuery = ref('')

const filteredCourses = computed(() => {
  const courses = getAllCourses()
  if (!searchQuery.value) return courses
  
  const query = searchQuery.value.toLowerCase()
  return courses.filter(c => 
    c.course_code.toLowerCase().includes(query) ||
    c.name.toLowerCase().includes(query)
  )
})

const isActive = (code) => {
  return route.params.code === code || 
         route.params.code1 === code || 
         route.params.code2 === code
}

const selectCourse = (code) => {
  router.push(`/course/${code}`)
}
</script>

<style scoped>
.course-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
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
</style>
