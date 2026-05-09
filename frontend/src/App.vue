<template>
  <header class="site-header">
    <div class="container">
      <router-link to="/" class="site-logo">
        <span class="dot"></span>
        Henry Hu's Blog
      </router-link>
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索文章..."
          @keydown.enter="handleSearch"
        />
      </div>
      <nav class="site-nav">
        <router-link to="/">首页</router-link>
        <template v-if="auth.loggedIn">
          <router-link to="/new">写文章</router-link>
          <router-link to="/password">改密码</router-link>
          <a href="#" @click.prevent="handleLogout">退出</a>
        </template>
        <template v-else>
          <router-link to="/login">登录</router-link>
        </template>
      </nav>
    </div>
  </header>
  <main class="container" style="padding-top: 32px; padding-bottom: 60px">
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from './stores/auth'

const router = useRouter()
const searchQuery = ref('')

onMounted(() => auth.check())

function handleSearch() {
  const q = searchQuery.value.trim()
  router.push(q ? `/?q=${encodeURIComponent(q)}` : '/')
}

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.search-box {
  flex: 1;
  max-width: 280px;
  margin: 0 24px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.search-box input {
  width: 100%;
  padding: 7px 14px 7px 36px;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  color: white;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-box input:focus {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
