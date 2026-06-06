import request from './request'
import type { ApiResponse, PaginatedData, CtSlice, SliceFilters } from '@/types'

export function uploadSlice(studyId: number, file: File, sliceIndex: number) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('slice_index', String(sliceIndex))
  return request.post<ApiResponse<CtSlice>>(`/studies/${studyId}/slices`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getSliceList(params: SliceFilters) {
  return request.get<ApiResponse<PaginatedData<CtSlice>>>('/slices', { params })
}

export function getSliceDetail(sliceId: number) {
  return request.get<ApiResponse<CtSlice>>(`/slices/${sliceId}`)
}
