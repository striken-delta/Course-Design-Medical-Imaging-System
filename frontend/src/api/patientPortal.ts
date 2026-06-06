import request from './request'
import type { ApiResponse, PatientReportSummary, PatientReportDetail, PatientProgress } from '@/types'

export function getPatientReports() {
  return request.get<ApiResponse<PatientReportSummary[]>>('/patient/reports')
}

export function getPatientReportDetail(predictionId: number) {
  return request.get<ApiResponse<PatientReportDetail>>(`/patient/reports/${predictionId}`)
}

export function getPatientProgress() {
  return request.get<ApiResponse<PatientProgress>>('/patient/progress')
}
