<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const orders = ref([])
const loading = ref(true)
const error = ref(null)
const updating = ref({})

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

// Status options matching TransactionStatus seed data
const statusOptions = [
  { value: 'PENDING_PAYMENT', label: 'Pending Payment' },
  { value: 'CONFIRMED', label: 'Confirmed' },
  { value: 'PREPARING', label: 'Preparing' },
  { value: 'OUT_FOR_DELIVERY', label: 'Out for Delivery' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'CANCELLED', label: 'Cancelled' },
]

const getStatusLabel = (code) => {
  const found = statusOptions.find(s => s.value === code)
  return found ? found.label : code
}

const getStatusClass = (code) => {
  const classes = {
    PENDING_PAYMENT: 'bg-yellow-100 text-yellow-800',
    CONFIRMED: 'bg-blue-100 text-blue-800',
    PREPARING: 'bg-purple-100 text-purple-800',
    OUT_FOR_DELIVERY: 'bg-orange-100 text-orange-800',
    COMPLETED: 'bg-green-100 text-green-800',
    CANCELLED: 'bg-red-100 text-red-800',
  }
  return classes[code] || 'bg-gray-100 text-gray-800'
}

async function fetchOrders() {
  try {
    loading.value = true
    const response = await api.get('/vendors/pos/')
    orders.value = response.data
  } catch (err) {
    error.value = 'Failed to load orders'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function updateOrderStatus(orderId, newStatusCode) {
  try {
    updating.value[orderId] = true
    await api.post('/vendors/pos/', {
      order_id: orderId,
      status_code: newStatusCode,
    })
    // Refresh orders to get updated status
    await fetchOrders()
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to update status'
    console.error(err)
    // Revert optimistic update by re-fetching
    await fetchOrders()
  } finally {
    updating.value[orderId] = false
  }
}

function canTransition(currentStatus, newStatus) {
  // Basic validation - don't allow transitions to same status
  if (currentStatus === newStatus) return false
  // Don't allow transitions from COMPLETED or CANCELLED
  if (['COMPLETED', 'CANCELLED'].includes(currentStatus)) return false
  return true
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">Vendor POS</h1>
      <button
        @click="fetchOrders"
        :disabled="loading"
        class="text-blue-600 hover:text-blue-800 text-sm font-medium disabled:opacity-50"
      >
        ↻ Refresh
      </button>
    </div>

    <div v-if="loading" class="text-center py-8">
      Loading orders...
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>

    <div v-else-if="orders.length > 0">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 bg-white rounded-lg shadow-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">#{{ order.id }}</div>
                <div class="text-xs text-gray-500" v-if="order.transaction?.reference_no">
                  {{ order.transaction.reference_no }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ order.user?.username || order.user_email || 'Unknown' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(order.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ formatPrice(order.total_amount) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="['inline-flex px-2 py-1 text-xs font-semibold rounded-full', getStatusClass(order.status_code?.code)]"
                >
                  {{ getStatusLabel(order.status_code?.code) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <select
                  :value="order.status_code?.code"
                  @change="updateOrderStatus(order.id, $event.target.value)"
                  :disabled="updating[order.id] || ['COMPLETED', 'CANCELLED'].includes(order.status_code?.code)"
                  class="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option v-for="status in statusOptions" :key="status.value" :value="status.value" :disabled="!canTransition(order.status_code?.code, status.value)">
                    {{ status.label }}
                  </option>
                </select>
                <div v-if="updating[order.id]" class="text-xs text-blue-600 mt-1">Updating...</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <div class="text-6xl mb-4">📋</div>
      <p class="text-gray-500 mb-4">No orders found</p>
      <p class="text-sm text-gray-400">Orders will appear here when customers place them</p>
    </div>
  </div>
</template>

<style scoped>
/* VendorPOSView specific styles */
</style>