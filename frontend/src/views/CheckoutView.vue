<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const cart = ref({ items: [] })
const loading = ref(true)
const error = ref(null)
const processing = ref(false)
const fulfillmentMethod = ref('DELIVERY')

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

// Group items by vendor
const itemsByVendor = computed(() => {
  const grouped = {}
  if (cart.value.items) {
    cart.value.items.forEach(item => {
      const vendorId = item.vendor_id || 'unknown'
      if (!grouped[vendorId]) {
        grouped[vendorId] = {
          vendor_name: item.vendor_name || 'Unknown Vendor',
          vendor_id: vendorId,
          items: [],
          subtotal: 0
        }
      }
      grouped[vendorId].items.push(item)
      grouped[vendorId].subtotal += Number(item.product_price) * Number(item.quantity)
    })
  }
  return grouped
})

const totalAmount = computed(() => {
  return Object.values(itemsByVendor.value).reduce((sum, vendor) => sum + vendor.subtotal, 0)
})

async function fetchCart() {
  try {
    loading.value = true
    const response = await api.get('/cart/')
    cart.value = response.data
  } catch (err) {
    error.value = 'Failed to load cart'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function placeOrder() {
  try {
    processing.value = true
    error.value = null
    const response = await api.post('/checkout/', { fulfillment_code: fulfillmentMethod.value })
    const orderIds = response.data.order_ids
    const transactionIds = response.data.transaction_ids
    alert(`Order placed successfully! Created ${orderIds.length} order(s).`)
    // Redirect to payment screen with the first transaction_id (payment API expects transaction_id)
    if (transactionIds.length > 0) {
      router.push({ name: 'payment', params: { id: transactionIds[0] } })
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Checkout failed'
    console.error(err)
  } finally {
    processing.value = false
  }
}

function goBackToCart() {
  router.push('/cart')
}

onMounted(() => {
  fetchCart()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">Checkout</h1>
      <button
        @click="goBackToCart"
        class="text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        ← Back to Cart
      </button>
    </div>

    <div v-if="loading" class="text-center py-8">
      Loading checkout...
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>

    <div v-else-if="cart.items && cart.items.length > 0">
      <div class="space-y-6">
        <!-- Vendor groups -->
        <div v-for="(vendor, vendorId) in itemsByVendor" :key="vendorId" class="bg-white border border-gray-200 rounded-lg">
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 rounded-t-lg">
            <h3 class="text-lg font-semibold text-gray-900">{{ vendor.vendor_name }}</h3>
          </div>

          <div class="divide-y divide-gray-200">
            <div v-for="item in vendor.items" :key="item.id" class="px-6 py-4 flex items-center gap-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ item.product_name }}</p>
                <p class="text-sm text-gray-500">{{ formatPrice(item.product_price) }} × {{ item.quantity }}</p>
              </div>
              <div class="text-right whitespace-nowrap">
                <p class="text-sm font-medium text-gray-900">{{ formatPrice(Number(item.product_price) * Number(item.quantity)) }}</p>
              </div>
            </div>
          </div>

          <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg flex justify-between items-center">
            <span class="text-sm font-medium text-gray-700">Vendor Subtotal</span>
            <span class="text-lg font-semibold text-gray-900">{{ formatPrice(vendor.subtotal) }}</span>
          </div>
        </div>

        <!-- Fulfillment Method Selection -->
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Fulfillment Method</h3>
          <div class="grid grid-cols-2 gap-4">
            <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                   :class="fulfillmentMethod === 'DELIVERY' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
              <input type="radio" v-model="fulfillmentMethod" value="DELIVERY" class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500" />
              <div>
                <p class="font-medium text-gray-900">Delivery</p>
                <p class="text-sm text-gray-500">Delivered to your address</p>
              </div>
            </label>
            <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                   :class="fulfillmentMethod === 'PICKUP' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
              <input type="radio" v-model="fulfillmentMethod" value="PICKUP" class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500" />
              <div>
                <p class="font-medium text-gray-900">Pickup</p>
                <p class="text-sm text-gray-500">Collect from vendor stall</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Order Total -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div class="flex justify-between items-center mb-4">
            <span class="text-lg font-semibold text-blue-900">Order Total</span>
            <span class="text-2xl font-bold text-blue-900">{{ formatPrice(totalAmount) }}</span>
          </div>

          <button
            @click="placeOrder"
            :disabled="processing"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            <span v-if="processing">Placing Order...</span>
            <span v-else>Place Order ({{ formatPrice(totalAmount) }})</span>
          </button>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500 mb-4">Your cart is empty</p>
      <button @click="goBackToCart" class="text-blue-600 hover:text-blue-800 font-medium">
        Continue Shopping
      </button>
    </div>
  </div>
</template>

<style scoped>
/* CheckoutView specific styles */
</style>