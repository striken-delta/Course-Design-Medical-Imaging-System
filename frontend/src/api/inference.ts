import request from './request'
import type { ApiResponse, Prediction } from '@/types'

export function triggerInference(sliceId: number) {
  return request.post<ApiResponse<Prediction>>(`/inference/${sliceId}`)
}
