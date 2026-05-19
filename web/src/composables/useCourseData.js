import { ref, computed, onMounted } from 'vue'

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

  const programmes = computed(() => {
    if (!courseData.value?.programs) return []
    return Object.entries(courseData.value.programs)
      .map(([code, info]) => ({
        code,
        name_en: info.name_en,
        name_sv: info.name_sv,
        course_count: info.course_codes.length,
      }))
      .sort((a, b) => a.code.localeCompare(b.code))
  })

  const getCourse = (code) => {
    if (!courseData.value) return null
    return courseData.value.courses.find(c => c.course_code === code)
  }

  const getAllCourses = () => {
    if (!courseData.value) return []
    return courseData.value.courses
  }

  const getProgrammeCourses = (programmeCode) => {
    if (!courseData.value?.programs?.[programmeCode]) return []
    const codes = courseData.value.programs[programmeCode].course_codes
    return (courseData.value.courses || []).filter(c => codes.includes(c.course_code))
  }

  const getProgrammeMetadata = (programmeCode) => {
    const courses = getProgrammeCourses(programmeCode)
    let totalEvaluations = 0
    courses.forEach(c => {
      totalEvaluations += c.evaluations?.length || 0
    })
    return {
      total_courses: courses.length,
      total_evaluations: totalEvaluations,
    }
  }

  return {
    courseData,
    loading,
    error,
    programmes,
    getCourse,
    getAllCourses,
    getProgrammeCourses,
    getProgrammeMetadata,
  }
}
