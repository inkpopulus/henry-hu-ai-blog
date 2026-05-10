<template>
  <div>
    <div class="card">
      <h3>编辑器</h3>
      <textarea v-model="editorContent" rows="6" placeholder="在这里写内容..."></textarea>
    </div>
    <div class="card chat-panel">
      <div class="chat-header">
        <h3>AI 对话</h3>
        <button class="btn btn-ghost" @click="clear" style="font-size: 12px; padding: 4px 10px">清空</button>
      </div>
      <div class="chat-messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="chat-empty">
          向 AI 助手提问，帮助你写作
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
        <button v-if="loading" class="btn btn-danger" @click="stop" style="padding: 6px 14px">停止</button>
        <button v-else class="btn btn-primary" @click="handleSend" :disabled="!input.trim()" style="padding: 6px 14px">发送</button>
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
.chat-panel {
  margin-top: 16px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chat-header h3 {
  margin: 0;
}

.chat-messages {
  height: 320px;
  overflow-y: auto;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  background: #fafafa;
}

.chat-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 0;
}

.chat-msg {
  margin-bottom: 12px;
  display: flex;
}

.chat-msg.user {
  justify-content: flex-end;
}

.chat-msg.assistant {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 80%;
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
  background: white;
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
}

.chat-input input {
  flex: 1;
}
</style>
