import request from './request'
import type { ApiResponse, View3DData } from '@/types'

export function getView3DData(studyId: number) {
  return request.get<ApiResponse<View3DData>>(`/view3d/studies/${studyId}`)
}
