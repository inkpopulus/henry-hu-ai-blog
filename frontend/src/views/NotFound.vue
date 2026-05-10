<template>
  <div class="not-found fade-in">
    <h1>404</h1>
    <p>页面不存在</p>
    <router-link to="/" class="btn btn-primary">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found {
  text-align: center;
  padding: 80px 0;
}

.not-found h1 {
  font-size: 72px;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.not-found p {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}
</style>
