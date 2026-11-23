<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const cart = ref({ items: [] })
const loading = ref(true)
const error = ref(null)

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

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

async function updateQuantity(itemId, quantity) {
  try {
    await api.post('/cart/update_item/', { item_id: itemId, quantity })
    await fetchCart()
  } catch (err) {
    error.value = 'Failed to update quantity'
    console.error(err)
  }
}

async function removeItem(itemId) {
  try {
    await api.post('/cart/remove_item/', { item_id: itemId })
    await fetchCart()
  } catch (err) {
    error.value = 'Failed to remove item'
    console.error(err)
  }
}

async function checkout() {
  try {
    error.value = null
    await api.post('/checkout/')
    alert('Checkout complete! Orders created.')
    await fetchCart()
  } catch (err) {
    error.value = 'Checkout failed'
    console.error(err)
  }
}

onMounted(() => {
  fetchCart()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Shopping Cart</h1>

    <div v-if="loading" class="text-center py-8">
      Loading cart...
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>

    <div v-else-if="cart.items && cart.items.length > 0">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subtotal</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="item in cart.items" :key="item.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ item.product_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatPrice(item.product_price) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <button
                    @click="updateQuantity(item.id, item.quantity - 1)"
                    class="px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
                    :disabled="item.quantity <= 1"
                  >
                    -
                  </button>
                  <span class="w-8 text-center">{{ item.quantity }}</span>
                  <button
                    @click="updateQuantity(item.id, item.quantity + 1)"
                    class="px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
                  >
                    +
                  </button>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ formatPrice(item.product_price * item.quantity) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="removeItem(item.id)"
                  class="text-red-600 hover:text-red-900 text-sm font-medium"
                >
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-6 text-right">
        <div class="text-lg font-semibold mb-4">
          Total: {{ formatPrice(cart.total_amount) }}
        </div>
        <button
          @click="checkout"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Checkout
        </button>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500 mb-4">Your cart is empty</p>
      <router-link to="/catalog" class="text-blue-600 hover:text-blue-800">
        Continue Shopping
      </router-link>
    </div>
  </div>
</template>

<style scoped>
/* CartView specific styles can go here */
</style>