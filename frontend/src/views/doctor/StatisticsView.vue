<template>
  <div class="statistics-page">
    <el-form :inline="true" class="filter-form">
      <el-form-item label="起始日期">
        <el-date-picker
          v-model="dateRange.date_from"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="结束日期">
        <el-date-picker
          v-model="dateRange.date_to"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
      </el-form-item>
    </el-form>

    <div v-loading="loading">
      <!-- 概览卡片 -->
      <el-row :gutter="16" class="overview-row">
        <el-col :span="4">
          <el-card class="stat-card">
            <div class="stat-value">{{ overview.upload_count }}</div>
            <div class="stat-label">上传量</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <div class="stat-value">{{ overview.inference_count }}</div>
            <div class="stat-label">推理量</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <div class="stat-value">{{ overview.review_count }}</div>
            <div class="stat-label">复核量</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <div class="stat-value positive">{{ (overview.positive_rate * 100).toFixed(1) }}%</div>
            <div class="stat-label">阳性率</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <div class="stat-value consistency">{{ (overview.consistency_rate * 100).toFixed(1) }}%</div>
            <div class="stat-label">复核一致率</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 趋势图 -->
      <el-card class="chart-card">
        <template #header><span>阳性率趋势</span></template>
        <StatisticChart :option="trendChartOption" :height="400" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getStatisticsOverview } from '@/api/statistics'
import StatisticChart from '@/components/StatisticChart.vue'
import type { StatisticsOverview, TrendItem } from '@/types'

const loading = ref(false)
const overview = reactive<StatisticsOverview>({
  upload_count: 0,
  inference_count: 0,
  review_count: 0,
  positive_rate: 0,
  consistency_rate: 0
})
const trendData = ref<TrendItem[]>([])
const dateRange = reactive({
  date_from: undefined as string | undefined,
  date_to: undefined as string | undefined
})

const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: trendData.value.map(t => t.date)
  },
  yAxis: [
    {
      type: 'value',
      name: '上传量',
      axisLabel: { formatter: '{value}' }
    },
    {
      type: 'value',
      name: '阳性率',
      axisLabel: { formatter: '{value}%' },
      max: 100
    }
  ],
  series: [
    {
      name: '上传量',
      type: 'bar',
      data: trendData.value.map(t => t.upload_count),
      itemStyle: { color: '#409EFF' }
    },
    {
      name: '阳性率',
      type: 'line',
      yAxisIndex: 1,
      data: trendData.value.map(t => (t.positive_rate * 100).toFixed(1)),
      itemStyle: { color: '#E6A23C' },
      smooth: true
    }
  ]
}))

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (dateRange.date_from) params.date_from = dateRange.date_from
    if (dateRange.date_to) params.date_to = dateRange.date_to
    const res = await getStatisticsOverview(params)
    const data = res.data.data
    Object.assign(overview, data.overview)
    trendData.value = data.trend || []
  } catch { /* handled */ }
  finally { loading.value = false }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.statistics-page {
  width: 100%;
}
.filter-form {
  margin-bottom: 16px;
}
.overview-row {
  margin-bottom: 20px;
}
.stat-card {
  text-align: center;
  cursor: default;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}
.stat-value.positive {
  color: #E6A23C;
}
.stat-value.consistency {
  color: #67C23A;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.chart-card {
  width: 100%;
}
</style>
