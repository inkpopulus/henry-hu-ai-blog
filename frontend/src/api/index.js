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
