<template>
  <div class="login-page fade-in">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">🔐</div>
        <h2>登录</h2>
        <p>登录后可以发布和删除文章</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </div>
        <div v-if="error" class="login-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'
import { auth } from '../stores/auth'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '' })

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const res = await login(form.username, form.password)
    auth.setToken(res.access_token)
    await auth.check()
    const redirect = router.currentRoute.value.query.redirect
    router.push(redirect || '/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.login-card {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.login-header h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 6px;
}

.login-header p {
  color: var(--text-muted);
  font-size: 14px;
}

.login-error {
  background: #fef2f2;
  color: #ef4444;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
  border: 1px solid #fecaca;
}

.login-btn {
  width: 100%;
  justify-content: center;
  padding: 12px;
  font-size: 15px;
}
</style>
