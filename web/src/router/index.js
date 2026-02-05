import { createRouter, createWebHistory } from 'vue-router'
import CourseDetail from '../components/CourseDetail.vue'
import CompareView from '../components/CompareView.vue'
import WelcomeView from '../components/WelcomeView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: WelcomeView
  },
  {
    path: '/course/:code',
    name: 'CourseDetail',
    component: CourseDetail,
    props: true
  },
  {
    path: '/compare/:code1/:code2',
    name: 'Compare',
    component: CompareView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
