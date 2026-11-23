<script setup>
import { onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const showNavbar = computed(() => route.name !== 'login')

onMounted(async () => {
  await authStore.init()
})
</script>

<template>
  <Navbar v-if="showNavbar" />
  <router-view />
</template>
