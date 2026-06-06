import request from './request'
import type { ApiResponse, PaginatedData, User, CreateUserRequest, UpdateUserRequest, UserListParams } from '@/types'

export function getUserList(params: UserListParams) {
  return request.get<ApiResponse<PaginatedData<User>>>('/users', { params })
}

export function createUser(data: CreateUserRequest) {
  return request.post<ApiResponse<User>>('/users', data)
}

export function updateUser(userId: number, data: UpdateUserRequest) {
  return request.patch<ApiResponse<User>>(`/users/${userId}`, data)
}
