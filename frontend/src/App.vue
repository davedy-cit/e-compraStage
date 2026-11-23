<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  await authStore.init()
})
</script>

<template>
  <router-view />
</template>