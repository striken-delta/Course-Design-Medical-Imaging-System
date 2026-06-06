<template>
  <div class="view3d-page">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span>3D 肺部展示 - Study #{{ studyId }}</span>
      </template>
    </el-page-header>

    <div v-loading="loading" class="viewer-wrapper">
      <el-empty v-if="!loading && error" :description="error" />
      <LungViewer v-else :markers="markers" />
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
    error.value = '3D 资源加载失败'
  }
  finally { loading.value = false }
}

onMounted(() => {
  fetch3DData()
})
</script>

<style scoped>
.view3d-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.viewer-wrapper {
  width: 100%;
}
</style>
