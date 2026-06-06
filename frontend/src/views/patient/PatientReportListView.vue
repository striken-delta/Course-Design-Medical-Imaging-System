<template>
  <div class="patient-reports-page">
    <h3 class="page-title">我的检查报告</h3>

    <div v-loading="loading">
      <el-empty v-if="!loading && reports.length === 0" description="暂无检查记录，请稍后查看">
        <el-button type="primary" @click="$router.push('/patient/progress')">查看检查进度</el-button>
      </el-empty>

      <div v-else class="report-cards">
        <div
          v-for="report in reports"
          :key="report.prediction_id"
          class="report-card"
          :class="'card-' + report.color_code"
          @click="goDetail(report.prediction_id)"
        >
          <div class="card-icon">
            <el-icon :size="32">
              <CircleCheckFilled v-if="report.color_code === 'green'" />
              <WarningFilled v-else-if="report.color_code === 'yellow'" />
              <CircleCloseFilled v-else />
            </el-icon>
          </div>
          <div class="card-body">
            <div class="card-date">
              <el-icon :size="14"><Clock /></el-icon>
              {{ report.study_date }}
            </div>
            <div class="card-summary">{{ report.summary }}</div>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPatientReports } from '@/api/patientPortal'
import type { PatientReportSummary } from '@/types'

const router = useRouter()
const reports = ref<PatientReportSummary[]>([])
const loading = ref(false)

async function fetchReports() {
  loading.value = true
  try {
    const res = await getPatientReports()
    reports.value = res.data.data || []
  } catch { /* handled */ }
  finally { loading.value = false }
}

function goDetail(predictionId: number) {
  router.push(`/patient/reports/${predictionId}`)
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.patient-reports-page {
  max-width: 700px;
  margin: 0 auto;
}
.page-title {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}
.report-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.report-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}
.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.card-green {
  background: #f0fdf4;
  border-color: #4ade80;
}
.card-yellow {
  background: #fefce8;
  border-color: #facc15;
}
.card-red {
  background: #fef2f2;
  border-color: #f87171;
}
.card-icon {
  flex-shrink: 0;
}
.card-green .card-icon { color: #22c55e; }
.card-yellow .card-icon { color: #eab308; }
.card-red .card-icon { color: #ef4444; }
.card-body {
  flex: 1;
}
.card-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}
.card-summary {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}
.card-arrow {
  color: #c0c4cc;
}
</style>
