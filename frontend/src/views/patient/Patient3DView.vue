<template>
  <div class="patient-3d-page">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span>三维肺部展示</span>
      </template>
    </el-page-header>

    <div class="patient-notice">
      <el-alert
        title="说明"
        type="info"
        :closable="false"
        show-icon
        description="下面是您本次检查的肺部三维示意图。彩色小球标记了AI分析时发现的关注区域。红色标记表示需要医生进一步确认的区域。您可以拖拽旋转、滚动缩放来查看模型。"
      />
    </div>

    <div v-loading="loading" class="viewer-wrapper">
      <el-empty v-if="!loading && error" :description="error" />
      <LungViewer v-else :markers="markers" :patient-mode="true" />
    </div>

    <div class="legend">
      <div class="legend-item">
        <span class="dot dot-red"></span>
        <span>疑似结节</span>
      </div>
      <div class="legend-item">
        <span class="dot dot-blue"></span>
        <span>正常区域</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getView3DData } from '@/api/view3d'
import LungViewer from '@/components/LungViewer.vue'
import type { Lung3DMarker } from '@/types'

const route = useRoute()
const studyId = Number(route.params.studyId)

const markers = ref<Lung3DMarker[]>([])
const loading = ref(false)
const error = ref('')

async function fetch3DData() {
  loading.value = true
  error.value = ''
  try {
    const res = await getView3DData(studyId)
    markers.value = res.data.data.markers || []
  } catch {
    error.value = '3D 资源加载失败，请稍后再试'
  }
  finally { loading.value = false }
}

onMounted(() => {
  fetch3DData()
})
</script>

<style scoped>
.patient-3d-page {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.patient-notice {
  margin-bottom: 0;
}
.viewer-wrapper {
  width: 100%;
}
.legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}
.dot-red {
  background: #ff4444;
}
.dot-blue {
  background: #4444ff;
}
</style>
