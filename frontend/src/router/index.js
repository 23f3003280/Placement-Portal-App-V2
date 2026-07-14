import { createRouter, createWebHistory } from 'vue-router'

import LandingView from '../views/LandingView.vue'
import AdminView from '../views/AdminView.vue'
import UserView from '../views/UserView.vue'
import StudentDashboard from '../components/StudentDashboard.vue'
import StudentHistory from '../components/StudentHistory.vue'
import StudentProfile from '../components/StudentProfile.vue'
import CompanyDashboard from '../components/CompanyDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView,
    },
    
    
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
    },
    {
      path: '/user',
      component: UserView,
      children: [
        {
          path: '',
          name: 'student-dashboard',
          component: StudentDashboard,
        },
        {
          path: 'history',
          name: 'student-history',
          component: StudentHistory,
        },
        {
          path: 'profile',
          name: 'student-profile',
          component: StudentProfile,
        },
        {
          path: 'company',
          name: 'company-dashboard',
          component: CompanyDashboard,
        },
        {
          path: 'company-profile',
          name: 'company-profile',
          component: () => import('../components/CompanyProfile.vue')
        }
      ],
    },
  ],
})

export default router
