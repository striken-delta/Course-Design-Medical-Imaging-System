// ==================== 枚举类型 ====================

export type UserRole = 'doctor' | 'admin' | 'patient'

export type Gender = 'male' | 'female' | 'unknown'

export type PredictionLabel = 'nodule' | 'non_nodule'

export type ReviewLabel = 'confirmed' | 'corrected'

export type ColorCode = 'green' | 'yellow' | 'red'

export type FileFormat = 'png' | 'jpg' | 'jpeg'

// ==================== API 响应格式 ====================

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  request_id?: string
}

export interface PaginatedData<T> {
  items: T[]
  page: number
  page_size: number
  total: number
}

// ==================== 数据实体 ====================

export interface User {
  id: number
  username: string
  role: UserRole
  patient_id?: number
  is_active: boolean
  created_at: string
}

export interface Patient {
  id: number
  patient_code: string
  gender: Gender
  age_range?: string
  created_at: string
  created_by: number
}

export interface Study {
  id: number
  patient_id: number
  description?: string
  created_at: string
  created_by: number
}

export interface StudyDetail extends Study {
  patient?: Patient
  slice_count?: number
  latest_prediction?: Prediction
}

export interface CtSlice {
  id: number
  study_id: number
  slice_index: number
  file_path: string
  file_format: FileFormat
  file_size: number
  uploaded_at: string
  uploaded_by: number
}

export interface Prediction {
  id: number
  slice_id: number
  label: PredictionLabel
  confidence: number
  model_version: string
  inference_time_ms: number
  heatmap_path?: string
  created_at: string
}

/** 复核记录 */
export interface Review {
  id: number
  prediction_id: number
  review_label: ReviewLabel
  /** 纠正后的标签，仅 review_label=corrected 时有值 */
  corrected_label?: string
  comment?: string
  reviewed_by: number
  reviewed_at: string
  reviewed_by_name?: string
}

export interface Lung3DMarker {
  id: number
  study_id: number
  slice_id?: number
  x: number
  y: number
  z: number
  confidence: number
  label?: PredictionLabel
  created_at: string
}

export interface AuditLog {
  id: number
  user_id: number
  action: string
  target_type?: string
  target_id?: number
  detail?: string
  created_at: string
  username?: string
}

// ==================== 登录相关 ====================

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  patient_code?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// ==================== 请求参数 ====================

export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PatientFilters extends PaginationParams {
  patient_code?: string
  gender?: Gender
}

export interface SliceFilters extends PaginationParams {
  study_id?: number
  patient_code?: string
  date_from?: string
  date_to?: string
}

export interface ReportFilters extends PaginationParams {
  patient_code?: string
  date_from?: string
  date_to?: string
  label?: PredictionLabel
  review_status?: 'unreviewed' | 'reviewed'
}

export interface AuditFilters extends PaginationParams {
  user_id?: number
  action?: string
  date_from?: string
  date_to?: string
}

// ==================== 请求体 ====================

export interface CreateUserRequest {
  username: string
  password: string
  role: UserRole
  patient_id?: number
}

export interface UpdateUserRequest {
  role?: UserRole
  is_active?: boolean
}

export interface PatientAccount {
  id: number
  username: string
  patient_id: number | null
  linked: boolean
}

export interface CreatePatientRequest {
  patient_code: string
  gender: Gender
  age_range?: string
  user_id?: number
}

export interface CreateStudyRequest {
  description?: string
}

export interface UploadSliceRequest {
  file: File
  slice_index: number
}

/** 提交复核请求体 */
export interface SubmitReviewRequest {
  prediction_id: number
  review_label: ReviewLabel
  /** 纠正后的标签，仅 review_label=corrected 时必填 */
  corrected_label?: string
  comment?: string
}

// ==================== 报告相关 ====================

export interface ReportItem {
  prediction_id: number
  patient_code: string
  patient_id: number
  gender: Gender
  age_range?: string
  study_id: number
  slice_id: number
  slice_index: number
  slice_file_path: string
  label: PredictionLabel
  confidence: number
  model_version: string
  inference_time_ms: number
  heatmap_path?: string
  review_status: string
  review_label?: ReviewLabel
  /** 纠正后的标签，仅 review_label=corrected 时有值 */
  corrected_label?: string
  created_at: string
}

export interface ReportDetail {
  prediction: Prediction
  slice: CtSlice
  study: Study
  patient: Patient
  latest_review?: Review
  review_history: Review[]
  markers_summary?: Lung3DMarker[]
}

// ==================== 统计相关 ====================

export interface StatisticsOverview {
  upload_count: number
  inference_count: number
  review_count: number
  positive_rate: number
  consistency_rate: number
}

export interface TrendItem {
  date: string
  upload_count: number
  positive_rate: number
}

export interface StatisticsData {
  overview: StatisticsOverview
  trend: TrendItem[]
}

// ==================== 患者端 ====================

export interface PatientReportSummary {
  prediction_id: number
  study_id: number
  study_date: string
  label: PredictionLabel
  confidence: number
  review_status: string
  summary: string
  color_code: ColorCode
  icon: string
}

export interface PatientReportDetail {
  prediction_id: number
  study_id: number
  summary: string
  color_code: ColorCode
  icon: string
  explanation?: string
  term_definitions?: { term: string; explanation: string }[]
  has_3d: boolean
  study_id_for_3d?: number
  slice_preview_url?: string
}

export interface PatientProgress {
  status: 'pending_upload' | 'processing' | 'result_ready' | 'reviewed'
  status_label: string
  description: string
  studies: {
    study_id: number
    study_date: string
    status: string
    status_label: string
  }[]
}

// ==================== 3D 相关 ====================

export interface View3DData {
  study_id: number
  model_url: string
  markers: Lung3DMarker[]
}

// ==================== 用户管理 ====================

export interface UserListParams extends PaginationParams {
  role?: UserRole
  keyword?: string
}
