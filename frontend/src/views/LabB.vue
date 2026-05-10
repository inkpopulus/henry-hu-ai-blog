<template>
  <div class="lab-b-layout">
    <div class="editor-area card">
      <h3>编辑器</h3>
      <textarea v-model="editorContent" rows="12" placeholder="在这里写内容..."></textarea>
    </div>
    <div class="sidebar" :class="{ open: sidebarOpen }">
      <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen">
        {{ sidebarOpen ? '→' : '← AI' }}
      </button>
      <div v-if="sidebarOpen" class="sidebar-content">
        <div class="sidebar-header">
          <h3>AI 助手</h3>
          <button class="btn btn-ghost" @click="clear" style="font-size: 12px; padding: 4px 10px">清空</button>
        </div>
        <div class="chat-messages" ref="messagesRef">
          <div v-if="messages.length === 0" class="chat-empty">
            向 AI 助手提问
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
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'
import { useChat } from '../composables/useChat'

const { messages, input, loading, send, stop, clear } = useChat()
const messagesRef = ref(null)
const editorContent = ref('')
const sidebarOpen = ref(true)

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

watch(() => messages.value.length, () => {
  nextTick(() => {
    const el = messagesRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
})
</script>

<style scoped>
.lab-b-layout {
  display: flex;
  gap: 0;
  position: relative;
}

.editor-area {
  flex: 1;
  min-width: 0;
  transition: margin-right 0.3s;
}

.editor-area textarea {
  min-height: 300px;
}

.sidebar {
  width: 44px;
  transition: width 0.3s;
  flex-shrink: 0;
  position: relative;
}

.sidebar.open {
  width: 360px;
}

.sidebar-toggle {
  position: absolute;
  left: -16px;
  top: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1.5px solid var(--border);
  background: var(--surface);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  z-index: 10;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-content {
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  height: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 15px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
}

.chat-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 0;
  font-size: 14px;
}

.chat-msg {
  margin-bottom: 10px;
  display: flex;
}

.chat-msg.user { justify-content: flex-end; }
.chat-msg.assistant { justify-content: flex-start; }

.chat-bubble {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
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
.chat-bubble :deep(pre) { background: #1e293b; color: #e2e8f0; padding: 8px; border-radius: 6px; overflow-x: auto; margin: 6px 0; font-size: 12px; }
.chat-bubble :deep(code) { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
.chat-bubble :deep(pre code) { background: none; padding: 0; }

.typing {
  color: var(--text-muted);
  font-style: italic;
}

.chat-input {
  display: flex;
  gap: 6px;
  padding: 10px 14px;
  border-top: 1px solid var(--border);
}

.chat-input input {
  flex: 1;
  font-size: 13px;
  padding: 6px 10px;
}
</style>
