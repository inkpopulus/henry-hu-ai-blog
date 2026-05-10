<template>
  <div class="fade-in">
    <router-link to="/" class="back-link">← 返回首页</router-link>
    <div class="card form-card">
      <h2>{{ isEdit ? '编辑文章' : '写新文章' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>标题</label>
          <input v-model="form.title" placeholder="给文章起个标题" required />
        </div>
        <div class="form-group">
          <label>标签</label>
          <input v-model="tagInput" placeholder="用逗号分隔，如: python, tech, life" />
        </div>
        <div class="form-group">
          <div class="editor-toolbar">
            <div class="toolbar-group">
              <button type="button" class="tb-btn" title="加粗" @click="wrapText('**', '**')"><b>B</b></button>
              <button type="button" class="tb-btn" title="斜体" @click="wrapText('*', '*')"><i>I</i></button>
              <button type="button" class="tb-btn" title="删除线" @click="wrapText('~~', '~~')"><s>S</s></button>
            </div>
            <div class="toolbar-sep"></div>
            <div class="toolbar-group">
              <button type="button" class="tb-btn" title="一级标题" @click="insertPrefix('# ')">H1</button>
              <button type="button" class="tb-btn" title="二级标题" @click="insertPrefix('## ')">H2</button>
              <button type="button" class="tb-btn" title="三级标题" @click="insertPrefix('### ')">H3</button>
            </div>
            <div class="toolbar-sep"></div>
            <div class="toolbar-group">
              <button type="button" class="tb-btn" title="链接" @click="insertLink">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              </button>
              <button type="button" class="tb-btn" title="代码" @click="wrapText('`', '`')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              </button>
              <button type="button" class="tb-btn" title="代码块" @click="insertBlock('```', '```')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10h8M8 14h5"/></svg>
              </button>
              <button type="button" class="tb-btn" title="引用" @click="insertPrefix('> ')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/></svg>
              </button>
            </div>
            <div class="toolbar-sep"></div>
            <div class="toolbar-group">
              <label class="tb-btn" title="上传图片">
                <span v-if="uploading">...</span>
                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                <input type="file" accept="image/*" @change="handleUpload" hidden />
              </label>
              <button type="button" class="tb-btn" title="插入网络图片" @click="showImageDialog = true">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
              </button>
              <button type="button" class="tb-btn" title="插入视频" @click="showVideoDialog = true">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              </button>
            </div>
            <div class="toolbar-sep"></div>
            <div class="toolbar-group">
              <button type="button" class="tb-btn ai-btn" title="AI 续写" @click="handleContinue" :disabled="aiLoading">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/></svg>
                续写
              </button>
              <button type="button" class="tb-btn ai-btn" title="AI 润色" @click="handlePolish" :disabled="aiLoading">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.828 2.828 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
                润色
              </button>
              <button type="button" class="tb-btn ai-btn" title="AI 生成文章" @click="showGenerateDialog = true" :disabled="aiLoading">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
                生成
              </button>
              <button v-if="aiLoading" type="button" class="tb-btn ai-btn-stop" title="停止生成" @click="handleStopAI">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>
                停止
              </button>
            </div>
          </div>
          <textarea
            ref="textareaRef"
            v-model="form.content"
            placeholder="写下你的想法...&#10;&#10;支持 Markdown 格式：**加粗** *斜体* # 标题 > 引用 `代码`"
            required
          ></textarea>
        </div>
        <div v-if="error" class="login-error" style="margin-bottom: 16px">{{ error }}</div>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? '提交中...' : (isEdit ? '保存修改' : '发布文章') }}
        </button>
      </form>
    </div>

    <!-- Video embed dialog -->
    <div v-if="showVideoDialog" class="dialog-overlay" @mousedown.self="showVideoDialog = false">
      <div class="dialog">
        <h3>插入视频</h3>
        <div class="form-group">
          <label>平台</label>
          <select v-model="videoPlatform" class="video-select">
            <option v-for="p in platformList" :key="p.key" :value="p.key">{{ p.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>视频链接或 ID</label>
          <input v-model="videoInput" :placeholder="videoPlaceholder" @keydown.enter="insertVideo" />
        </div>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
          粘贴完整链接会自动提取视频 ID。
        </p>
        <div class="dialog-actions">
          <button class="btn btn-ghost" @click="showVideoDialog = false">取消</button>
          <button class="btn btn-primary" @click="insertVideo" :disabled="!videoInput.trim()">插入</button>
        </div>
      </div>
    </div>

    <!-- Network image dialog -->
    <div v-if="showImageDialog" class="dialog-overlay" @mousedown.self="showImageDialog = false">
      <div class="dialog">
        <h3>插入网络图片</h3>
        <input v-model="imageUrl" placeholder="输入图片 URL，如 https://example.com/img.png" @keydown.enter="insertNetworkImage" />
        <div class="dialog-actions">
          <button class="btn btn-ghost" @click="showImageDialog = false">取消</button>
          <button class="btn btn-primary" @click="insertNetworkImage" :disabled="!imageUrl.trim()">插入</button>
        </div>
      </div>
    </div>

    <!-- AI Generate article dialog -->
    <div v-if="showGenerateDialog" class="dialog-overlay" @mousedown.self="showGenerateDialog = false">
      <div class="dialog">
        <h3>AI 生成文章</h3>
        <div class="form-group">
          <label>主题 *</label>
          <input v-model="generateTopic" placeholder="文章主题，如：Vue 3 组合式 API 入门指南" @keydown.enter="handleGenerate" />
        </div>
        <div class="form-group">
          <label>大纲（可选）</label>
          <textarea v-model="generateOutline" placeholder="可选的详细大纲，每行一个要点..." rows="4"></textarea>
        </div>
        <div class="dialog-actions">
          <button class="btn btn-ghost" @click="showGenerateDialog = false">取消</button>
          <button class="btn btn-primary" @click="handleGenerate" :disabled="!generateTopic.trim()">生成</button>
        </div>
      </div>
    </div>

    <!-- AI Polish dialog -->
    <div v-if="showPolishDialog" class="dialog-overlay" @mousedown.self="showPolishDialog = false">
      <div class="dialog">
        <h3>AI 润色</h3>
        <div class="form-group">
          <label>改写指令（可选）</label>
          <input v-model="polishInstruction" placeholder="如：更正式、更简洁、适合初学者..." @keydown.enter="handlePolishConfirm" />
        </div>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
          留空则默认润色为更流畅、专业的表达。
        </p>
        <div class="dialog-actions">
          <button class="btn btn-ghost" @click="showPolishDialog = false">取消</button>
          <button class="btn btn-primary" @click="handlePolishConfirm">润色</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getPost, createPost, updatePost, uploadImage, streamAIContinue, streamAIPolish, streamAIGenerate } from '../api'
import { extractVideoId, getPlatformNames } from '../utils/videoEmbed'

const props = defineProps({ id: String })
const router = useRouter()
const isEdit = computed(() => !!props.id)

const submitting = ref(false)
const uploading = ref(false)
const error = ref('')
const tagInput = ref('')
const textareaRef = ref(null)
const form = reactive({ title: '', content: '' })

const showImageDialog = ref(false)
const imageUrl = ref('')

// Video state
const showVideoDialog = ref(false)
const videoPlatform = ref('bilibili')
const videoInput = ref('')
const platformList = getPlatformNames()
const videoPlaceholder = computed(() =>
  videoPlatform.value === 'bilibili'
    ? 'BV1xx411c7mD 或 https://www.bilibili.com/video/BV...'
    : 'dQw4w9WgXcQ 或 https://www.youtube.com/watch?v=...'
)

// AI state
const aiLoading = ref(false)
const aiAbortController = ref(null)
const showGenerateDialog = ref(false)
const generateTopic = ref('')
const generateOutline = ref('')
const showPolishDialog = ref(false)
const polishInstruction = ref('')
const polishSelection = ref(null)

onMounted(async () => {
  if (props.id) {
    const post = await getPost(props.id)
    form.title = post.title
    form.content = post.content
    tagInput.value = post.tags.join(', ')
  }
})

function getSelection() {
  const el = textareaRef.value
  if (!el) return { start: 0, end: 0 }
  return { start: el.selectionStart, end: el.selectionEnd }
}

function insertAtCursor(text) {
  const el = textareaRef.value
  if (!el) {
    form.content += text
    return
  }
  const { start, end } = getSelection()
  const before = form.content.substring(0, start)
  const after = form.content.substring(end)
  form.content = before + text + after
  const pos = start + text.length
  setTimeout(() => {
    el.selectionStart = el.selectionEnd = pos
    el.focus()
  }, 0)
}

function wrapText(before, after) {
  const el = textareaRef.value
  if (!el) return
  const { start, end } = getSelection()
  const selected = form.content.substring(start, end) || '文本'
  const newText = before + selected + after
  const pBefore = form.content.substring(0, start)
  const pAfter = form.content.substring(end)
  form.content = pBefore + newText + pAfter
  setTimeout(() => {
    el.selectionStart = start + before.length
    el.selectionEnd = start + before.length + selected.length
    el.focus()
  }, 0)
}

function insertPrefix(prefix) {
  const el = textareaRef.value
  if (!el) return
  const { start } = getSelection()
  const lineStart = form.content.lastIndexOf('\n', start - 1) + 1
  form.content = form.content.substring(0, lineStart) + prefix + form.content.substring(lineStart)
  setTimeout(() => {
    const newPos = start + prefix.length
    el.selectionStart = el.selectionEnd = newPos
    el.focus()
  }, 0)
}

function insertBlock(before, after) {
  insertAtCursor(`\n${before}\n代码\n${after}\n`)
}

function insertLink() {
  const el = textareaRef.value
  if (!el) return
  const { start, end } = getSelection()
  const selected = form.content.substring(start, end)
  if (selected) {
    wrapText('[', '](url)')
  } else {
    insertAtCursor('[链接文字](url)')
  }
}

function insertNetworkImage() {
  const url = imageUrl.value.trim()
  if (!url) return
  insertAtCursor(`\n![图片](${url})\n`)
  imageUrl.value = ''
  showImageDialog.value = false
}

function insertVideo() {
  const input = videoInput.value.trim()
  if (!input) return

  const detected = extractVideoId(input)
  const platform = detected ? detected.platform : videoPlatform.value
  const id = detected ? detected.id : input

  insertAtCursor(`\n{% ${platform} ${id} %}\n`)
  videoInput.value = ''
  showVideoDialog.value = false
}

async function handleUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  error.value = ''
  try {
    const res = await uploadImage(file)
    insertAtCursor(`\n![${file.name}](${res.url})\n`)
  } catch (err) {
    error.value = err.response?.data?.detail || '图片上传失败'
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

// --- AI Skill Handlers ---
function startAI() {
  aiLoading.value = true
  error.value = ''
  aiAbortController.value = new AbortController()
  textareaRef.value?.classList.add('ai-streaming')
}

function stopAI() {
  aiLoading.value = false
  aiAbortController.value?.abort()
  aiAbortController.value = null
  textareaRef.value?.classList.remove('ai-streaming')
}

function handleStopAI() {
  stopAI()
}

function handleContinue() {
  if (!form.content.trim()) {
    error.value = '请先写一些内容再使用续写功能'
    return
  }
  const el = textareaRef.value
  const selected = el ? form.content.substring(el.selectionStart, el.selectionEnd) : ''

  startAI()
  streamAIContinue({
    content: form.content,
    selected_text: selected || undefined,
  }, {
    signal: aiAbortController.value.signal,
    onChunk(chunk) {
      form.content += chunk
      nextTick(() => {
        if (el) {
          el.selectionStart = el.selectionEnd = form.content.length
          el.scrollTop = el.scrollHeight
        }
      })
    },
    onDone() { stopAI() },
    onError(msg) { error.value = msg; stopAI() },
  })
}

function handlePolish() {
  const el = textareaRef.value
  if (!el) return
  const { start, end } = { start: el.selectionStart, end: el.selectionEnd }
  const selected = form.content.substring(start, end)
  if (!selected.trim()) {
    error.value = '请先选中要润色的文字'
    return
  }
  polishSelection.value = { start, end }
  polishInstruction.value = ''
  showPolishDialog.value = true
}

function handlePolishConfirm() {
  const sel = polishSelection.value
  if (!sel) return
  showPolishDialog.value = false

  startAI()
  const { start, end } = sel
  const before = form.content.substring(0, start)
  const after = form.content.substring(end)
  let replacement = ''

  streamAIPolish({
    selected_text: form.content.substring(start, end),
    content: form.content,
    instruction: polishInstruction.value || undefined,
  }, {
    signal: aiAbortController.value.signal,
    onChunk(chunk) {
      replacement += chunk
      form.content = before + replacement + after
      nextTick(() => {
        const el = textareaRef.value
        if (el) {
          el.selectionStart = el.selectionEnd = start + replacement.length
        }
      })
    },
    onDone() {
      stopAI()
      polishSelection.value = null
    },
    onError(msg) {
      error.value = msg
      stopAI()
    },
  })
}

function handleGenerate() {
  const topic = generateTopic.value.trim()
  if (!topic) return
  showGenerateDialog.value = false

  startAI()
  form.content = ''
  streamAIGenerate({
    topic,
    outline: generateOutline.value.trim() || undefined,
  }, {
    signal: aiAbortController.value.signal,
    onChunk(chunk) {
      form.content += chunk
      nextTick(() => {
        const el = textareaRef.value
        if (el) {
          el.selectionStart = el.selectionEnd = form.content.length
          el.scrollTop = el.scrollHeight
        }
      })
    },
    onDone() {
      stopAI()
      // Auto-extract title from first heading if title is empty
      if (!form.title.trim()) {
        const match = form.content.match(/^#\s+(.+)$/m)
        if (match) form.title = match[1].trim()
      }
    },
    onError(msg) { error.value = msg; stopAI() },
  })
  generateTopic.value = ''
  generateOutline.value = ''
}

async function handleSubmit() {
  submitting.value = true
  error.value = ''
  try {
    const tags = tagInput.value
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
    if (isEdit.value) {
      await updatePost(props.id, { ...form, tags })
      router.push(`/post/${props.id}`)
    } else {
      const post = await createPost({ ...form, tags })
      router.push(`/post/${post.id}`)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请先登录'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  padding: 6px 8px;
  background: #f8fafc;
  border: 1.5px solid var(--border);
  border-bottom: none;
  border-radius: 10px 10px 0 0;
  flex-wrap: wrap;
}

.editor-toolbar + textarea {
  border-radius: 0 0 10px 10px !important;
}

.toolbar-group {
  display: flex;
  gap: 2px;
}

.toolbar-sep {
  width: 1px;
  height: 20px;
  background: #e2e8f0;
  margin: 0 4px;
}

.tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 30px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  transition: all 0.15s;
}

.tb-btn:hover {
  background: #e2e8f0;
  color: var(--text);
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  backdrop-filter: blur(2px);
}

.dialog {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 28px;
  width: 100%;
  max-width: 460px;
  box-shadow: var(--shadow-lg);
}

.dialog h3 {
  margin-bottom: 16px;
  font-size: 18px;
}

.dialog input,
.dialog textarea {
  margin-bottom: 20px;
}

.dialog .form-group {
  margin-bottom: 0;
}

.dialog .form-group label {
  margin-bottom: 6px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.video-select {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  background: var(--surface);
  color: var(--text);
  margin-bottom: 20px;
  cursor: pointer;
}

.ai-btn {
  color: #6366f1;
  font-size: 12px;
  width: auto;
  padding: 0 8px;
  gap: 3px;
}

.ai-btn:hover:not(:disabled) {
  background: #eef2ff;
  color: #4f46e5;
}

.ai-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-btn-stop {
  color: #ef4444;
  font-size: 12px;
  width: auto;
  padding: 0 8px;
  gap: 3px;
}

.ai-btn-stop:hover {
  background: #fef2f2;
}

textarea.ai-streaming {
  border-color: #818cf8 !important;
  animation: ai-pulse 1.5s ease-in-out infinite;
}

@keyframes ai-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
  50% { box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25); }
}
</style>
