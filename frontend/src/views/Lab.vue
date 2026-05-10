<template>
  <div class="fade-in">
    <router-link to="/" class="back-link">← 返回首页</router-link>
    <div class="card" style="margin-bottom: 24px">
      <h2>AI 对话助手原型对比</h2>
      <p style="color: var(--text-secondary); margin-bottom: 16px">
        三种交互方案，请分别体验后选择。
      </p>
      <div class="lab-tabs">
        <router-link to="/lab/a" class="lab-tab" :class="{ active: $route.path === '/lab/a' }">
          Lab A — 内嵌聊天
        </router-link>
        <router-link to="/lab/b" class="lab-tab" :class="{ active: $route.path === '/lab/b' }">
          Lab B — 侧边栏
        </router-link>
        <router-link to="/lab/c" class="lab-tab" :class="{ active: $route.path === '/lab/c' }">
          Lab C — 浮动入口
        </router-link>
      </div>
    </div>
    <router-view />
  </div>
</template>

<style scoped>
.lab-tabs {
  display: flex;
  gap: 8px;
}

.lab-tab {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: #f1f5f9;
  text-decoration: none;
  transition: all 0.15s;
}

.lab-tab:hover {
  background: #e2e8f0;
}

.lab-tab.active {
  background: var(--primary);
  color: white;
}
</style>
