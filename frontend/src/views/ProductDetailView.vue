<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const loading = ref(true)
const quantity = ref(1)
const error = ref('')

const fetchProduct = async () => {
  try {
    const res = await api.get(`catalog/products/${route.params.id}/`)
    product.value = res.data
  } catch (e) {
    error.value = 'Product not found'
  } finally {
    loading.value = false
  }
}

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const addToCart = async () => {
  try {
    await api.post('cart/add/', { product_id: product.value.id, quantity: quantity.value })
    alert(`Added ${quantity.value} to cart!`)
    quantity.value = 1
  } catch (e) {
    alert('Failed to add to cart')
  }
}

const reserveForPickup = async () => {
  // This will call checkout with pickup fulfillment
  router.push({ name: 'checkout', query: { product_id: product.value.id, quantity: quantity.value, fulfillment: 'PICKUP' } })
}

onMounted(fetchProduct)
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <router-link to="/catalog" class="text-gray-600 hover:text-purple-600">← Back</router-link>
        <h1 class="text-xl font-bold text-purple-600">Product Details</h1>
        <router-link to="/cart" class="text-sm text-gray-600 hover:text-purple-600">🛒 Cart</router-link>
      </div>
    </header>

    <div v-if="loading" class="max-w-7xl mx-auto px-4 py-12 text-center">Loading...</div>
    <div v-else-if="error" class="max-w-7xl mx-auto px-4 py-12 text-center text-red-600">{{ error }}</div>
    <div v-else-if="product" class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid md:grid-cols-2 gap-8">
        <!-- Image Gallery -->
        <div>
          <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-4">
            <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">No Image</div>
          </div>
        </div>

        <!-- Details -->
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
          <p class="text-purple-600 text-2xl font-bold mb-4">{{ formatPrice(product.price) }} <span class="text-gray-500 font-normal text-lg">/ {{ product.unit_code }}</span></p>

          <div class="mb-4">
            <span :class="product.availability_code === 'IN_STOCK' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="px-3 py-1 rounded-full text-sm font-medium">
              {{ product.availability_code === 'IN_STOCK' ? 'In Stock' : 'Out of Stock' }}
            </span>
          </div>

          <p class="text-gray-600 mb-6">{{ product.description }}</p>

          <div class="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 class="font-medium text-gray-900 mb-2">Vendor Information</h3>
            <p class="text-gray-600">{{ product.vendor_name }}</p>
            <p class="text-gray-500 text-sm">Stall: {{ product.stall_location }}</p>
            <p class="text-gray-500 text-sm">Section: {{ product.market_section }}</p>
          </div>

          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
              <input v-model.number="quantity" type="number" min="1" :max="product.stock_quantity" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>
          </div>

          <div class="flex gap-4 mt-6">
            <button @click="addToCart" :disabled="product.availability_code !== 'IN_STOCK'" class="flex-1 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 font-medium">
              Add to Cart
            </button>
            <button @click="reserveForPickup" :disabled="product.availability_code !== 'IN_STOCK'" class="flex-1 py-3 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 disabled:opacity-50 font-medium">
              Reserve for Pickup
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>