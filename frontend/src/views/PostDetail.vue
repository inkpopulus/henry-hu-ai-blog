<template>
  <div v-if="post" class="fade-in">
    <router-link to="/" class="back-link">← 返回首页</router-link>
    <div class="card">
      <div class="detail-header">
        <h1>{{ post.title }}</h1>
        <div class="meta">{{ post.created_at }}</div>
        <div class="post-tags" style="margin-top: 16px">
          <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>
      <div class="post-body" v-html="renderedContent"></div>
      <div v-if="auth.loggedIn" class="detail-actions">
        <router-link :to="`/edit/${post.id}`" class="btn btn-primary">编辑文章</router-link>
        <button class="btn btn-danger" @click="handleDelete">删除文章</button>
      </div>
    </div>
  </div>
  <div v-else class="state-empty">
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import { getPost, deletePost } from '../api'
import { auth } from '../stores/auth'
import { parseVideoEmbeds } from '../utils/videoEmbed'

const props = defineProps({ id: String })
const router = useRouter()
const post = ref(null)

// Configure marked
const VIDEO_PLACEHOLDER_RE = /\{% *(bilibili|youtube) +\S+ *%\}/gi

marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderer = new marked.Renderer()

renderer.image = function ({ href, title, text }) {
  const alt = text ? ` alt="${text}"` : ''
  return `<img src="${href}"${alt} class="post-image">`
}

function renderMarkdown(text) {
  // Replace video embed tags with placeholders before marked processes them
  const videoSlots = []
  const protectedText = text.replace(VIDEO_PLACEHOLDER_RE, (match) => {
    const idx = videoSlots.length
    videoSlots.push(match)
    return `%%VIDEO_${idx}%%`
  })

  let html = marked.parse(protectedText, { renderer })

  // Restore video embeds and parse via videoEmbed utility
  html = html.replace(/<p>%%VIDEO_(\d+)%%<\/p>/g, (_, i) => videoSlots[parseInt(i)])
  html = html.replace(/%%VIDEO_(\d+)%%/g, (_, i) => videoSlots[parseInt(i)])
  return parseVideoEmbeds(html)
}

const renderedContent = computed(() => {
  if (!post.value) return ''
  return renderMarkdown(post.value.content)
})

onMounted(async () => {
  post.value = await getPost(props.id)
})

async function handleDelete() {
  if (!confirm('确定要删除这篇文章吗？')) return
  await deletePost(props.id)
  router.push('/')
}
</script>

<style scoped>
.post-body {
  line-height: 1.9;
  font-size: 16px;
  color: var(--text);
}

.post-body :deep(h1) {
  font-size: 26px;
  font-weight: 700;
  margin: 32px 0 14px;
  color: var(--text);
}

.post-body :deep(h2) {
  font-size: 22px;
  font-weight: 700;
  margin: 28px 0 12px;
  color: var(--text);
}

.post-body :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 24px 0 10px;
  color: var(--text);
}

.post-body :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 8px;
  color: var(--text);
}

.post-body :deep(ul),
.post-body :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.post-body :deep(li) {
  margin: 4px 0;
}

.post-body :deep(table) {
  border-collapse: collapse;
  margin: 16px 0;
  width: 100%;
}

.post-body :deep(th),
.post-body :deep(td) {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}

.post-body :deep(th) {
  background: #f8fafc;
  font-weight: 600;
}

.post-body :deep(input[type="checkbox"]) {
  margin-right: 6px;
}

.post-body :deep(p) {
  margin: 8px 0;
}

.post-body :deep(strong) {
  font-weight: 600;
}

.post-body :deep(em) {
  font-style: italic;
}

.post-body :deep(del) {
  text-decoration: line-through;
  color: var(--text-muted);
}

.post-body :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 14px;
  color: #e11d48;
}

.post-body :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px 20px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 16px 0;
}

.post-body :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: 14px;
}

.post-body :deep(blockquote) {
  border-left: 4px solid var(--primary);
  padding: 8px 16px;
  margin: 12px 0;
  background: #f8fafc;
  color: var(--text-secondary);
  border-radius: 0 8px 8px 0;
}

.post-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}

.post-body :deep(a) {
  color: var(--primary);
  text-decoration: underline;
}

.post-body :deep(.post-image) {
  display: block;
  max-width: 100%;
  border-radius: 10px;
  margin: 20px 0;
  box-shadow: var(--shadow);
}

.post-body :deep(.video-embed) {
  position: relative;
  width: 100%;
  max-width: 680px;
  aspect-ratio: 16 / 9;
  margin: 24px 0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.post-body :deep(.video-embed iframe) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
