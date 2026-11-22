<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const transactionId = route.params.id || route.query.transaction_id
const loading = ref(true)
const processing = ref(false)
const error = ref(null)
const success = ref(false)

const transaction = ref(null)
const order = ref(null)

const paymentMethod = ref('cash')
const providerReference = ref('')

const paymentMethods = [
  { value: 'cash', label: 'Cash on Delivery' },
  { value: 'card', label: 'Credit/Debit Card' },
  { value: 'gcash', label: 'GCash' },
  { value: 'maya', label: 'Maya' },
]

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

async function fetchTransaction() {
  if (!transactionId) {
    error.value = 'No transaction ID provided'
    loading.value = false
    return
  }

  try {
    loading.value = true
    // Fetch order details to get transaction info
    // The checkout endpoint returns order_ids, we need to get the transaction from an order
    // For now, we'll try to fetch order and then its transaction
    const response = await api.get(`/orders/${transactionId}/`)
    order.value = response.data

    // If order has transactions, use the first one
    if (order.value.transactions && order.value.transactions.length > 0) {
      transaction.value = order.value.transactions[0]
    } else if (order.value.transaction) {
      transaction.value = order.value.transaction
    }
  } catch (err) {
    // Try fetching transaction directly if order fetch fails
    try {
      const txnResponse = await api.get(`/transactions/${transactionId}/`)
      transaction.value = txnResponse.data
    } catch (txnErr) {
      error.value = 'Failed to load transaction details'
      console.error(txnErr)
    }
  } finally {
    loading.value = false
  }
}

const amount = computed(() => {
  if (transaction.value?.amount) return transaction.value.amount
  if (order.value?.total_amount) return order.value.total_amount
  return '0.00'
})

async function processPayment() {
  if (!transaction.value) {
    error.value = 'No transaction to pay for'
    return
  }

  if (!providerReference.value.trim() && paymentMethod.value !== 'cash') {
    error.value = 'Please enter a reference number'
    return
  }

  try {
    processing.value = true
    error.value = null

    const response = await api.post('/payment/', {
      transaction_id: transaction.value.id,
      provider: paymentMethod.value,
      provider_reference: providerReference.value || `MANUAL-${Date.now()}`,
      amount: amount.value,
    })

    success.value = true
    setTimeout(() => {
      router.push('/confirmation')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Payment failed'
    console.error(err)
  } finally {
    processing.value = false
  }
}

function goBack() {
  router.push('/checkout')
}

onMounted(() => {
  fetchTransaction()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">Payment</h1>
      <button @click="goBack" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
        ← Back to Checkout
      </button>
    </div>

    <div v-if="loading" class="text-center py-8">
      Loading payment details...
    </div>

    <div v-else-if="error && !success" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>

    <div v-else-if="success" class="bg-green-100 border border-green-400 text-green-700 px-4 py-6 rounded text-center">
      <div class="text-6xl mb-4">✓</div>
      <h2 class="text-2xl font-bold mb-2">Payment Successful!</h2>
      <p class="mb-4">Your payment of {{ formatPrice(amount) }} has been processed.</p>
      <p class="text-sm opacity-80">Redirecting to confirmation...</p>
    </div>

    <div v-else-if="transaction || order" class="space-y-6">
      <!-- Order/Transaction Summary -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Order Summary</h3>
        <div v-if="order" class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Order ID</span>
            <span class="font-medium">#{{ order.id }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Vendor</span>
            <span class="font-medium">{{ order.vendor_name || order.vendor }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Status</span>
            <span class="font-medium capitalize">{{ order.status_code?.code?.toLowerCase().replace('_', ' ') || order.status }}</span>
          </div>
        </div>
        <div v-else-if="transaction" class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Transaction ID</span>
            <span class="font-medium">#{{ transaction.id }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Reference</span>
            <span class="font-medium">{{ transaction.reference_no }}</span>
          </div>
        </div>
        <div class="border-t border-gray-200 pt-4 mt-4 flex justify-between">
          <span class="text-lg font-semibold text-gray-900">Amount Due</span>
          <span class="text-2xl font-bold text-blue-600">{{ formatPrice(amount) }}</span>
        </div>
      </div>

      <!-- Payment Method Selection -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Payment Method</h3>
        <div class="space-y-3">
          <label v-for="method in paymentMethods" :key="method.value" class="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
            <input
              type="radio"
              v-model="paymentMethod"
              :value="method.value"
              class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            >
            <span class="ml-3 text-gray-900">{{ method.label }}</span>
          </label>
        </div>

        <!-- Provider Reference Input -->
        <div v-if="paymentMethod !== 'cash'" class="mt-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Reference Number <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            v-model="providerReference"
            :placeholder="paymentMethod === 'gcash' ? 'Enter GCash reference number' : paymentMethod === 'maya' ? 'Enter Maya reference number' : 'Enter card transaction reference'"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
          <p class="text-xs text-gray-500 mt-1">Enter the transaction reference from your payment provider</p>
        </div>

        <div v-if="paymentMethod === 'cash'" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-sm text-yellow-800">
            <strong>Cash on Delivery:</strong> No reference number needed. Payment will be collected upon delivery.
          </p>
        </div>
      </div>

      <!-- Pay Button -->
      <button
        @click="processPayment"
        :disabled="processing"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-6 py-3 rounded-lg font-medium text-lg transition-colors"
      >
        <span v-if="processing">Processing...</span>
        <span v-else>Pay {{ formatPrice(amount) }}</span>
      </button>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500 mb-4">No transaction found</p>
      <button @click="goBack" class="text-blue-600 hover:text-blue-800 font-medium">
        Back to Checkout
      </button>
    </div>
  </div>
</template>

<style scoped>
/* PaymentView specific styles */
</style>