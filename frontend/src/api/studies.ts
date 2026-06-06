import request from './request'
import type { ApiResponse, Study, StudyDetail, CreateStudyRequest } from '@/types'

export function getStudiesByPatient(patientId: number) {
  return request.get<ApiResponse<Study[]>>(`/patients/${patientId}/studies`)
}

export function createStudy(patientId: number, data: CreateStudyRequest) {
  return request.post<ApiResponse<Study>>(`/patients/${patientId}/studies`, data)
}

export function getStudyDetail(studyId: number) {
  return request.get<ApiResponse<StudyDetail>>(`/studies/${studyId}`)
}
