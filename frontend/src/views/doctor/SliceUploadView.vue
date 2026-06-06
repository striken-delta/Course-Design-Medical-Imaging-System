<template>
  <div class="slice-page">
    <el-card>
      <template #header>
        <span>上传 CT 切片</span>
      </template>
      <el-form :inline="true" label-width="100px">
        <el-form-item label="关联检查" required>
          <el-input-number v-model="uploadForm.study_id" :min="1" placeholder="请输入 Study ID" />
        </el-form-item>
        <el-form-item label="切片序号" required>
          <el-input-number v-model="uploadForm.slice_index" :min="0" placeholder="切片序号" />
        </el-form-item>
      </el-form>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="10"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :before-upload="beforeUpload"
        :file-list="fileList"
        drag
        multiple
        accept=".png,.jpg,.jpeg"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">将 CT 切片拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="upload-tip">仅支持 png / jpg 格式，单文件不超过 10MB</div>
        </template>
      </el-upload>
      <div style="margin-top: 16px">
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="fileList.length === 0 || !uploadForm.study_id"
          @click="handleUpload"
        >
          {{ uploading ? '上传中...' : '开始上传' }}
        </el-button>
        <el-progress
          v-if="uploadProgress > 0 && uploadProgress < 100"
          :percentage="uploadProgress"
          style="width: 300px; margin-left: 16px"
        />
      </div>
    </el-card>

    <!-- 切片列表 -->
    <el-card class="section-card">
      <template #header>
        <span>切片列表</span>
      </template>
      <el-form :inline="true" :model="sliceFilters" class="filter-form">
        <el-form-item label="Study ID">
          <el-input-number v-model="sliceFilters.study_id" :min="1" placeholder="全部" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchSlices">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="slices" v-loading="sliceLoading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="study_id" label="Study ID" width="90" />
        <el-table-column prop="slice_index" label="切片序号" width="100" />
        <el-table-column prop="file_format" label="格式" width="80" />
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">
            {{ (row.file_size / 1024).toFixed(1) }} KB
          </template>
        </el-table-column>
        <el-table-column prop="uploaded_at" label="上传时间" width="170" />
        <el-table-column label="预览" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="previewSlice(row)">
              预览
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              type="warning"
              link
              size="small"
              :loading="inferringId === row.id"
              @click="handleInference(row.id)"
            >
              推理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!sliceLoading && slices.length === 0" description="暂无切片数据" />
    </el-card>

    <!-- 切片预览弹窗 -->
    <el-dialog v-model="showPreview" title="切片预览" width="600px">
      <SlicePreview :src="previewSrc" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type UploadInstance, type UploadFile, type UploadFiles } from 'element-plus'
import { getSliceList, uploadSlice } from '@/api/slices'
import { triggerInference } from '@/api/inference'
import SlicePreview from '@/components/SlicePreview.vue'
import type { CtSlice, SliceFilters } from '@/types'

const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadFile[]>([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadForm = reactive({
  study_id: undefined as number | undefined,
  slice_index: 0
})

function handleFileChange(_file: UploadFile, files: UploadFiles) {
  fileList.value = files as UploadFile[]
}
function handleFileRemove() {
  // handled by el-upload
}
function beforeUpload(file: UploadFile) {
  const isValidFormat = ['image/png', 'image/jpg', 'image/jpeg'].includes(file.raw?.type || '')
  const isValidSize = (file.size || 0) <= 10 * 1024 * 1024
  if (!isValidFormat) {
    ElMessage.error('仅支持 png/jpg 格式的文件')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  return true
}

async function handleUpload() {
  if (!uploadForm.study_id) {
    ElMessage.warning('请输入关联的 Study ID')
    return
  }
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  const total = fileList.value.length
  let success = 0

  for (let i = 0; i < fileList.value.length; i++) {
    const fileItem = fileList.value[i]
    if (!fileItem.raw) continue
    try {
      await uploadSlice(uploadForm.study_id, fileItem.raw, uploadForm.slice_index + i)
      success++
    } catch { /* skip failed */ }
    uploadProgress.value = Math.round(((i + 1) / total) * 100)
  }

  uploading.value = false
  ElMessage.success(`上传完成：${success}/${total} 成功`)
  if (success > 0) {
    fileList.value = []
    uploadRef.value?.clearFiles()
    fetchSlices()
  }
}

// ===== 切片列表 =====
const slices = ref<CtSlice[]>([])
const sliceLoading = ref(false)
const sliceFilters = reactive<SliceFilters>({ page: 1, page_size: 20 })

async function fetchSlices() {
  sliceLoading.value = true
  try {
    const res = await getSliceList(sliceFilters)
    slices.value = res.data.data.items
  } catch { /* handled */ }
  finally { sliceLoading.value = false }
}

// ===== 推理 =====
const inferringId = ref<number | null>(null)

async function handleInference(sliceId: number) {
  inferringId.value = sliceId
  try {
    const res = await triggerInference(sliceId)
    ElMessage.success(`推理完成：${res.data.data.label === 'nodule' ? '疑似结节' : '未发现结节'}（置信度 ${(res.data.data.confidence * 100).toFixed(1)}%）`)
  } catch { /* handled */ }
  finally { inferringId.value = null }
}

// ===== 预览 =====
const showPreview = ref(false)
const previewSrc = ref('')

function previewSlice(row: CtSlice) {
  previewSrc.value = row.file_path
  showPreview.value = true
}

onMounted(() => {
  fetchSlices()
})
</script>

<style scoped>
.slice-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.section-card {
  width: 100%;
}
.upload-icon {
  font-size: 48px;
  color: #409EFF;
}
.upload-text {
  margin-top: 8px;
  color: #606266;
}
.upload-tip {
  color: #909399;
  font-size: 12px;
}
.filter-form {
  margin-bottom: 16px;
}
</style>
