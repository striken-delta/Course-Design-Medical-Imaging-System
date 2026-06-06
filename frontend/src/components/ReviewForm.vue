<!--
  复核表单组件 — ReviewForm

  医生对 AI 预测结果进行复核的交互界面。
  - confirmed: 确认 AI 结果，直接提交
  - corrected: 修正 AI 结果，需额外选择纠正后的标签（nodule / non_nodule）
    提交后后端会同步更新预测记录的 label
-->
<template>
  <div class="review-form">
    <h4>提交复核意见</h4>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <!-- 复核结论：确认 or 修正 -->
      <el-form-item label="复核结论" prop="review_label">
        <el-radio-group v-model="form.review_label">
          <el-radio value="confirmed">
            <el-icon><Check /></el-icon>
            确认预测结果
          </el-radio>
          <el-radio value="corrected">
            <el-icon><Close /></el-icon>
            修正预测结果
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 仅在"修正"时显示：选择纠正后的正确标签 -->
      <el-form-item
        v-if="form.review_label === 'corrected'"
        label="纠正为"
        prop="corrected_label"
      >
        <el-radio-group v-model="form.corrected_label">
          <el-radio value="nodule">有结节 (nodule)</el-radio>
          <el-radio value="non_nodule">无结节 (non_nodule)</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 复核评语（选填） -->
      <el-form-item label="复核意见" prop="comment">
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="请输入复核意见（选填，最多500字）"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          提交复核
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
/**
 * ReviewForm — 医生复核表单逻辑

 * 交互流程:
 * 1. 默认选中"确认预测结果"
 * 2. 若医生选择"修正预测结果" → 展开纠正标签选择器
 * 3. 提交时校验：修正模式下 corrected_label 为必填
 * 4. 提交后触发 submitted 事件通知父组件刷新
 */
import { reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { submitReview } from '@/api/reviews'
import type { ReviewLabel } from '@/types'

const props = defineProps<{
  predictionId: number  // 被复核的预测记录 ID
}>()

const emit = defineEmits<{
  submitted: []  // 复核成功后通知父组件
}>()

const formRef = ref<FormInstance>()
const submitting = ref(false)

// 表单数据
const form = reactive({
  review_label: 'confirmed' as ReviewLabel,
  corrected_label: '' as string,  // 仅 corrected 时填写
  comment: ''
})

// 校验规则：修正时 corrected_label 必填
const rules: FormRules = {
  review_label: [
    { required: true, message: '请选择复核结论', trigger: 'change' }
  ],
  corrected_label: [
    {
      validator: (_rule, value, callback) => {
        if (form.review_label === 'corrected' && !value) {
          callback(new Error('请选择纠正后的标签'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

async function handleSubmit() {
  if (!formRef.value) return
  // 表单校验
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    // 调用 API 提交复核
    await submitReview({
      prediction_id: props.predictionId,
      review_label: form.review_label,
      corrected_label: form.corrected_label || undefined,  // 空字符串转为 undefined
      comment: form.comment || undefined
    })
    ElMessage.success('复核提交成功')
    emit('submitted')  // 通知父组件刷新数据
  } catch {
    // 错误已在请求拦截器中统一提示
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.review-form {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e6e6e6;
}
.review-form h4 {
  margin-bottom: 16px;
  font-size: 15px;
  color: #303133;
}
</style>
