<template>
  <div class="patient-progress-page">
    <h3 class="page-title">检查进度</h3>

    <div v-loading="loading">
      <el-empty v-if="!loading && !progress" description="暂无检查记录" />

      <template v-if="progress">
        <!-- 当前状态 -->
        <el-card class="status-card">
          <template #header><span>当前状态</span></template>
          <el-steps :active="currentStep" finish-status="success" align-center>
            <el-step title="等待上传" description="切片上传中" />
            <el-step title="检测中" description="AI 正在分析" />
            <el-step title="结果已出" description="等待医生确认" />
            <el-step title="已复核" description="医生已确认结果" />
          </el-steps>
          <div class="current-status">
            <el-tag :type="statusType" size="large">
              {{ progress.status_label }}
            </el-tag>
            <p class="status-desc">{{ progress.description }}</p>
          </div>
        </el-card>

        <!-- 各检查进度 -->
        <el-card v-if="progress.studies && progress.studies.length > 0" class="studies-card">
          <template #header><span>各项检查详细进度</span></template>
          <el-table :data="progress.studies" stripe>
            <el-table-column prop="study_date" label="检查日期" width="120" />
            <el-table-column prop="status_label" label="状态" min-width="200" />
            <el-table-column prop="status" label="阶段" width="130">
              <template #default="{ row }">
                <el-tag :type="stepType(row.status)" size="small">
                  {{ stepLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getPatientProgress } from '@/api/patientPortal'
import type { PatientProgress } from '@/types'

const progress = ref<PatientProgress | null>(null)
const loading = ref(false)

const stepMap: Record<string, number> = {
  pending_upload: 0,
  processing: 1,
  result_ready: 2,
  reviewed: 3
}

const currentStep = computed(() => {
  if (!progress.value) return 0
  return stepMap[progress.value.status] || 0
})

const statusType = computed(() => {
  const map: Record<string, string> = {
    pending_upload: 'info',
    processing: 'warning',
    result_ready: '',
    reviewed: 'success'
  }
  return map[progress.value?.status || ''] || 'info'
})

function stepType(status: string) {
  const map: Record<string, string> = {
    pending_upload: 'info', processing: 'warning',
    result_ready: 'primary', reviewed: 'success'
  }
  return map[status] || 'info'
}

function stepLabel(status: string) {
  const map: Record<string, string> = {
    pending_upload: '等待上传', processing: '检测中',
    result_ready: '已出结果', reviewed: '已复核'
  }
  return map[status] || status
}

async function fetchProgress() {
  loading.value = true
  try {
    const res = await getPatientProgress()
    progress.value = res.data.data
  } catch { /* handled */ }
  finally { loading.value = false }
}

onMounted(() => {
  fetchProgress()
})
</script>

<style scoped>
.patient-progress-page {
  max-width: 700px;
  margin: 0 auto;
}
.page-title {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}
.status-card {
  margin-bottom: 20px;
}
.current-status {
  text-align: center;
  margin-top: 24px;
}
.status-desc {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
.studies-card {
  width: 100%;
}
</style>
