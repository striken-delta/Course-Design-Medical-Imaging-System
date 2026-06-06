<template>
  <div class="audit-page">
    <el-card>
      <template #header>
        <span>审计日志</span>
      </template>
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="操作类型">
          <el-select v-model="filters.action" placeholder="全部" clearable style="width: 140px">
            <el-option label="登录" value="login" />
            <el-option label="上传" value="upload" />
            <el-option label="推理" value="inference" />
            <el-option label="复核" value="review" />
            <el-option label="修改" value="modify" />
          </el-select>
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
        <el-form-item>
          <el-button type="primary" @click="fetchLogs">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="action" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="actionType(row.action)" size="small">{{ actionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="对象类型" width="100" />
        <el-table-column prop="target_id" label="对象ID" width="80" />
        <el-table-column prop="detail" label="详情" min-width="180">
          <template #default="{ row }">
            <el-tooltip :content="row.detail" placement="top" :disabled="!row.detail">
              <span class="detail-text">{{ row.detail || '-' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="170" />
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchLogs"
        />
      </div>
      <el-empty v-if="!loading && logs.length === 0" description="暂无日志记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAuditLogs } from '@/api/audit'
import type { AuditLog, AuditFilters } from '@/types'

const logs = ref<AuditLog[]>([])
const total = ref(0)
const loading = ref(false)
const filters = reactive<AuditFilters>({ page: 1, page_size: 20 })

function actionLabel(action: string) {
  const map: Record<string, string> = {
    login: '登录', upload: '上传', inference: '推理',
    review: '复核', modify: '修改', create: '创建', delete: '删除'
  }
  return map[action] || action
}
function actionType(action: string) {
  if (action === 'login') return 'info'
  if (action === 'upload') return 'primary'
  if (action === 'inference') return 'warning'
  if (action === 'review') return 'success'
  return ''
}

async function fetchLogs() {
  loading.value = true
  try {
    const params: AuditFilters = { page: filters.page, page_size: filters.page_size }
    if (filters.action) params.action = filters.action
    if (filters.date_from) params.date_from = filters.date_from
    if (filters.date_to) params.date_to = filters.date_to
    if (filters.user_id) params.user_id = filters.user_id
    const res = await getAuditLogs(params)
    logs.value = res.data.data.items
    total.value = res.data.data.total
  } catch { /* handled */ }
  finally { loading.value = false }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.audit-page {
  width: 100%;
}
.filter-form {
  margin-bottom: 16px;
}
.detail-text {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
