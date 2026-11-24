<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const product = ref(null)
const comparisonProducts = ref([])
const similarProducts = ref([])
const vendor = ref(null)
const loading = ref(true)
const quantity = ref(1)
const error = ref('')

const fetchProduct = async () => {
  try {
    const res = await api.get(`catalog/products/${route.params.id}/`)
    product.value = res.data
    // Fetch comparison products (same comparison_group)
    if (res.data.comparison_group) {
      await fetchComparisonProducts(res.data.comparison_group, res.data.id)
    }
    // Fetch similar products (same category)
    if (res.data.category) {
      await fetchSimilarProducts(res.data.category, res.data.id)
    }
    // Fetch vendor details
    if (res.data.vendor_id) {
      await fetchVendor(res.data.vendor_id)
    }
  } catch (e) {
    error.value = 'Product not found'
  } finally {
    loading.value = false
  }
}

const fetchComparisonProducts = async (comparisonGroup, excludeId) => {
  try {
    const res = await api.get(`catalog/products/?comparison_group=${comparisonGroup}&page_size=10`)
    comparisonProducts.value = (res.data.results || res.data).filter(p => p.id !== excludeId)
  } catch (e) {
    console.error('Failed to fetch comparison products:', e)
  }
}

const fetchSimilarProducts = async (category, excludeId) => {
  try {
    const res = await api.get(`catalog/products/?category=${category}&page_size=8`)
    similarProducts.value = (res.data.results || res.data).filter(p => p.id !== excludeId).slice(0, 4)
  } catch (e) {
    console.error('Failed to fetch similar products:', e)
  }
}

const fetchVendor = async (vendorId) => {
  try {
    const res = await api.get(`catalog/vendors/${vendorId}/`)
    vendor.value = res.data
  } catch (e) {
    console.error('Failed to fetch vendor:', e)
  }
}

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-PH', { day: '2-digit', month: 'short', year: 'numeric' })
}

const categoryIcons = {
  'Fish': '🐟',
  'Meat': '🥩',
  'Poultry': '🍗',
  'Fruits': '🍎',
  'Vegetables': '🥬',
  'Rice': '🍚',
  'Dry goods': '🫙',
  'Spices': '🧂',
  'Others': '🧺',
}

const getCategoryIcon = (name) => categoryIcons[name] || '📦'

const isLowestPrice = computed(() => {
  if (!product.value || comparisonProducts.value.length === 0) return false
  const currentPrice = Number(product.value.price)
  return comparisonProducts.value.every(p => Number(p.price) >= currentPrice)
})

const lowestComparisonPrice = computed(() => {
  if (comparisonProducts.value.length === 0) return null
  return Math.min(...comparisonProducts.value.map(p => Number(p.price)))
})

const comparisonPricesDisplay = computed(() => {
  if (comparisonProducts.value.length === 0) return null
  const prices = [...new Set(comparisonProducts.value.map(p => Number(p.price)))]
    .sort((a, b) => a - b)
    .slice(0, 3)
    .map(p => formatPrice(p))
  return prices.join(' · ')
})

const subtotal = computed(() => {
  if (!product.value) return 0
  return Number(product.value.price) * Number(quantity.value)
})

const stockQuantity = computed(() => {
  if (!product.value) return 0
  return Number(product.value.stock_quantity || 0)
})

const maxQuantity = computed(() => Math.max(1, stockQuantity.value))

const addToCart = async () => {
  if (!product.value || product.value.availability !== 'IN_STOCK') return
  try {
    await api.post('cart/add/', { product_id: product.value.id, quantity: quantity.value })
    alert(`Added ${quantity.value} ${product.value.unit || 'kg'} to cart!`)
    quantity.value = 1
  } catch (e) {
    alert('Failed to add to cart')
  }
}

const reserveForPickup = async () => {
  if (!product.value || product.value.availability !== 'IN_STOCK') return
  // Navigate to checkout with pickup fulfillment and pre-filled product
  router.push({
    name: 'checkout',
    query: {
      product_id: product.value.id,
      quantity: quantity.value,
      fulfillment: 'PICKUP'
    }
  })
}

