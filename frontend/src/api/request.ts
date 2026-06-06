import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

const instance: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动携带 JWT Token
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一错误处理
instance.interceptors.response.use(
  (response) => {
    const data = response.data as ApiResponse
    // 业务成功
    if (data.code === 0) {
      return response
    }
    // 业务错误
    ElMessage.error(data.message || '请求失败')
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  (error: AxiosError<ApiResponse>) => {
    const status = error.response?.status
    const respData: any = error.response?.data
    const message = respData?.message || respData?.detail?.message || respData?.detail || error.message

    switch (status) {
      case 401:
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        ElMessage.error('登录已过期，请重新登录')
        // 跳转登录页（避免重复跳转）
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        break
      case 403:
        ElMessage.error('无权限访问该资源')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error('服务器内部错误，请稍后重试')
        break
      default:
        ElMessage.error(message || '网络异常，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default instance
