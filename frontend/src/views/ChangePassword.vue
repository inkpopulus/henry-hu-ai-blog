<template>
  <div class="login-page fade-in">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">🔑</div>
        <h2>修改密码</h2>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>旧密码</label>
          <input v-model="form.old_password" type="password" placeholder="请输入旧密码" required />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="form.new_password" type="password" placeholder="至少6位" required />
        </div>
        <div v-if="error" class="login-error">{{ error }}</div>
        <div v-if="success" class="login-success">{{ success }}</div>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          {{ loading ? '提交中...' : '确认修改' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const loading = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({ old_password: '', new_password: '' })

async function handleSubmit() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const token = localStorage.getItem('token')
    await axios.put('/api/password', form, {
      headers: { Authorization: `Bearer ${token}` },
    })
    success.value = '密码修改成功'
    form.old_password = ''
    form.new_password = ''
  } catch (e) {
    error.value = e.response?.data?.detail || '修改失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-success {
  background: #f0fdf4;
  color: #16a34a;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
  border: 1px solid #bbf7d0;
}
</style>
