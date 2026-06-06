<template>
  <el-container class="layout">
    <el-aside width="240px" class="aside">
      <div class="logo">
        <el-icon :size="24"><Monitor /></el-icon>
        <span>医学影像系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/doctor/patients">
          <el-icon><User /></el-icon>
          <span>患者与检查管理</span>
        </el-menu-item>
        <el-menu-item index="/doctor/slices">
          <el-icon><Upload /></el-icon>
          <span>切片上传与管理</span>
        </el-menu-item>
        <el-menu-item index="/doctor/reports">
          <el-icon><Document /></el-icon>
          <span>报告检索</span>
        </el-menu-item>
        <el-menu-item index="/doctor/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/doctor/patients' }">医生工作台</el-breadcrumb-item>
            <el-breadcrumb-item v-if="pageTitle">{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="primary" size="small">医生</el-tag>
          <span class="username">{{ authStore.user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/doctor/patients': '患者与检查管理',
    '/doctor/slices': '切片上传与管理',
    '/doctor/reports': '报告检索',
    '/doctor/statistics': '统计分析'
  }
  // match dynamic routes
  if (route.path.startsWith('/doctor/reports/')) return '报告详情'
  if (route.path.startsWith('/doctor/view3d/')) return '3D 肺部展示'
  return titles[route.path] || ''
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background-color: #304156;
  overflow-y: auto;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
  height: 60px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.username {
  font-weight: 500;
}
.main {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  padding: 20px;
}
</style>
