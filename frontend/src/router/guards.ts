import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function setupGuards(router: Router) {
  router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore()

    // 不需要认证的页面直接放行
    if (!to.meta.requiresAuth) {
      // 已登录用户访问登录页，重定向到对应主页
      if (to.path === '/login' && authStore.isLoggedIn) {
        authStore.restoreUser()
        return next(getHomeRoute(authStore.role))
      }
      return next()
    }

    // 需要认证但没有 Token
    if (!authStore.isLoggedIn) {
      return next('/login')
    }

    // 有 Token 但用户信息未加载，尝试获取
    if (!authStore.user) {
      authStore.restoreUser()
      if (!authStore.user) {
        try {
          await authStore.fetchUser()
        } catch {
          authStore.logout()
          return next('/login')
        }
      }
    }

    // 角色校验
    const requiredRoles = to.meta.roles as string[] | undefined
    if (requiredRoles && authStore.role) {
      if (!requiredRoles.includes(authStore.role)) {
        // 角色不匹配，重定向到对应主页
        return next(getHomeRoute(authStore.role))
      }
    }

    next()
  })
}

function getHomeRoute(role: string | null): string {
  switch (role) {
    case 'admin':
      return '/admin/users'
    case 'doctor':
      return '/doctor/patients'
    case 'patient':
      return '/patient/reports'
    default:
      return '/login'
  }
}
