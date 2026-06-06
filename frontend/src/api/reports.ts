import request from './request'
import type { ApiResponse, PaginatedData, ReportItem, ReportDetail, ReportFilters } from '@/types'

export function searchReports(params: ReportFilters) {
  return request.get<ApiResponse<PaginatedData<ReportItem>>>('/reports', { params })
}

export function getReportDetail(predictionId: number) {
  return request.get<ApiResponse<ReportDetail>>(`/reports/${predictionId}`)
}
