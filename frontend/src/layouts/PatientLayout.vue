<template>
  <el-container class="layout">
    <el-header class="patient-header">
      <div class="header-left">
        <el-icon :size="22"><HomeFilled /></el-icon>
        <span class="app-name">个人检查报告</span>
      </div>
      <div class="header-right">
        <span class="welcome">您好，{{ authStore.user?.username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="patient-aside">
        <el-menu
          :default-active="activeMenu"
          router
          class="patient-menu"
        >
          <el-menu-item index="/patient/reports">
            <el-icon><Document /></el-icon>
            <span>我的报告</span>
          </el-menu-item>
          <el-menu-item index="/patient/progress">
            <el-icon><Clock /></el-icon>
            <span>检查进度</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="patient-main">
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

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
  background: #f5f7fa;
}
.patient-header {
  background: #409EFF;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.welcome {
  font-size: 14px;
}
.patient-aside {
  background: #fff;
  border-right: 1px solid #e6e6e6;
  min-height: calc(100vh - 56px);
}
.patient-menu {
  border-right: none;
}
.patient-main {
  background: #f5f7fa;
  padding: 24px;
  min-height: calc(100vh - 56px);
}
</style>
