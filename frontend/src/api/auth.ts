import request from './request'
import type { ApiResponse, LoginRequest, LoginResponse, RegisterRequest, User } from '@/types'

export function login(data: LoginRequest) {
  return request.post<ApiResponse<LoginResponse>>('/auth/login', data)
}

export function register(data: RegisterRequest) {
  return request.post<ApiResponse<User>>('/auth/register', data)
}

export function getCurrentUser() {
  return request.get<ApiResponse<User>>('/auth/me')
}
