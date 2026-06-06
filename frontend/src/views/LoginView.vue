<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="48" color="#409EFF"><Monitor /></el-icon>
        <h2>医学影像报告检索与肺结节分类系统</h2>
        <p>Medical Imaging Report Retrieval & Lung Nodule Classification</p>
      </div>

      <!-- 登录 / 注册 切换 -->
      <div class="tab-switch">
        <span
          class="tab-item"
          :class="{ active: mode === 'login' }"
          @click="switchMode('login')"
        >登录</span>
        <span class="tab-divider">|</span>
        <span
          class="tab-item"
          :class="{ active: mode === 'register' }"
          @click="switchMode('register')"
        >患者注册</span>
      </div>

      <!-- 登录表单 -->
      <el-form
        v-if="mode === 'login'"
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loginLoading"
            style="width: 100%"
          >
            {{ loginLoading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 注册表单 -->
      <el-form
        v-else
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
        size="large"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="4-32字符"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="患者编码" prop="patient_code">
          <el-input
            v-model="registerForm.patient_code"
            placeholder="选填，医生提供给您后可绑定已有检查数据"
            :prefix-icon="Ticket"
          />
          <div class="field-hint">如医生已为您创建患者档案，填写编码可绑定已有数据</div>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="至少6位，需包含字母、数字、下划线中至少两种"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="success"
            native-type="submit"
            :loading="registerLoading"
            style="width: 100%"
          >
            {{ registerLoading ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <template v-if="mode === 'login'">
          <span>没有账号？<a href="#" @click.prevent="switchMode('register')">立即注册</a></span>
        </template>
        <template v-else>
          <span>已有账号？<a href="#" @click.prevent="switchMode('login')">去登录</a></span>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Ticket } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { register as registerApi } from '@/api/auth'
import type { UserRole } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const mode = ref<'login' | 'register'>('login')

function switchMode(m: 'login' | 'register') {
  mode.value = m
  loginFormRef.value?.resetFields()
  registerFormRef.value?.resetFields()
}

// ========== 登录 ==========
const loginFormRef = ref<FormInstance>()
const loginLoading = ref(false)
const loginForm = reactive({ username: '', password: '' })

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 32, message: '用户名长度为 4-32 字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

function getHomeRoute(role: UserRole): string {
  switch (role) {
    case 'admin': return '/admin/users'
    case 'doctor': return '/doctor/patients'
    case 'patient': return '/patient/reports'
  }
}

async function handleLogin() {
  if (!loginFormRef.value) return
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loginLoading.value = true
  try {
    const user = await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })
    ElMessage.success(`欢迎回来，${user.username}！`)
    router.push(getHomeRoute(user.role))
  } catch {
    // 错误已在拦截器中统一提示
  } finally {
    loginLoading.value = false
  }
}

// ========== 注册 ==========
const registerFormRef = ref<FormInstance>()
const registerLoading = ref(false)
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  patient_code: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: (err?: Error) => void) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validatePasswordStrength = (_rule: any, value: string, callback: (err?: Error) => void) => {
  if (value.length < 6) {
    callback(new Error('密码长度不能小于6位'))
    return
  }
  let categories = 0
  if (/[a-zA-Z]/.test(value)) categories++
  if (/[0-9]/.test(value)) categories++
  if (value.includes('_')) categories++
  if (categories < 2) {
    callback(new Error('密码需包含字母、数字、下划线 _ 中至少两种'))
    return
  }
  callback()
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 32, message: '用户名长度为 4-32 字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePasswordStrength, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  if (!registerFormRef.value) return
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  registerLoading.value = true
  try {
    await registerApi({
      username: registerForm.username,
      password: registerForm.password,
      patient_code: registerForm.patient_code || undefined
    })
    ElMessage.success('注册成功！请登录')
    switchMode('login')
  } catch {
    // 错误已在拦截器中统一提示
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
  padding: 36px 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.login-header {
  text-align: center;
  margin-bottom: 24px;
}
.login-header h2 {
  margin: 10px 0 6px;
  font-size: 20px;
  color: #303133;
}
.login-header p {
  font-size: 12px;
  color: #909399;
}
.tab-switch {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
  font-size: 15px;
}
.tab-item {
  cursor: pointer;
  color: #909399;
  font-weight: 500;
  transition: color 0.2s;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
}
.tab-item.active {
  color: #409EFF;
  border-bottom-color: #409EFF;
}
.tab-item:hover {
  color: #409EFF;
}
.tab-divider {
  color: #dcdfe6;
}
.login-footer {
  text-align: center;
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.login-footer a {
  color: #409EFF;
  text-decoration: none;
}
.field-hint {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
  line-height: 1.4;
}
</style>
