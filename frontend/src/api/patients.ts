import request from './request'
import type { ApiResponse, PaginatedData, Patient, PatientAccount, CreatePatientRequest, PatientFilters } from '@/types'

export function getPatientList(params: PatientFilters) {
  return request.get<ApiResponse<PaginatedData<Patient>>>('/patients', { params })
}

export function getPatientAccounts() {
  return request.get<ApiResponse<PatientAccount[]>>('/patients/available-accounts')
}

export function createPatient(data: CreatePatientRequest) {
  return request.post<ApiResponse<Patient>>('/patients', data)
}
