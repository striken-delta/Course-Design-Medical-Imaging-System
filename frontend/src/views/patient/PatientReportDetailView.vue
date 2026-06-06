<template>
  <div class="patient-detail-page">
    <el-page-header @back="$router.back()" title="返回列表">
      <template #content>
        <span>报告详情</span>
      </template>
    </el-page-header>

    <div v-loading="loading" class="detail-content">
      <el-empty v-if="!loading && !detail" description="报告不存在" />

      <template v-if="detail">
        <!-- 结果摘要卡片 -->
        <PatientSummaryCard
          :summary="detail.summary"
          :color-code="detail.color_code"
          :explanation="detail.explanation"
          :term-definitions="detail.term_definitions"
          :title="detail.color_code === 'green' ? '检查结果正常' : detail.color_code === 'yellow' ? '检查结果待确认' : '检查发现异常'"
        />

        <!-- 切片图像（如果有） -->
        <el-card v-if="detail.slice_preview_url" class="detail-card">
          <template #header><span>检查图像</span></template>
          <SlicePreview :src="detail.slice_preview_url" />
        </el-card>

        <!-- 3D 展示入口 -->
        <el-card v-if="detail.has_3d && detail.study_id_for_3d" class="detail-card">
          <template #header><span>三维查看</span></template>
          <div class="three-d-entry">
            <p>您可以通过下面按钮查看本次检查的三维肺部展示。</p>
            <el-button type="primary" @click="$router.push(`/patient/view3d/${detail.study_id_for_3d}`)">
              <el-icon><View /></el-icon>
              查看 3D 肺部展示
            </el-button>
          </div>
        </el-card>

        <!-- 医生提示 -->
        <el-card class="detail-card notice-card">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> 温馨提示</span>
          </template>
          <p>
            以上检查结果由人工智能辅助分析生成，仅供您参考，不构成任何医疗诊断意见。
            如有疑问，请及时咨询您的医生。医生会根据您的具体情况提供专业的诊疗建议。
          </p>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPatientReportDetail } from '@/api/patientPortal'
import PatientSummaryCard from '@/components/PatientSummaryCard.vue'
import SlicePreview from '@/components/SlicePreview.vue'
import type { PatientReportDetail } from '@/types'

const route = useRoute()
const predictionId = Number(route.params.id)

const detail = ref<PatientReportDetail | null>(null)
const loading = ref(false)

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getPatientReportDetail(predictionId)
    detail.value = res.data.data
  } catch { /* handled */ }
  finally { loading.value = false }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.patient-detail-page {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-card {
  width: 100%;
}
.three-d-entry {
  text-align: center;
  padding: 16px 0;
}
.three-d-entry p {
  margin-bottom: 12px;
  color: #606266;
}
.notice-card {
  background: #f0f9ff;
  border-color: #bae6fd;
}
.notice-card p {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}
</style>
