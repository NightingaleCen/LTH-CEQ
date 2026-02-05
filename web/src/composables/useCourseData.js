import { ref, onMounted } from 'vue'

const courseData = ref(null)
const loading = ref(true)
const error = ref(null)

export function useCourseData() {
  onMounted(async () => {
    if (courseData.value) return
    
    try {
      const response = await fetch('/courses_data.json')
      if (!response.ok) throw new Error('Failed to load course data')
      const data = await response.json()
      courseData.value = data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  })

  const getCourse = (code) => {
    if (!courseData.value) return null
    return courseData.value.courses.find(c => c.course_code === code)
  }

  const getAllCourses = () => {
    if (!courseData.value) return []
    return courseData.value.courses
  }

  return {
    courseData,
    loading,
    error,
    getCourse,
    getAllCourses
  }
}
