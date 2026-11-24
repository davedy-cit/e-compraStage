import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    _initialized: false,
  }),
  actions: {
    async login(username, password) {
      const res = await api.post('auth/token/', { username, password })
      localStorage.setItem('access_token', res.data.access)
      localStorage.setItem('refresh_token', res.data.refresh)
      this.isAuthenticated = true
      await this.fetchUser()
    },
    async register(payload) {
      const res = await api.post('accounts/auth/register/', payload)
      localStorage.setItem('access_token', res.data.access)
      localStorage.setItem('refresh_token', res.data.refresh)
      this.user = res.data.user
      this.isAuthenticated = true
    },
    async fetchUser() {
      try {
        const res = await api.get('accounts/auth/user/')
        this.user = res.data
      } catch (e) {
        this.logout()
      }
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.user = null
      this.isAuthenticated = false
    },
    async init() {
      if (this._initialized) return
      const token = localStorage.getItem('access_token')
      if (token) {
        this.isAuthenticated = true
        await this.fetchUser()
      }
      this._initialized = true
    },
  },
})