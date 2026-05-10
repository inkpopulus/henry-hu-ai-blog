<template>
  <div>
    <div class="card">
      <h3>编辑器</h3>
      <textarea v-model="editorContent" rows="10" placeholder="在这里写内容..."></textarea>
    </div>

    <!-- Floating pet button -->
    <div class="pet-button" @click="sidebarOpen = !sidebarOpen" :class="{ active: sidebarOpen }">
      <span>AI</span>
    </div>

    <!-- Sidebar overlay -->
    <Transition name="sidebar">
      <div v-if="sidebarOpen" class="sidebar-overlay" @mousedown.self="sidebarOpen = false">
        <div class="sidebar-panel">
          <div class="sidebar-header">
            <h3>AI 助手</h3>
            <div style="display: flex; gap: 6px">
              <button class="btn btn-ghost" @click="clear" style="font-size: 12px; padding: 4px 10px">清空</button>
              <button class="btn btn-ghost" @click="sidebarOpen = false" style="font-size: 12px; padding: 4px 10px">关闭</button>
            </div>
          </div>
          <div class="chat-messages" ref="messagesRef">
            <div v-if="messages.length === 0" class="chat-empty">
              <div class="chat-empty-icon">AI</div>
              <p>你好！我是你的写作助手</p>
              <p style="font-size: 13px">你可以问我任何关于写作的问题</p>
            </div>
            <div v-for="(msg, i) in messages" :key="i" :class="['chat-msg', msg.role]">
              <div class="chat-bubble" v-html="renderBubble(msg.content)"></div>
            </div>
            <div v-if="loading" class="chat-msg assistant">
              <div class="chat-bubble typing">思考中...</div>
            </div>
          </div>
          <div class="chat-input">
            <input
              v-model="input"
              placeholder="输入消息..."
              @keydown.enter.exact="handleSend"
            />
            <button v-if="loading" class="btn btn-danger" @click="stop" style="padding: 6px 14px">停</button>
            <button v-else class="btn btn-primary" @click="handleSend" :disabled="!input.trim()" style="padding: 6px 14px">发</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Notification bubble -->
    <Transition name="bubble">
      <div v-if="notifyBubble" class="notify-bubble" @click="sidebarOpen = true; notifyBubble = false">
        <span>AI 回复了</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'
import { useChat } from '../composables/useChat'

const { messages, input, loading, send, stop, clear } = useChat()
const messagesRef = ref(null)
const editorContent = ref('')
const sidebarOpen = ref(false)
const notifyBubble = ref(false)

marked.setOptions({ breaks: true, gfm: true })

function renderBubble(text) {
  return marked.parse(text)
}

function handleSend() {
  const ctx = editorContent.value.trim()
  const systemPrompt = ctx
    ? `你是一个写作助手。用户正在写以下内容：\n\n${ctx}\n\n请根据上下文帮助用户。回复使用 Markdown 格式。`
    : '你是一个写作助手，帮助用户写博客文章。回复使用 Markdown 格式。'
  send(systemPrompt)
}

// Show notification when AI finishes while sidebar is closed
watch(loading, (newVal, oldVal) => {
  if (oldVal && !newVal && !sidebarOpen.value) {
    notifyBubble.value = true
    setTimeout(() => { notifyBubble.value = false }, 4000)
  }
})

watch(() => messages.value.length, () => {
  nextTick(() => {
    const el = messagesRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
})
</script>

<style scoped>
.pet-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: 700;
  font-size: 15px;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  transition: all 0.2s;
  z-index: 100;
}

.pet-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

.pet-button.active {
  background: #4f46e5;
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 200;
  display: flex;
  justify-content: flex-end;
}

.sidebar-panel {
  width: 380px;
  max-width: 90vw;
  background: var(--surface);
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.chat-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.chat-empty-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.chat-msg {
  margin-bottom: 12px;
  display: flex;
}

.chat-msg.user { justify-content: flex-end; }
.chat-msg.assistant { justify-content: flex-start; }

.chat-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.chat-msg.user .chat-bubble {
  background: var(--primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-msg.assistant .chat-bubble {
  background: #f8fafc;
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}

.chat-bubble :deep(p) { margin: 4px 0; }
.chat-bubble :deep(pre) { background: #1e293b; color: #e2e8f0; padding: 10px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
.chat-bubble :deep(code) { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 13px; }
.chat-bubble :deep(pre code) { background: none; padding: 0; }

.typing {
  color: var(--text-muted);
  font-style: italic;
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--border);
}

.chat-input input {
  flex: 1;
}

.notify-bubble {
  position: fixed;
  bottom: 88px;
  right: 24px;
  background: var(--primary);
  color: white;
  padding: 10px 18px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  z-index: 100;
}

/* Transitions */
.sidebar-enter-active,
.sidebar-leave-active {
  transition: opacity 0.25s;
}
.sidebar-enter-active .sidebar-panel,
.sidebar-leave-active .sidebar-panel {
  transition: transform 0.25s;
}
.sidebar-enter-from,
.sidebar-leave-to {
  opacity: 0;
}
.sidebar-enter-from .sidebar-panel,
.sidebar-leave-to .sidebar-panel {
  transform: translateX(100%);
}

.bubble-enter-active {
  transition: all 0.3s ease;
}
.bubble-leave-active {
  transition: all 0.3s ease;
}
.bubble-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.9);
}
.bubble-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.9);
}
</style>