const goToProduct = (p) => {
  router.push({ name: 'product-detail', params: { id: p.id } })
}

const isProductFavorited = ref(false)

const toggleFavoriteProduct = async () => {
  if (!product.value) return
  try {
    if (authStore.isAuthenticated) {
      if (isProductFavorited.value) {
        await api.delete(`favorites/products/${product.value.id}/`)
        isProductFavorited.value = false
        alert('Removed from favorites!')
      } else {
        await api.post('favorites/products/', { product_id: product.value.id })
        isProductFavorited.value = true
        alert('Added to favorites!')
      }
    } else {
      router.push('/login')
    }
  } catch (e) {
    alert('Failed to update favorites')
  }
}

const toggleFavoriteVendor = async () => {
  if (!vendor.value) return
  try {
    if (authStore.isAuthenticated) {
      await api.post('favorites/vendors/', { vendor_id: vendor.value.id })
      alert('Added to favorites!')
    } else {
      router.push('/login')
    }
  } catch (e) {
    alert('Failed to add to favorites')
  }
}

onMounted(fetchProduct)

// Reset quantity when product changes
watch(() => route.params.id, () => {
  quantity.value = 1
  fetchProduct()
})
</script>

<template>
  <div class="min-h-screen bg-bg">
    <!-- Navbar -->
    <Navbar />

    <main class="page">
      <div class="wrap stack">

        <!-- Breadcrumb -->
        <nav class="small muted" aria-label="Breadcrumb" v-if="product">
          <router-link to="/catalog" class="underline">Marketplace</router-link>
          <span class="mx-2">›</span>
          <router-link :to="{ name: 'catalog', query: { category: product.category } }" class="underline">{{ product.category_name || product.category }}</router-link>
          <span class="mx-2">›</span>
          <span>{{ product.name }}</span>
        </nav>

        <div v-if="loading" class="text-center py-12">Loading…</div>
        <div v-else-if="error" class="text-center py-12">
          <p class="text-danger">{{ error }}</p>
          <router-link to="/catalog" class="btn btn-primary mt12">← Back to Marketplace</router-link>
        </div>

        <div v-else-if="product" class="stack" style="gap: 24px;">

          <!-- Gallery + Buy Box -->
          <div class="grid grid-2" style="grid-template-columns: 1.1fr 1fr; align-items: start; gap: 24px;">

            <!-- Gallery -->
            <div class="stack" style="gap: 10px;">
              <div class="card" style="padding: 0; overflow: hidden;">
                <div style="height: 280px; display: grid; place-items: center; font-size: 6rem; background: var(--color-brand-light); border-bottom: 1px solid var(--color-line);">
                  <img
                    v-if="product.image_url"
                    :src="product.image_url"
                    :alt="product.name"
                    class="w-full h-full object-cover"
                  >
                  <span v-else>{{ getCategoryIcon(product.category_name || product.category) }}</span>
                </div>
              </div>

              <!-- Thumbnails -->
              <div class="row" style="gap: 10px;">
                <div
                  class="thumb-active"
                  style="flex: 1; height: 62px; display: grid; place-items: center; font-size: 1.7rem; background: var(--color-brand-light); border: 2px solid var(--color-brand); border-radius: var(--radius-sm);"
                >
                  <img
                    v-if="product.image_url"
                    :src="product.image_url"
                    :alt="product.name"
                    style="max-width: 100%; max-height: 100%; object-fit: contain;"
                  >
                  <span v-else>{{ getCategoryIcon(product.category_name || product.category) }}</span>
                </div>
                <div
                  v-for="(thumb, idx) in [1,2,3]"
                  :key="idx"
                  style="flex: 1; height: 62px; display: grid; place-items: center; font-size: 1.7rem; background: var(--color-neutral-bg); border: 1px solid var(--color-line); border-radius: var(--radius-sm);"
                >
                  <span>{{ getCategoryIcon(product.category_name || product.category) }}</span>
                </div>
              </div>
            </div>

            <!-- Buy Box -->
            <div class="stack" style="gap: 16px;">

              <!-- Badges -->
              <div class="row-wrap mb8" style="gap: 8px;">
                <span class="badge badge-brand">{{ product.category_name || product.category }}</span>
                <span class="badge" :class="product.availability === 'IN_STOCK' ? 'badge-ok' : 'badge-danger'">
                  <i class="dot" v-if="product.availability === 'IN_STOCK'"></i>
                  {{ product.availability === 'IN_STOCK' ? 'In stock' : 'Out of stock' }}
                </span>
                <span v-if="isLowestPrice" class="badge badge-accent">Lowest price in market</span>
              </div>

              <h1 class="mb0">{{ product.name }}</h1>
              <p class="muted">{{ product.description }}</p>

              <!-- Price Card -->
              <div class="card">
                <div class="row-between" style="align-items: flex-start;">
                  <div>
                    <div class="price price-lg" style="font-size: 2rem;">{{ formatPrice(product.price) }}</div>
                    <div class="unit">per {{ product.unit || 'kilogram (kg)' }}</div>
                  </div>
                  <div v-if="comparisonProducts.length > 0" class="center" style="min-width: 140px;">
                    <div class="tiny muted">Other vendors</div>
                    <div class="small">{{ comparisonPricesDisplay }}</div>
                    <router-link to="/price-comparison" class="tiny" :query="{ group: product.comparison_group }">Compare all {{ comparisonProducts.length + 1 }} →</router-link>
                  </div>
                </div>

                <hr class="divider">

                <!-- Quantity + Subtotal -->
                <div class="row" style="align-items: flex-end; gap: 16px;">
                  <label class="field mb0" style="flex: 1;">
                    <span>Quantity ({{ product.unit || 'kg' }})</span>
                    <input
                      v-model.number="quantity"
                      type="number"
                      :min="1"
                      :max="maxQuantity"
                      class="input"
                      aria-label="Quantity"
                      @input="quantity = Math.min(Math.max(1, quantity || 1), maxQuantity)"
                    >
                  </label>
                  <div class="field mb0" style="flex: 1;">
                    <span>Subtotal</span>
                    <div class="price" style="font-size: 1.3rem; padding: 8px 0;">{{ formatPrice(subtotal) }}</div>
                  </div>
                </div>

                <div class="note mt12 tiny">
                  Only <strong>{{ stockQuantity }} {{ product.unit || 'kg' }}</strong> available — the vendor confirms stock when the order is accepted.
                </div>

                <!-- Action Buttons -->
                <div class="stack mt12" style="gap: 12px;">
                  <button
                    @click="addToCart"
                    :disabled="product.availability !== 'IN_STOCK' || stockQuantity <= 0"
                    class="btn btn-primary btn-lg btn-block"
                  >
                    Add to cart
                  </button>
                  <button
                    @click="reserveForPickup"
                    :disabled="product.availability !== 'IN_STOCK' || stockQuantity <= 0"
                    class="btn btn-accent btn-lg btn-block"
                  >
                    Reserve for pickup
                  </button>
                  <button
                    @click="toggleFavoriteProduct"
                    class="btn btn-ghost btn-lg btn-block"
                    :class="{ 'btn-danger': isProductFavorited }"
                  >
                    {{ isProductFavorited ? '♥' : '♡' }} Favorite product
                  </button>
                </div>
                <div class="center tiny muted mt8">Reserve now, pay at the stall — or pay online and have it delivered.</div>
              </div>

              <!-- Vendor Card -->
              <div class="card" v-if="vendor">
                <div class="card-head row-between">
                  <h3>Sold by</h3>
                  <button
                    @click="toggleFavoriteVendor"
                    class="btn btn-ghost btn-sm"
                    style="padding: 4px 8px; font-size: .8rem;"
                  >
                    ♡ Favorite vendor
                  </button>
                </div>
                <div class="row-between">
                  <div>
                    <div style="font-weight: 650;">{{ vendor.name }}</div>
                    <div class="small muted">📍 {{ vendor.stall_location }} · {{ vendor.section_name || vendor.section }}</div>
                    <div class="small muted">📞 {{ vendor.contact_phone || '—' }}</div>
                  </div>
                  <div class="center">
                    <div class="badge badge-ok">Verified vendor</div>
                    <div class="tiny muted mt8">{{ vendor.product_count || 0 }} products listed</div>
                  </div>
                </div>
                <div class="card-foot row-wrap">
                  <router-link to="/market-map" class="btn btn-sm">Show on market map</router-link>
                  <router-link :to="{ name: 'catalog', query: { vendor: vendor.id } }" class="btn btn-sm">See all products</router-link>
                </div>
              </div>

              <!-- Specs / Details -->
              <div class="card">
                <div class="card-head"><h3>Details</h3></div>
                <dl class="kv">
                  <dt>Unit of measure</dt><dd>{{ product.unit_name || product.unit || '—' }}</dd>
                  <dt>Comparison group</dt><dd class="mono">{{ product.comparison_group || product.comparison_group_name || '—' }}</dd>
                  <dt>Stock on hand</dt><dd>{{ stockQuantity }} {{ product.unit || 'kg' }}</dd>
                  <dt>Category</dt><dd>{{ product.category_name || product.category }}</dd>
                  <dt>Stall</dt><dd>{{ product.stall_location }}</dd>
                  <dt>Listed</dt><dd>{{ formatDate(product.created_at) }}</dd>
                </dl>
                <div class="note mt12 tiny">
                  <strong>Why "comparison group"?</strong> It is the key that lets E-Compra rank this {{ product.name.toLowerCase() }} against
                  the same item at another stall, even if one vendor prices per gram and another per sack.
                </div>
              </div>

            </div>
          </div>

          <!-- Similar Products -->
          <section v-if="similarProducts.length > 0">
            <h2>Similar products in {{ product.category_name || product.category }}</h2>
            <div class="grid grid-4">
              <article
                v-for="p in similarProducts"
                :key="p.id"
                class="pcard"
                @click="goToProduct(p)"
              >
                <div class="thumb">{{ getCategoryIcon(p.category_name || p.category) }}</div>
                <div class="body">
                  <h3 class="name">{{ p.name }}</h3>
                  <p class="vendor">{{ p.vendor_name }} · {{ p.stall_location }}</p>
                  <div class="foot">
                    <span class="price price-sm">{{ formatPrice(p.price) }} <span class="unit">/ {{ p.unit || 'kg' }}</span></span>
                    <button
                      @click.stop="addToCart"
                      :disabled="p.availability !== 'IN_STOCK'"
                      class="btn btn-sm"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </article>
            </div>
          </section>

        </div>

      </div>
    </main>

    <footer class="foot">
      <div class="wrap row-between">
        <span>E-Compra · CCS630 Advance Database Systems capstone</span>
        <span>All prices in Philippine pesos (₱)</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Gallery main image */
.card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Thumbnail active state */
.thumb-active {
  border-color: var(--color-brand) !important;
  background: var(--color-brand-light) !important;
}

/* Breadcrumb */
nav.small.muted a:hover {
  opacity: 0.8;
}

/* Badge dot for in-stock */
.badge .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  margin-right: 6px;
  vertical-align: middle;
}

/* Price comparison link */
.tiny a:hover {
  opacity: 0.8;
}

/* Quantity input */
.field input[type="number"] {
  -moz-appearance: textfield;
}
.field input[type="number"]::-webkit-outer-spin-button,
.field input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Responsive */
@media (max-width: 860px) {
  .grid-2 {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 640px) {
  .grid-4 {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 480px) {
  .grid-4 {
    grid-template-columns: 1fr !important;
  }
}
</style>