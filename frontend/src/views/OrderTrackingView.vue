<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const order = ref(null)
const loading = ref(true)
const error = ref('')

const statusSteps = [
  { code: 'PENDING_PAYMENT', label: 'Pending Payment', icon: '⏳' },
  { code: 'CONFIRMED', label: 'Confirmed', icon: '✅' },
  { code: 'PREPARING', label: 'Preparing', icon: '📦' },
  { code: 'READY_FOR_PICKUP', label: 'Ready for Pickup', icon: '🔔' },
  { code: 'OUT_FOR_DELIVERY', label: 'Out for Delivery', icon: '🚚' },
  { code: 'COMPLETED', label: 'Completed', icon: '🎉' },
]

const fetchOrder = async () => {
  try {
    const res = await api.get(`orders/${route.params.id}/`)
    order.value = res.data
  } catch (e) {
    error.value = 'Order not found'
  } finally {
    loading.value = false
  }
}

const currentStepIndex = computed(() => {
  if (!order.value?.status_code) return -1
  return statusSteps.findIndex(s => s.code === order.value.status_code)
})

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(fetchOrder)
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <router-link to="/catalog" class="text-gray-600 hover:text-purple-600">← Back</router-link>
        <h1 class="text-xl font-bold text-purple-600">Order Tracking</h1>
      </div>
    </header>

    <div v-if="loading" class="max-w-7xl mx-auto px-4 py-12 text-center">Loading...</div>
    <div v-else-if="error" class="max-w-7xl mx-auto px-4 py-12 text-center text-red-600">{{ error }}</div>
    <div v-else-if="order" class="max-w-7xl mx-auto px-4 py-8">
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h2 class="text-xl font-bold">Order #{{ order.id }}</h2>
            <p class="text-gray-500">{{ formatDate(order.created_at) }}</p>
          </div>
          <span :class="order.status_code === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'" class="px-3 py-1 rounded-full text-sm font-medium">
            {{ order.status_display || order.status_code }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div><span class="text-gray-500">Vendor:</span> {{ order.vendor_name || order.vendor }}</div>
          <div><span class="text-gray-500">Fulfillment:</span> {{ order.fulfillment_display || order.fulfillment_code }}</div>
          <div><span class="text-gray-500">Total:</span> <span class="font-bold text-purple-600">{{ formatPrice(order.total_amount) }}</span></div>
        </div>
      </div>

      <!-- Status Timeline -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-bold mb-6">Status Timeline</h3>
        <div class="relative">
          <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />
          <div v-for="(step, index) in statusSteps" :key="step.code" class="relative pl-14 mb-6 last:mb-0">
            <div class="absolute left-6 top-1 w-3 h-3 rounded-full border-2"
                 :class="index <= currentStepIndex ? 'bg-purple-600 border-purple-600' : 'bg-white border-gray-300'">
              <span v-if="index <= currentStepIndex" class="absolute inset-0 flex items-center justify-center text-white text-xs">✓</span>
            </div>
            <div class="pb-4">
              <p class="font-medium" :class="index <= currentStepIndex ? 'text-purple-600' : 'text-gray-500'">
                {{ step.icon }} {{ step.label }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Items -->
      <div class="mt-6 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-bold mb-4">Items</h3>
        <div v-for="item in order.items" :key="item.id" class="flex justify-between py-2 border-b last:border-0">
          <div>
            <p class="font-medium">{{ item.product_name }}</p>
            <p class="text-sm text-gray-500">Qty: {{ item.quantity }} × {{ formatPrice(item.unit_price) }}</p>
          </div>
          <p class="font-medium">{{ formatPrice(item.quantity * item.unit_price) }}</p>
        </div>
        <div class="flex justify-between pt-4 font-bold text-lg">
          <span>Total</span>
          <span>{{ formatPrice(order.total_amount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* OrderTrackingView specific styles */
</style>