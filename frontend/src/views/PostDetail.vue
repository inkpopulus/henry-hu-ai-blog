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
import { getPost, deletePost } from '../api'
import { auth } from '../stores/auth'
import { parseVideoEmbeds } from '../utils/videoEmbed'

const props = defineProps({ id: String })
const router = useRouter()
const post = ref(null)

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderMarkdown(text) {
  // Extract code blocks first to protect them from further processing
  const codeBlocks = []
  let result = text.replace(/```([\s\S]*?)```/g, (_, code) => {
    const placeholder = `__CODEBLOCK_${codeBlocks.length}__`
    codeBlocks.push('<pre><code>' + escapeHtml(code) + '</code></pre>')
    return placeholder
  })
  // Split into lines for block-level elements
  const lines = result.split('\n')
  const output = []
  let inList = false

  for (let line of lines) {
    // Code block placeholder — pass through as-is
    if (/^__CODEBLOCK_\d+__$/.test(line.trim())) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push(line.trim())
      continue
    }
    // Headings
    if (line.startsWith('#### ')) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('<h4>' + inlineMarkdown(escapeHtml(line.slice(5))) + '</h4>')
      continue
    }
    if (line.startsWith('### ')) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('<h3>' + inlineMarkdown(escapeHtml(line.slice(4))) + '</h3>')
      continue
    }
    if (line.startsWith('## ')) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('<h2>' + inlineMarkdown(escapeHtml(line.slice(3))) + '</h2>')
      continue
    }
    if (line.startsWith('# ')) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('<h2>' + inlineMarkdown(escapeHtml(line.slice(2))) + '</h2>')
      continue
    }
    // Blockquote
    if (line.startsWith('> ')) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('<blockquote>' + inlineMarkdown(escapeHtml(line.slice(2))) + '</blockquote>')
      continue
    }
    // Horizontal rule
    if (/^-{3,}$/.test(line.trim()) || /^\*{3,}$/.test(line.trim())) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('<hr>')
      continue
    }
    // Video embed tag
    if (/^{% *(bilibili|youtube) +\S+ *%}$/i.test(line.trim())) {
      if (inList) { output.push('</ul>'); inList = false }
      output.push(line.trim())
      continue
    }
    // Empty line
    if (line.trim() === '') {
      if (inList) { output.push('</ul>'); inList = false }
      output.push('')
      continue
    }
    // Normal text
    if (inList) { output.push('</ul>'); inList = false }
    output.push('<p>' + inlineMarkdown(escapeHtml(line)) + '</p>')
  }
  if (inList) output.push('</ul>')
  // Restore code blocks and parse video embeds
  const html = output.join('\n').replace(/__CODEBLOCK_(\d+)__/g, (_, i) => codeBlocks[parseInt(i)])
  return parseVideoEmbeds(html)
}

function inlineMarkdown(text) {
  // Images
  text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="post-image">')
  // Links
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  // Bold
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // Italic
  text = text.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // Strikethrough
  text = text.replace(/~~(.+?)~~/g, '<del>$1</del>')
  // Inline code
  text = text.replace(/`(.+?)`/g, '<code>$1</code>')
  return text
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
