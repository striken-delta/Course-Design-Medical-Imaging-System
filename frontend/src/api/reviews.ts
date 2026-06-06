import request from './request'
import type { ApiResponse, Review, SubmitReviewRequest } from '@/types'

export function submitReview(data: SubmitReviewRequest) {
  return request.post<ApiResponse<Review>>('/reviews', data)
}
