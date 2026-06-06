<template>
  <div class="patient-study-page">
    <!-- 患者列表 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <span>患者管理</span>
          <el-button type="primary" size="small" @click="showPatientDialog = true">
            <el-icon><Plus /></el-icon>
            新增患者
          </el-button>
        </div>
      </template>
      <el-form :inline="true" :model="patientFilters" class="filter-form">
        <el-form-item label="患者编码">
          <el-input v-model="patientFilters.patient_code" placeholder="输入编码" clearable />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="patientFilters.gender" placeholder="全部" clearable style="width: 120px">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPatients">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="patients" v-loading="patientLoading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="patient_code" label="患者编码" min-width="140" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="age_range" label="年龄段" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="selectPatient(row)">
              查看检查
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!patientLoading && patients.length === 0" description="暂无患者数据" />
    </el-card>

    <!-- 检查列表 -->
    <el-card v-if="selectedPatient" class="section-card">
      <template #header>
        <div class="card-header">
          <span>检查列表 - {{ selectedPatient.patient_code }}</span>
          <el-button type="primary" size="small" @click="showStudyDialog = true">
            <el-icon><Plus /></el-icon>
            新增检查
          </el-button>
        </div>
      </template>
      <el-table :data="studies" v-loading="studyLoading" stripe>
        <el-table-column prop="id" label="Study ID" width="80" />
        <el-table-column prop="description" label="检查说明" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="open3DView(row.id)">
              3D 展示
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!studyLoading && selectedPatient && studies.length === 0" description="暂无检查记录" />
    </el-card>

    <!-- 新增患者弹窗 -->
    <el-dialog v-model="showPatientDialog" title="新增患者" width="520px">
      <el-form ref="patientFormRef" :model="patientForm" :rules="patientRules" label-width="110px">
        <el-form-item label="患者编码" prop="patient_code">
          <el-input v-model="patientForm.patient_code" placeholder="请输入脱敏患者编码" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="patientForm.gender" style="width: 100%">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄段" prop="age_range">
          <el-input v-model="patientForm.age_range" placeholder="如 40-50（选填）" />
        </el-form-item>
        <el-form-item label="关联患者账号">
          <el-select
            v-model="patientForm.user_id"
            placeholder="选填，选择已注册的患者账号"
            clearable
            filterable
            style="width: 100%"
            @focus="fetchPatientAccounts"
          >
            <el-option
              v-for="acc in patientAccounts"
              :key="acc.id"
              :label="`${acc.username}${acc.linked ? '（已关联）' : '（未关联）'}`"
              :value="acc.id"
              :disabled="acc.linked"
            />
          </el-select>
          <div class="field-hint">选择后，该患者报告将自动同步到对应用户账号</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPatientDialog = false">取消</el-button>
        <el-button type="primary" :loading="patientSubmitting" @click="handleCreatePatient">创建</el-button>
      </template>
    </el-dialog>

    <!-- 新增检查弹窗 -->
    <el-dialog v-model="showStudyDialog" title="新增检查" width="480px">
      <el-form ref="studyFormRef" :model="studyForm" label-width="100px">
        <el-form-item label="检查说明" prop="description">
          <el-input v-model="studyForm.description" type="textarea" :rows="3" placeholder="请输入检查说明（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStudyDialog = false">取消</el-button>
        <el-button type="primary" :loading="studySubmitting" @click="handleCreateStudy">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getPatientList, createPatient, getPatientAccounts } from '@/api/patients'
import { createStudy, getStudiesByPatient } from '@/api/studies'
import type { Patient, Study, PatientFilters, CreatePatientRequest, PatientAccount, Gender } from '@/types'

const router = useRouter()

// ===== 患者列表 =====
const patients = ref<Patient[]>([])
const patientLoading = ref(false)
const patientFilters = reactive<PatientFilters>({ page: 1, page_size: 20 })

const showPatientDialog = ref(false)
const patientFormRef = ref<FormInstance>()
const patientSubmitting = ref(false)
const patientAccounts = ref<PatientAccount[]>([])

const patientForm = reactive<CreatePatientRequest>({
  patient_code: '',
  gender: 'unknown',
  user_id: undefined
})

async function fetchPatientAccounts() {
  if (patientAccounts.value.length > 0) return  // 已加载过则跳过
  try {
    const res = await getPatientAccounts()
    patientAccounts.value = res.data.data || []
  } catch { /* ignore */ }
}

const patientRules: FormRules = {
  patient_code: [
    { required: true, message: '请输入患者编码', trigger: 'blur' },
    { max: 64, message: '编码长度不超过64字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ]
}

async function fetchPatients() {
  patientLoading.value = true
  try {
    const res = await getPatientList(patientFilters)
    patients.value = res.data.data.items
  } catch { /* handled in interceptor */ }
  finally { patientLoading.value = false }
}

async function handleCreatePatient() {
  if (!patientFormRef.value) return
  const valid = await patientFormRef.value.validate().catch(() => false)
  if (!valid) return
  patientSubmitting.value = true
  try {
    await createPatient({
      patient_code: patientForm.patient_code,
      gender: patientForm.gender,
      age_range: patientForm.age_range || undefined,
      user_id: patientForm.user_id || undefined
    })
    ElMessage.success('患者创建成功')
    showPatientDialog.value = false
    patientForm.patient_code = ''
    patientForm.gender = 'unknown'
    patientForm.age_range = ''
    patientForm.user_id = undefined
    patientAccounts.value = []  // 下次打开重新加载
    fetchPatients()
  } catch { /* handled */ }
  finally { patientSubmitting.value = false }
}

// ===== 检查列表 =====
const selectedPatient = ref<Patient | null>(null)
const studies = ref<Study[]>([])
const studyLoading = ref(false)
const showStudyDialog = ref(false)
const studyFormRef = ref<FormInstance>()
const studySubmitting = ref(false)
const studyForm = reactive({ description: '' })

async function selectPatient(patient: Patient) {
  selectedPatient.value = patient
  await fetchStudies(patient.id)
}

async function fetchStudies(patientId: number) {
  studyLoading.value = true
  try {
    const res = await getStudiesByPatient(patientId)
    studies.value = res.data.data || []
  } catch {
    studies.value = []
  } finally {
    studyLoading.value = false
  }
}

async function handleCreateStudy() {
  if (!selectedPatient.value) return
  studySubmitting.value = true
  try {
    await createStudy(selectedPatient.value.id, {
      description: studyForm.description || undefined
    })
    ElMessage.success('检查创建成功')
    showStudyDialog.value = false
    studyForm.description = ''
    // 重新加载检查列表
    await fetchStudies(selectedPatient.value.id)
  } catch { /* handled */ }
  finally { studySubmitting.value = false }
}

function open3DView(studyId: number) {
  router.push(`/doctor/view3d/${studyId}`)
}

onMounted(() => {
  fetchPatients()
})
</script>

<style scoped>
.patient-study-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.section-card {
  width: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-form {
  margin-bottom: 16px;
}
</style>
