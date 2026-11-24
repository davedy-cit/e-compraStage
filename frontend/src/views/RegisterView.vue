<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  phone: '',
  address: '',
})

const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await authStore.register(form.value)
    router.push('/cart')
  } catch (e) {
    if (e.response?.data) {
      const data = e.response.data
      if (typeof data === 'object') {
        const messages = Object.values(data).flat()
        error.value = messages.join(', ')
      } else {
        error.value = data
      }
    } else {
      error.value = 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push({ name: 'login', query: route.query })
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12">
    <div class="w-full max-w-md p-8 bg-white rounded-lg shadow card">
      <h1 class="text-2xl font-bold mb-6 text-center">Create Account</h1>

      <p class="text-center text-muted mb-6">Join Mandaue Public Market E-Compra</p>

      <div v-if="error" class="mb-4 p-3 bg-danger-bg text-danger rounded-sm">
        {{ error }}
      </div>

      <div class="field">
        <span>First Name</span>
        <input
          v-model="form.first_name"
          type="text"
          class="input"
          placeholder="Juan"
          required
        />
      </div>

      <div class="field">
        <span>Last Name</span>
        <input
          v-model="form.last_name"
          type="text"
          class="input"
          placeholder="Dela Cruz"
          required
        />
      </div>

      <div class="field">
        <span>Username</span>
        <input
          v-model="form.username"
          type="text"
          class="input"
          placeholder="username"
          required
          autocomplete="username"
        />
      </div>

      <div class="field">
        <span>Email</span>
        <input
          v-model="form.email"
          type="email"
          class="input"
          placeholder="juan@example.com"
          required
          autocomplete="email"
        />
      </div>

      <div class="field">
        <span>Phone</span>
        <input
          v-model="form.phone"
          type="tel"
          class="input"
          placeholder="09171234567"
          required
        />
      </div>

      <div class="field">
        <span>Address (optional)</span>
        <input
          v-model="form.address"
          type="text"
          class="input"
          placeholder="123 Mandaue City, Cebu"
        />
      </div>

      <div class="field">
        <span>Password</span>
        <input
          v-model="form.password"
          type="password"
          class="input"
          placeholder="••••••••"
          required
          autocomplete="new-password"
          minlength="8"
        />
      </div>

      <div class="field">
        <span>Confirm Password</span>
        <input
          v-model="form.password_confirm"
          type="password"
          class="input"
          placeholder="••••••••"
          required
          autocomplete="new-password"
        />
      </div>

      <button
        @click="handleRegister"
        :disabled="loading"
        class="btn btn-primary btn-block btn-lg mt8"
      >
        {{ loading ? 'Creating Account...' : 'Register' }}
      </button>

      <p class="text-center text-sm muted mt12">
        Already have an account?
        <a @click="goToLogin" class="font-medium" style="color: var(--color-brand); cursor: pointer;">
          Login
        </a>
      </p>
    </div>
  </div>
</template>