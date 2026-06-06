<template>
  <div class="summary-card" :class="colorClass">
    <div class="summary-icon">
      <el-icon :size="36">
        <CircleCheckFilled v-if="colorCode === 'green'" />
        <WarningFilled v-else-if="colorCode === 'yellow'" />
        <CircleCloseFilled v-else />
      </el-icon>
    </div>
    <div class="summary-content">
      <h3>{{ title }}</h3>
      <p>{{ summary }}</p>
      <div v-if="explanation" class="explanation">
        <el-icon :size="14"><InfoFilled /></el-icon>
        <span>{{ explanation }}</span>
      </div>
      <div v-if="termDefinitions && termDefinitions.length > 0" class="terms">
        <el-popover
          v-for="(term, idx) in termDefinitions"
          :key="idx"
          placement="bottom"
          :width="280"
          trigger="click"
        >
          <template #reference>
            <el-tag size="small" class="term-tag" type="info">
              {{ term.term }}
              <el-icon :size="12"><QuestionFilled /></el-icon>
            </el-tag>
          </template>
          <p class="term-explain">{{ term.explanation }}</p>
        </el-popover>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ColorCode } from '@/types'

const props = defineProps<{
  title?: string
  summary: string
  colorCode: ColorCode
  explanation?: string
  termDefinitions?: { term: string; explanation: string }[]
}>()

const colorClass = computed(() => `card-${props.colorCode}`)
</script>

<style scoped>
.summary-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border-radius: 12px;
  border: 2px solid transparent;
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
.summary-icon {
  flex-shrink: 0;
}
.card-green .summary-icon {
  color: #22c55e;
}
.card-yellow .summary-icon {
  color: #eab308;
}
.card-red .summary-icon {
  color: #ef4444;
}
.summary-content h3 {
  font-size: 16px;
  margin-bottom: 4px;
  color: #303133;
}
.summary-content p {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
.explanation {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
.terms {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.term-tag {
  cursor: pointer;
}
.term-explain {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}
</style>
