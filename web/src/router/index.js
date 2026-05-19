import { createRouter, createWebHistory } from 'vue-router'
import CourseDetail from '../components/CourseDetail.vue'
import CompareView from '../components/CompareView.vue'
import WelcomeView from '../components/WelcomeView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: WelcomeView,
  },
  {
    path: '/programme/:programmeCode',
    name: 'ProgrammeHome',
    component: WelcomeView,
    props: true,
  },
  {
    path: '/programme/:programmeCode/course/:code',
    name: 'CourseDetail',
    component: CourseDetail,
    props: true,
  },
  {
    path: '/programme/:programmeCode/compare/:code1/:code2',
    name: 'Compare',
    component: CompareView,
    props: true,
  },
  // legacy redirects
  {
    path: '/course/:code',
    redirect: (to) => `/programme/MMSR/course/${to.params.code}`,
  },
  {
    path: '/compare/:code1/:code2',
    redirect: (to) => `/programme/MMSR/compare/${to.params.code1}/${to.params.code2}`,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
