import { reactive } from 'vue'
import { getMe } from '../api'

export const auth = reactive({
  loggedIn: false,
  username: null,
  loading: true,

  async check() {
    try {
      const res = await getMe()
      this.loggedIn = res.logged_in
      this.username = res.username
    } catch {
      this.loggedIn = false
      this.username = null
    } finally {
      this.loading = false
    }
  },

  setToken(token) {
    localStorage.setItem('token', token)
    this.loggedIn = true
  },

  logout() {
    localStorage.removeItem('token')
    this.loggedIn = false
    this.username = null
  },
})
