import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  // ========== 医生端 ==========
  {
    path: '/doctor',
    component: () => import('@/layouts/DoctorLayout.vue'),
    meta: { requiresAuth: true, roles: ['doctor', 'admin'] },
    children: [
      {
        path: '',
        redirect: '/doctor/patients'
      },
      {
        path: 'patients',
        name: 'DoctorPatients',
        component: () => import('@/views/doctor/PatientStudyView.vue')
      },
      {
        path: 'slices',
        name: 'DoctorSlices',
        component: () => import('@/views/doctor/SliceUploadView.vue')
      },
      {
        path: 'reports',
        name: 'DoctorReports',
        component: () => import('@/views/doctor/ReportListView.vue')
      },
      {
        path: 'reports/:id',
        name: 'DoctorReportDetail',
        component: () => import('@/views/doctor/ReportDetailView.vue')
      },
      {
        path: 'statistics',
        name: 'DoctorStatistics',
        component: () => import('@/views/doctor/StatisticsView.vue')
      },
      {
        path: 'view3d/:studyId',
        name: 'DoctorView3D',
        component: () => import('@/views/doctor/View3DView.vue')
      }
    ]
  },
  // ========== 管理员端 ==========
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      {
        path: '',
        redirect: '/admin/users'
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManageView.vue')
      },
      {
        path: 'audit',
        name: 'AdminAudit',
        component: () => import('@/views/admin/AuditLogView.vue')
      },
      {
        path: 'statistics',
        name: 'AdminStatistics',
        component: () => import('@/views/doctor/StatisticsView.vue')
      }
    ]
  },
  // ========== 患者端 ==========
  {
    path: '/patient',
    component: () => import('@/layouts/PatientLayout.vue'),
    meta: { requiresAuth: true, roles: ['patient'] },
    children: [
      {
        path: '',
        redirect: '/patient/reports'
      },
      {
        path: 'reports',
        name: 'PatientReports',
        component: () => import('@/views/patient/PatientReportListView.vue')
      },
      {
        path: 'reports/:id',
        name: 'PatientReportDetail',
        component: () => import('@/views/patient/PatientReportDetailView.vue')
      },
      {
        path: 'progress',
        name: 'PatientProgress',
        component: () => import('@/views/patient/PatientProgressView.vue')
      },
      {
        path: 'view3d/:studyId',
        name: 'PatientView3D',
        component: () => import('@/views/patient/Patient3DView.vue')
      }
    ]
  },
  // ========== 404 ==========
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
