<template>
  <el-tag :type="tagType" :size="size" :effect="effect">
    {{ label }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  reviewStatus?: string
  reviewLabel?: string
  size?: '' | 'small' | 'default' | 'large'
  effect?: 'light' | 'dark' | 'plain'
}>(), {
  size: 'default',
  effect: 'light'
})

const label = computed(() => {
  if (props.reviewLabel === 'confirmed') return '已确认'
  if (props.reviewLabel === 'corrected') return '已修正'
  if (props.reviewStatus === 'reviewed') return '已复核'
  return '未复核'
})

const tagType = computed(() => {
  if (props.reviewLabel === 'confirmed') return 'success'
  if (props.reviewLabel === 'corrected') return 'warning'
  if (props.reviewStatus === 'reviewed') return 'success'
  return 'info'
})
</script>
