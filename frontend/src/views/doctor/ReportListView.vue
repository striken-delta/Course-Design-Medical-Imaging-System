<template>
  <div class="report-list-page">
    <el-card>
      <template #header>
        <span>报告检索</span>
      </template>
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="患者编码">
          <el-input v-model="filters.patient_code" placeholder="输入编码" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="起始日期">
          <el-date-picker
            v-model="filters.date_from"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filters.date_to"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="预测结果">
          <el-select v-model="filters.label" placeholder="全部" clearable style="width: 130px">
            <el-option label="疑似结节" value="nodule" />
            <el-option label="未发现结节" value="non_nodule" />
          </el-select>
        </el-form-item>
        <el-form-item label="复核状态">
          <el-select v-model="filters.review_status" placeholder="全部" clearable style="width: 130px">
            <el-option label="未复核" value="unreviewed" />
            <el-option label="已复核" value="reviewed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchReports">检索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="reports" v-loading="loading" stripe @row-click="goDetail">
        <el-table-column prop="prediction_id" label="报告ID" width="80" />
        <el-table-column prop="patient_code" label="患者编码" min-width="130" />
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="age_range" label="年龄段" width="90" />
        <el-table-column prop="label" label="预测结果" width="110">
          <template #default="{ row }">
            <el-tag :type="row.label === 'nodule' ? 'danger' : 'success'" size="small">
              {{ row.label === 'nodule' ? '疑似结节' : '未发现结节' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="{ row }">
            {{ (row.confidence * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="review_status" label="复核状态" width="100">
          <template #default="{ row }">
            <ReportStatusTag :review-status="row.review_status" :review-label="row.review_label" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="推理时间" width="170" />
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchReports"
        />
      </div>
      <el-empty v-if="!loading && reports.length === 0" description="暂无报告数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { searchReports } from '@/api/reports'
import ReportStatusTag from '@/components/ReportStatusTag.vue'
import type { ReportItem, ReportFilters } from '@/types'

const router = useRouter()
const reports = ref<ReportItem[]>([])
const total = ref(0)
const loading = ref(false)
const filters = reactive<ReportFilters>({
  page: 1,
  page_size: 20
})

async function fetchReports() {
  loading.value = true
  try {
    const res = await searchReports(filters)
    reports.value = res.data.data.items
    total.value = res.data.data.total
  } catch { /* handled */ }
  finally { loading.value = false }
}

function resetFilters() {
  filters.patient_code = undefined
  filters.date_from = undefined
  filters.date_to = undefined
  filters.label = undefined
  filters.review_status = undefined
  filters.page = 1
  fetchReports()
}

function goDetail(row: ReportItem) {
  router.push(`/doctor/reports/${row.prediction_id}`)
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.report-list-page {
  width: 100%;
}
.filter-form {
  margin-bottom: 16px;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
