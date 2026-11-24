import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.resetAllMocks()
  })

  it('initializes with no user and not authenticated', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(store._initialized).toBe(false)
  })

  it('sets authenticated and fetches user on login', async () => {
    const store = useAuthStore()

    // Mock api calls
    vi.spyOn(api, 'post').mockResolvedValue({
      data: { access: 'mock-access-token', refresh: 'mock-refresh-token' }
    })
    vi.spyOn(api, 'get').mockResolvedValue({
      data: { id: 1, username: 'testuser', role: 'customer' }
    })

    await store.login('testuser', 'password')

    expect(store.isAuthenticated).toBe(true)
    expect(store.user).toEqual({ id: 1, username: 'testuser', role: 'customer' })
    expect(localStorage.getItem('access_token')).toBe('mock-access-token')
    expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token')
  })

  it('clears auth on logout', () => {
    const store = useAuthStore()

    // Manually set authenticated state
    store.isAuthenticated = true
    store.user = { id: 1, username: 'testuser' }
    localStorage.setItem('access_token', 'some-token')
    localStorage.setItem('refresh_token', 'some-refresh')

    expect(store.isAuthenticated).toBe(true)

    store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('initializes from localStorage on init', async () => {
    const store = useAuthStore()

    // Pre-populate localStorage
    localStorage.setItem('access_token', 'existing-token')
    localStorage.setItem('refresh_token', 'existing-refresh')

    vi.spyOn(api, 'get').mockResolvedValue({
      data: { id: 1, username: 'existinguser', role: 'vendor' }
    })

    await store.init()

    expect(store._initialized).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(store.user).toEqual({ id: 1, username: 'existinguser', role: 'vendor' })
  })

  it('does not set authenticated if no token in localStorage', async () => {
    const store = useAuthStore()

    await store.init()

    expect(store._initialized).toBe(true)
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('logs out if fetchUser fails during init', async () => {
    const store = useAuthStore()

    localStorage.setItem('access_token', 'bad-token')
    localStorage.setItem('refresh_token', 'bad-refresh')

    vi.spyOn(api, 'get').mockRejectedValue(new Error('Unauthorized'))

    await store.init()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('registers new user and sets authenticated state', async () => {
    const store = useAuthStore()

    const registerPayload = {
      username: 'newuser',
      email: 'new@test.com',
      first_name: 'Juan',
      last_name: 'Dela Cruz',
      password: 'SecurePass123',
      password_confirm: 'SecurePass123',
      phone: '09171234567',
      address: '123 Mandaue City, Cebu',
    }

    vi.spyOn(api, 'post').mockResolvedValue({
      data: {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: { id: 5, username: 'newuser', role: 'customer' },
      },
    })

    await store.register(registerPayload)

    expect(api.post).toHaveBeenCalledWith('accounts/auth/register/', registerPayload)
    expect(store.isAuthenticated).toBe(true)
    expect(store.user).toEqual({ id: 5, username: 'newuser', role: 'customer' })
    expect(localStorage.getItem('access_token')).toBe('mock-access-token')
    expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token')
  })

  it('throws error on registration failure', async () => {
    const store = useAuthStore()

    const registerPayload = {
      username: 'existing',
      email: 'exists@test.com',
      first_name: 'Juan',
      last_name: 'Dela Cruz',
      password: 'SecurePass123',
      password_confirm: 'SecurePass123',
      phone: '09171234567',
      address: '123 Mandaue City, Cebu',
    }

    vi.spyOn(api, 'post').mockRejectedValue({
      response: { data: { username: ['A user with that username already exists.'] } },
    })

    await expect(store.register(registerPayload)).rejects.toEqual({
      response: { data: { username: ['A user with that username already exists.'] } },
    })

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })
})