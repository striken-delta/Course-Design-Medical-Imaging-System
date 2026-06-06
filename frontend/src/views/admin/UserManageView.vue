<template>
  <div class="user-manage-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" size="small" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部" clearable style="width: 130px">
            <el-option label="医生" value="doctor" />
            <el-option label="管理员" value="admin" />
            <el-option label="患者" value="patient" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="用户名搜索" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" min-width="130" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              :loading="togglingId === row.id"
              @change="(val: boolean) => toggleActive(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- 新增用户弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新增用户" width="480px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="4-32字符" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="createForm.password" type="password" placeholder="6-64字符" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option label="医生" value="doctor" />
            <el-option label="管理员" value="admin" />
            <el-option label="患者" value="patient" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="createForm.role === 'patient'" label="关联患者ID">
          <el-input-number v-model="createForm.patient_id" :min="1" placeholder="患者ID" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getUserList, createUser, updateUser } from '@/api/users'
import type { User, UserListParams, CreateUserRequest, UserRole } from '@/types'

const users = ref<User[]>([])
const total = ref(0)
const loading = ref(false)
const filters = reactive<UserListParams>({ page: 1, page_size: 20 })

function roleLabel(role: UserRole) {
  return role === 'doctor' ? '医生' : role === 'admin' ? '管理员' : '患者'
}
function roleType(role: UserRole) {
  return role === 'admin' ? 'danger' : role === 'doctor' ? 'primary' : 'info'
}

async function fetchUsers() {
  loading.value = true
  try {
    const params: UserListParams = { page: filters.page, page_size: filters.page_size }
    if (filters.role) params.role = filters.role
    if (filters.keyword) params.keyword = filters.keyword
    const res = await getUserList(params)
    users.value = res.data.data.items
    total.value = res.data.data.total
  } catch { /* handled */ }
  finally { loading.value = false }
}

// ===== 启用/禁用 =====
const togglingId = ref<number | null>(null)
async function toggleActive(user: User, active: boolean) {
  togglingId.value = user.id
  try {
    await updateUser(user.id, { is_active: active })
    user.is_active = active
    ElMessage.success(active ? '用户已启用' : '用户已禁用')
  } catch { /* handled */ }
  finally { togglingId.value = null }
}

// ===== 新增用户 =====
const showCreateDialog = ref(false)
const createFormRef = ref<FormInstance>()
const creating = ref(false)
const createForm = reactive<CreateUserRequest>({
  username: '',
  password: '',
  role: 'doctor'
})
const createRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 32, message: '用户名长度 4-32 字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度 6-64 字符', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

async function handleCreate() {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await createUser({
      username: createForm.username,
      password: createForm.password,
      role: createForm.role
    })
    ElMessage.success('用户创建成功')
    showCreateDialog.value = false
    createForm.username = ''
    createForm.password = ''
    createForm.role = 'doctor'
    createForm.patient_id = undefined
    fetchUsers()
  } catch { /* handled */ }
  finally { creating.value = false }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-manage-page {
  width: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-form {
  margin-bottom: 16px;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
