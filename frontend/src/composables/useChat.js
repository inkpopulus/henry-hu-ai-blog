import { ref } from 'vue'
import { streamAIChat } from '../api'

export function useChat() {
  const messages = ref([])
  const input = ref('')
  const loading = ref(false)
  const abortController = ref(null)

  function send(systemPrompt) {
    const text = input.value.trim()
    if (!text || loading.value) return

    messages.value.push({ role: 'user', content: text })
    input.value = ''

    const apiMessages = [
      { role: 'system', content: systemPrompt || '你是一个写作助手，帮助用户写博客文章。回复使用 Markdown 格式。' },
      ...messages.value.map(m => ({ role: m.role, content: m.content })),
    ]

    loading.value = true
    abortController.value = new AbortController()
    let assistantMsg = { role: 'assistant', content: '' }
    messages.value.push(assistantMsg)

    streamAIChat(apiMessages, {
      signal: abortController.value.signal,
      onChunk(chunk) {
        assistantMsg.content += chunk
        // Trigger reactivity
        messages.value = [...messages.value]
      },
      onDone() {
        loading.value = false
        abortController.value = null
      },
      onError(msg) {
        assistantMsg.content += `\n\n**错误:** ${msg}`
        messages.value = [...messages.value]
        loading.value = false
        abortController.value = null
      },
    })
  }

  function stop() {
    abortController.value?.abort()
    loading.value = false
    abortController.value = null
  }

  function clear() {
    messages.value = []
  }

  return { messages, input, loading, send, stop, clear }
}
