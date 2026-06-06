<template>
  <div class="slice-preview">
    <div v-if="!src" class="empty-state">
      <el-icon :size="48"><Picture /></el-icon>
      <p>暂无切片图像</p>
    </div>
    <div v-else class="image-container">
      <el-image
        :src="src"
        :preview-src-list="[src]"
        fit="contain"
        :preview-teleported="true"
        class="slice-image"
      >
        <template #error>
          <div class="image-error">
            <el-icon :size="32"><PictureFilled /></el-icon>
            <p>图像加载失败</p>
          </div>
        </template>
        <template #placeholder>
          <div class="image-placeholder">
            <el-icon :size="32" class="is-loading"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
        </template>
      </el-image>
      <div class="image-overlay">
        <el-icon :size="16"><ZoomIn /></el-icon>
        <span>点击放大</span>
      </div>
      <div v-if="info" class="slice-info">
        <span v-if="info.slice_index !== undefined">切片序号：{{ info.slice_index }}</span>
        <span v-if="info.file_format">格式：{{ info.file_format.toUpperCase() }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  src?: string
  info?: {
    slice_index?: number
    file_format?: string
  }
}>()
</script>

<style scoped>
.slice-preview {
  border: 1px solid #393939;
  border-radius: 8px;
  overflow: hidden;
  background: #1a1a1a;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #666;
  background: #fafafa;
}
.empty-state p {
  margin-top: 8px;
  font-size: 14px;
}
.image-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  max-height: 520px;
  background: #1a1a1a;
}
.slice-image {
  width: 100%;
  height: 100%;
  max-height: 520px;
  cursor: pointer;
}
.slice-image :deep(img) {
  object-fit: contain;
  max-height: 520px;
}
.image-overlay {
  position: absolute;
  bottom: 36px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.55);
  border-radius: 4px;
  color: #ccc;
  font-size: 12px;
  pointer-events: none;
  transition: opacity 0.3s;
}
.image-container:hover .image-overlay {
  opacity: 0;
}
.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #666;
}
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #999;
}
.slice-info {
  display: flex;
  gap: 16px;
  padding: 8px 14px;
  background: #2a2a2a;
  font-size: 12px;
  color: #aaa;
  border-top: 1px solid #393939;
}
</style>
