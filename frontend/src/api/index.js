import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export const login = (username, password) =>
  api.post('/login', { username, password }).then((r) => r.data)

export const getMe = () =>
  api.get('/me').then((r) => r.data)

export const getPosts = ({ tag, q } = {}) =>
  api.get('/posts', { params: { ...(tag ? { tag } : {}), ...(q ? { q } : {}) } }).then((r) => r.data)

export const getPost = (id) =>
  api.get(`/posts/${id}`).then((r) => r.data)

export const createPost = (data) =>
  api.post('/posts', data).then((r) => r.data)

export const updatePost = (id, data) =>
  api.put(`/posts/${id}`, data).then((r) => r.data)

export const deletePost = (id) =>
  api.delete(`/posts/${id}`)

export const getTags = () =>
  api.get('/tags').then((r) => r.data)

export const uploadImage = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data)
}

export const getAISkills = () =>
  api.get('/ai/skills').then((r) => r.data)

async function streamAI(url, payload, { onChunk, onDone, onError, signal }) {
  const token = localStorage.getItem('token')
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      signal,
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: '请求失败' }))
      onError?.(err.detail || '请求失败')
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          if (data.error) { onError?.(data.error); return }
          if (data.done) { onDone?.(); return }
          if (data.chunk) { onChunk(data.chunk) }
        }
      }
    }
    onDone?.()
  } catch (e) {
    if (e.name === 'AbortError') {
      onDone?.()
    } else {
      onError?.(e.message || '网络错误')
    }
  }
}

export const streamAIContinue = (payload, callbacks) =>
  streamAI('/api/ai/continue', payload, callbacks)

export const streamAIPolish = (payload, callbacks) =>
  streamAI('/api/ai/polish', payload, callbacks)

export const streamAIGenerate = (payload, callbacks) =>
  streamAI('/api/ai/generate', payload, callbacks)
