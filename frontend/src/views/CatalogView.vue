<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const products = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref('')
const page = ref(1)
const pageSize = 20
const totalCount = ref(0)

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.append('q', search.value)
    if (selectedCategory.value) params.append('category', selectedCategory.value)
    params.append('page', page.value)
    params.append('page_size', pageSize)

    const res = await api.get(`catalog/products/?${params.toString()}`)
    products.value = res.data.results || res.data
    totalCount.value = res.data.count || products.value.length
  } catch (e) {
    console.error('Failed to fetch products:', e)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('catalog/categories/')
    categories.value = res.data.results || res.data
  } catch (e) {
    console.error('Failed to fetch categories:', e)
  }
}

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const goToProduct = (product) => {
  router.push({ name: 'product-detail', params: { id: product.id } })
}

const addToCart = async (product) => {
  try {
    await api.post('cart/add/', { product_id: product.id, quantity: 1 })
    alert('Added to cart!')
  } catch (e) {
    alert('Failed to add to cart')
  }
}

onMounted(() => {
  fetchProducts()
  fetchCategories()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-xl font-bold text-purple-600">E-Compra</h1>
        <router-link to="/cart" class="text-sm text-gray-600 hover:text-purple-600">🛒 Cart</router-link>
      </div>
    </header>

    <!-- Search & Filters -->
    <div class="max-w-7xl mx-auto px-4 py-4">
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <div class="flex-1">
          <input
            v-model="search"
            @keyup.enter="page = 1; fetchProducts()"
            placeholder="Search products..."
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
        <select
          v-model="selectedCategory"
          @change="page = 1; fetchProducts()"
          class="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
    </div>

    <!-- Product Grid -->
    <main class="max-w-7xl mx-auto px-4 pb-8">
      <div v-if="loading" class="text-center py-12">Loading...</div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="product in products" :key="product.id"
             @click="goToProduct(product)"
             class="bg-white rounded-lg shadow hover:shadow-md transition cursor-pointer overflow-hidden">
          <div class="aspect-square bg-gray-100">
            <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">No Image</div>
          </div>
          <div class="p-4">
            <h3 class="font-medium text-gray-900 line-clamp-2 mb-1">{{ product.name }}</h3>
            <p class="text-purple-600 font-bold mb-2">{{ formatPrice(product.price) }} / {{ product.unit }}</p>
            <p class="text-xs text-gray-500 mb-2">{{ product.vendor_name }} • {{ product.stall_location }}</p>
            <div class="flex items-center justify-between">
              <span :class="product.availability === 'IN_STOCK' ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
                {{ product.availability === 'IN_STOCK' ? 'In Stock' : 'Out of Stock' }}
              </span>
              <button
                @click.stop="addToCart(product)"
                :disabled="product.availability !== 'IN_STOCK'"
                class="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 disabled:bg-gray-300"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalCount > pageSize" class="flex justify-center gap-2 mt-6">
        <button @click="page > 1 && (page--, fetchProducts())" :disabled="page === 1" class="px-4 py-2 border rounded disabled:opacity-50">Previous</button>
        <span class="flex items-center px-4">Page {{ page }}</span>
        <button @click="page * pageSize < totalCount && (page++, fetchProducts())" :disabled="page * pageSize >= totalCount" class="px-4 py-2 border rounded disabled:opacity-50">Next</button>
      </div>
    </main>
  </div>
</template>