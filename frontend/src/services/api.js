import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 10000,
})

// Make interceptors completely safe for test environments
// The response interceptor can receive undefined error in some test scenarios
api.interceptors.request.use((config) => {
  try {
    const token = localStorage?.getItem?.('access_token')
    if (token && config && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch (e) {
    // Ignore all errors in test environment
  }
  return config
})

// Handle 401: try to refresh token, then retry once
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Extra defensive: handle completely undefined error
    if (!error) {
      return Promise.reject(new Error('Unknown error'))
    }
    // Guard against undefined error.config (can happen in test env)
    if (!error.config) {
      return Promise.reject(error)
    }
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refresh = localStorage?.getItem?.('refresh_token')
        if (!refresh) throw new Error('No refresh token')
        const res = await axios.post('http://localhost:8000/api/auth/token/refresh/', {
          refresh,
        })
        localStorage?.setItem?.('access_token', res.data.access)
        localStorage?.setItem?.('refresh_token', res.data.refresh)
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`
        }
        return api(originalRequest)
      } catch (e) {
        localStorage?.removeItem?.('access_token')
        localStorage?.removeItem?.('refresh_token')
        if (typeof window !== 'undefined' && window.location) {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api