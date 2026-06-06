import request from './request'
import type { ApiResponse, StatisticsData } from '@/types'

export function getStatisticsOverview(params?: { date_from?: string; date_to?: string }) {
  return request.get<ApiResponse<StatisticsData>>('/statistics/overview', { params })
}

export function getPositiveRateTrend(params?: { date_from?: string; date_to?: string }) {
  return request.get<ApiResponse<{ trend: { date: string; positive_rate: number }[] }>>('/statistics/positive-rate', { params })
}

export function getReviewConsistency(params?: { date_from?: string; date_to?: string }) {
  return request.get<ApiResponse<{ consistency_rate: number }>>('/statistics/review-consistency', { params })
}
