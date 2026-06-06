import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserRole, LoginRequest } from '@/types'
import { login as loginApi, getCurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  const role = computed<UserRole | null>(() => user.value?.role || null)

  const isDoctor = computed(() => role.value === 'doctor' || role.value === 'admin')
  const isAdmin = computed(() => role.value === 'admin')
  const isPatient = computed(() => role.value === 'patient')

  async function login(credentials: LoginRequest) {
    loading.value = true
    try {
      const res = await loginApi(credentials)
      const data = res.data.data
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data.user
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return null
    try {
      const res = await getCurrentUser()
      user.value = res.data.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return user.value
    } catch {
      logout()
      return null
    }
  }

  function restoreUser() {
    const saved = localStorage.getItem('user')
    if (saved) {
      try {
        user.value = JSON.parse(saved)
      } catch {
        // ignore parse error
      }
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    role,
    isDoctor,
    isAdmin,
    isPatient,
    login,
    fetchUser,
    restoreUser,
    logout
  }
})
