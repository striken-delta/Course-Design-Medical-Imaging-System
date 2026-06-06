<template>
  <div class="report-detail-page">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span>报告详情 #{{ predictionId }}</span>
      </template>
    </el-page-header>

    <div v-loading="loading" class="detail-content">
      <el-empty v-if="!loading && !detail" description="报告不存在" />

      <template v-if="detail">
        <!-- 患者信息 -->
        <el-card class="detail-card">
          <template #header><span>患者信息</span></template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="患者编码">{{ detail.patient.patient_code }}</el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ detail.patient.gender === 'male' ? '男' : detail.patient.gender === 'female' ? '女' : '未知' }}
            </el-descriptions-item>
            <el-descriptions-item label="年龄段">{{ detail.patient.age_range || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 检查信息 -->
        <el-card class="detail-card">
          <template #header><span>检查信息</span></template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Study ID">{{ detail.study.id }}</el-descriptions-item>
            <el-descriptions-item label="检查说明">{{ detail.study.description || '-' }}</el-descriptions-item>
            <el-descriptions-item label="切片序号">{{ detail.slice.slice_index }}</el-descriptions-item>
            <el-descriptions-item label="切片格式">{{ detail.slice.file_format?.toUpperCase() }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 切片预览 -->
        <el-card class="detail-card">
          <template #header><span>切片图像</span></template>
          <SlicePreview :src="detail.slice.file_path" :info="{ slice_index: detail.slice.slice_index, file_format: detail.slice.file_format }" />
        </el-card>

        <!-- 预测结果 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>预测结果</span>
              <el-tag :type="detail.prediction.label === 'nodule' ? 'danger' : 'success'">
                {{ detail.prediction.label === 'nodule' ? '疑似结节' : '未发现结节' }}
              </el-tag>
            </div>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="置信度">{{ (detail.prediction.confidence * 100).toFixed(1) }}%</el-descriptions-item>
            <el-descriptions-item label="模型版本">{{ detail.prediction.model_version }}</el-descriptions-item>
            <el-descriptions-item label="推理耗时">{{ detail.prediction.inference_time_ms }}ms</el-descriptions-item>
            <el-descriptions-item v-if="detail.prediction.heatmap_path" label="热力图">
              <el-image :src="detail.prediction.heatmap_path" style="max-width: 200px" fit="contain" />
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 复核表单 -->
        <el-card v-if="!detail.latest_review || detail.latest_review.review_label !== 'confirmed'" class="detail-card">
          <template #header><span>人工复核</span></template>
          <ReviewForm :prediction-id="predictionId" @submitted="fetchDetail" />
        </el-card>

        <!-- 复核状态 -->
        <el-card v-if="detail.latest_review" class="detail-card">
          <template #header><span>最新复核</span></template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="复核结论">
              <ReportStatusTag :review-label="detail.latest_review.review_label" />
            </el-descriptions-item>
            <el-descriptions-item label="复核人">{{ detail.latest_review.reviewed_by_name || detail.latest_review.reviewed_by }}</el-descriptions-item>
            <el-descriptions-item label="复核时间">{{ detail.latest_review.reviewed_at }}</el-descriptions-item>
            <el-descriptions-item v-if="detail.latest_review.comment" label="复核意见" :span="3">
              {{ detail.latest_review.comment }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 复核历史 -->
        <el-card v-if="detail.review_history.length > 1" class="detail-card">
          <template #header><span>复核历史</span></template>
          <el-timeline>
            <el-timeline-item
              v-for="review in detail.review_history"
              :key="review.id"
              :timestamp="review.reviewed_at"
              placement="top"
            >
              <el-tag :type="review.review_label === 'confirmed' ? 'success' : 'warning'" size="small">
                {{ review.review_label === 'confirmed' ? '已确认' : '已修正' }}
              </el-tag>
              <span v-if="review.comment" style="margin-left: 8px; color: #606266">{{ review.comment }}</span>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReportDetail } from '@/api/reports'
import SlicePreview from '@/components/SlicePreview.vue'
import ReportStatusTag from '@/components/ReportStatusTag.vue'
import ReviewForm from '@/components/ReviewForm.vue'
import type { ReportDetail } from '@/types'

const route = useRoute()
const predictionId = Number(route.params.id)

const detail = ref<ReportDetail | null>(null)
const loading = ref(false)

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getReportDetail(predictionId)
    detail.value = res.data.data
  } catch { /* handled */ }
  finally { loading.value = false }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.report-detail-page {
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
