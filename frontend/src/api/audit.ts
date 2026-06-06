import request from './request'
import type { ApiResponse, PaginatedData, AuditLog, AuditFilters } from '@/types'

export function getAuditLogs(params: AuditFilters) {
  return request.get<ApiResponse<PaginatedData<AuditLog>>>('/audit/logs', { params })
}
