<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Track favorited product IDs for instant UI feedback
const favoritedProducts = ref(new Set())
const favoriting = ref(new Set())

const products = ref([])
const categories = ref([])
const vendors = ref([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref('')
const page = ref(1)
const pageSize = 20
const totalCount = ref(0)

const featuredProducts = ref([])
const featuredVendors = ref([])

// Filter state
const selectedCategories = ref([])
const priceMin = ref('')
const priceMax = ref('')
const selectedAvailabilities = ref([])
const selectedVendors = ref([])
const showFilters = ref(false) // mobile filter drawer
const sortBy = ref('')
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)

onMounted(() => {
  const updateWidth = () => { windowWidth.value = window.innerWidth }
  window.addEventListener('resize', updateWidth)
  updateWidth()
  return () => window.removeEventListener('resize', updateWidth)
})

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.append('q', search.value)
    if (selectedCategory.value) params.append('category', selectedCategory.value)
    if (selectedCategories.value.length > 0) params.append('categories', selectedCategories.value.join(','))
    if (priceMin.value) params.append('price_min', priceMin.value)
    if (priceMax.value) params.append('price_max', priceMax.value)
    if (selectedAvailabilities.value.length > 0) params.append('availabilities', selectedAvailabilities.value.join(','))
    if (selectedVendors.value.length > 0) params.append('vendors', selectedVendors.value.join(','))
    if (sortBy.value) params.append('ordering', sortBy.value)
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

const fetchVendors = async () => {
  try {
    const res = await api.get('catalog/vendors/')
    vendors.value = res.data.results || res.data
  } catch (e) {
    console.error('Failed to fetch vendors:', e)
  }
}

const fetchFeaturedProducts = async () => {
  try {
    const res = await api.get('catalog/products/featured/')
    featuredProducts.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Failed to fetch featured products:', e)
    featuredProducts.value = []
  }
}

const fetchFeaturedVendors = async () => {
  try {
    const res = await api.get('catalog/vendors/featured/')
    featuredVendors.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Failed to fetch featured vendors:', e)
    featuredVendors.value = []
  }
}

// Initialize from URL query params
onMounted(() => {
  // Initialize search from query param
  if (route.query.q) search.value = route.query.q
  if (route.query.category) selectedCategory.value = route.query.category
  if (route.query.ordering) sortBy.value = route.query.ordering
  // Note: multi-value query params would need array parsing

  fetchProducts()
  fetchCategories()
  fetchVendors()
  fetchFeaturedProducts()
  fetchFeaturedVendors()
})

// Watch for route query changes (e.g., from category chips)
watch(() => route.query, (newQuery) => {
  if (newQuery.q !== undefined) search.value = newQuery.q || ''
  if (newQuery.category !== undefined) selectedCategory.value = newQuery.category || ''
  if (newQuery.ordering !== undefined) sortBy.value = newQuery.ordering || ''
  page.value = 1
  fetchProducts()
}, { deep: true })

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

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

const goToProduct = (product) => {
  router.push({ name: 'product-detail', params: { id: product.id } })
}

const goToSearchResults = (categoryId = null, query = null) => {
  const params = {}
  if (categoryId) params.category = categoryId
  if (query) params.q = query
  router.push({ name: 'catalog', query: params })
}

const addToCart = async (product) => {
  try {
    await api.post('cart/add/', { product_id: product.id, quantity: 1 })
    alert('Added to cart!')
  } catch (e) {
    alert('Failed to add to cart')
  }
}

const toggleFavorite = async (product) => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  const isFavorited = favoritedProducts.value.has(product.id)
  favoriting.value.add(product.id)

  try {
    if (isFavorited) {
      await api.delete(`favorites/products/${product.id}/`)
      favoritedProducts.value.delete(product.id)
    } else {
      await api.post('favorites/products/', { product_id: product.id })
      favoritedProducts.value.add(product.id)
    }
  } catch (e) {
    console.error('Failed to toggle favorite:', e)
    alert(isFavorited ? 'Failed to remove from favorites' : 'Failed to add to favorites')
  } finally {
    favoriting.value.delete(product.id)
  }
}

const isFavorited = (product) => favoritedProducts.value.has(product.id)

// Compute best value (cheapest) per comparison group
const bestValueMap = computed(() => {
  const map = new Map()
  // Group products by comparison_group (or by name as fallback)
  const groups = {}
  products.value.forEach(p => {
    const key = p.comparison_group || p.name
    if (!groups[key]) groups[key] = []
    groups[key].push(p)
  })
  Object.entries(groups).forEach(([key, group]) => {
    if (group.length > 1) {
      const cheapest = group.reduce((min, p) => Number(p.price) < Number(min.price) ? p : min)
      map.set(cheapest.id, true)
      // Mark price deltas for others
      group.forEach(p => {
        if (p.id !== cheapest.id) {
          const delta = Number(p.price) - Number(cheapest.price)
          p.priceDelta = delta > 0 ? `+${formatPrice(delta)}` : null
        }
      })
    }
  })
  return map
})

const isBestValue = (product) => bestValueMap.value.has(product.id)
const getPriceDelta = (product) => product.priceDelta || null

const availabilityOptions = [
  { value: 'IN_STOCK', label: 'In stock' },
  { value: 'LOW_STOCK', label: 'Low stock' },
  { value: 'OUT_OF_STOCK', label: 'Out of stock' },
]

const sortOptions = [
  { value: '', label: 'Price — lowest first' },
  { value: '-price', label: 'Price — highest first' },
  { value: 'vendor', label: 'Vendor name' },
  { value: '-availability', label: 'Availability' },
]

const clearFilters = () => {
  selectedCategories.value = []
  priceMin.value = ''
  priceMax.value = ''
  selectedAvailabilities.value = []
  selectedVendors.value = []
  page.value = 1
  fetchProducts()
}

const hasActiveFilters = computed(() =>
  selectedCategories.value.length > 0 ||
  priceMin.value !== '' ||
  priceMax.value !== '' ||
  selectedAvailabilities.value.length > 0 ||
  selectedVendors.value.length > 0
)

// Second result group: "Also in [category]" - products from same category not in main results
const alsoInCategory = computed(() => {
  if (!selectedCategory.value || products.value.length === 0) return []
  const mainIds = new Set(products.value.map(p => p.id))
  return products.value
    .filter(p => String(p.category) === selectedCategory.value && !mainIds.has(p.id))
    .slice(0, 8)
})
</script>

<template>
  <div class="min-h-screen bg-bg">
    <!-- Hero Section -->
    <section class="hero">
      <div class="wrap">
        <h1>Shop the market before you leave home.</h1>
        <p>Search what the vendors of Mandaue Public Market have today, compare prices across stalls, and reserve for pickup or delivery.</p>

        <form class="searchbar" @submit.prevent="page = 1; fetchProducts()">
          <input
            v-model="search"
            @keyup.enter="page = 1; fetchProducts()"
            type="search"
            placeholder="Search fish, vegetables, rice…"
            class="input"
            aria-label="Search products"
          >
          <button type="submit" class="btn btn-accent btn-lg">Search</button>
        </form>

        <div class="row-wrap mt12" style="font-size: .8rem; opacity: .9;">
          <span class="muted">Popular:</span>
          <router-link to="/catalog" :query="{ q: 'bangus' }" class="underline" style="color: #fff;">bangus</router-link>
          <router-link to="/catalog" :query="{ q: 'tomatoes' }" class="underline" style="color: #fff;">tomatoes</router-link>
          <router-link to="/catalog" :query="{ q: 'well-milled rice' }" class="underline" style="color: #fff;">well-milled rice</router-link>
          <router-link to="/catalog" :query="{ q: 'pork liempo' }" class="underline" style="color: #fff;">pork liempo</router-link>
        </div>
      </div>
    </section>

    <main class="page">
      <div class="wrap stack">

        <!-- Categories -->
        <section>
          <div class="row-between mb12">
            <h2 class="mb0">Browse by category</h2>
            <span class="muted small">{{ categories.length }} categories · {{ new Set(featuredVendors.map(v => v.id)).size }} vendors</span>
          </div>
          <div class="chips">
            <a
              class="chip"
              :class="{ on: !selectedCategory }"
              @click.prevent="selectedCategory = ''; page = 1; fetchProducts()"
              href="#"
            >
              All
            </a>
            <a
              v-for="cat in categories"
              :key="cat.id"
              class="chip"
              :class="{ on: selectedCategory === String(cat.id) }"
              @click.prevent="selectedCategory = String(cat.id); page = 1; fetchProducts()"
              href="#"
            >
              <span>{{ getCategoryIcon(cat.name) }}</span>
              <span>{{ cat.name }}</span>
            </a>
          </div>
        </section>

        <!-- Featured Products -->
        <section v-if="featuredProducts.length > 0">
          <div class="row-between mb12">
            <h2 class="mb0">Fresh today</h2>
            <router-link to="/catalog" class="small" style="color: var(--color-brand);">See all {{ totalCount }} products →</router-link>
          </div>
          <div class="grid grid-4">
            <article
              v-for="product in featuredProducts.slice(0, 8)"
              :key="product.id"
              class="pcard"
              @click="goToProduct(product)"
            >
              <div class="thumb">{{ getCategoryIcon(product.category_name || product.category) }}</div>
              <div class="body">
                <h3 class="name">{{ product.name }}</h3>
                <p class="vendor">{{ product.vendor_name }} · {{ product.stall_location }}</p>
                <div class="row-wrap">
                  <span class="badge" :class="product.availability === 'IN_STOCK' ? 'badge-ok' : 'badge-danger'">
                    <i class="dot" v-if="product.availability === 'IN_STOCK'"></i>
                    {{ product.availability === 'IN_STOCK' ? 'In stock' : 'Out of stock' }}
                  </span>
                  <span class="unit" v-if="product.stock_quantity">{{ product.stock_quantity }} {{ product.unit || 'kg' }} left</span>
                </div>
                <div class="foot">
                  <span class="price">{{ formatPrice(product.price) }} <span class="unit">/ {{ product.unit || 'kg' }}</span></span>
                  <button
                    @click.stop="toggleFavorite(product)"
                    :disabled="favoriting.has(product.id)"
                    :class="['btn btn-sm', isFavorited(product) ? 'btn-danger' : 'btn-ghost']"
                    title="Add to favorites"
                  >
                    {{ isFavorited(product) ? '♥' : '♡' }}
                  </button>
                  <button
                    @click.stop="addToCart(product)"
                    :disabled="product.availability !== 'IN_STOCK'"
                    class="btn btn-sm btn-primary"
                  >
                    Add
                  </button>
                </div>
              </div>
            </article>
          </div>
        </section>

        <!-- Featured Vendors -->
        <section v-if="featuredVendors.length > 0">
          <h2>Vendors at the market</h2>
          <div class="grid grid-3">
            <a
              v-for="vendor in featuredVendors.slice(0, 6)"
              :key="vendor.id"
              class="card card-tight"
              style="color: inherit; text-decoration: none;"
              @click.prevent="goToSearchResults(vendor.id)"
            >
              <div class="row-between">
                <strong>{{ vendor.name }}</strong>
                <span class="badge badge-brand">{{ vendor.category_name || vendor.category }}</span>
              </div>
              <div class="small muted">📍 {{ vendor.stall_location }} · {{ vendor.section_name || vendor.section }}</div>
              <div class="small muted mt8">{{ vendor.product_count || 0 }} products · {{ vendor.description || 'Fresh daily' }}</div>
            </a>
          </div>
        </section>

        <!-- Market Map Teaser -->
        <section class="card" style="background: linear-gradient(135deg, var(--color-brand-light) 0%, var(--color-bg) 100%);">
          <div class="grid grid-2" style="align-items: center; gap: 24px;">
            <div>
              <span class="badge badge-brand mb8">Interactive Market Map</span>
              <h2>Find the stall before you go.</h2>
              <p class="muted">See every section, stall number and vendor pin — then filter by category to plan your route through the market.</p>
              <router-link to="/market-map" class="btn btn-primary">Open the market map</router-link>
            </div>
            <div class="map" style="min-height: 190px; padding: 10px;">
              <div class="section" style="margin-bottom: 8px;">
                <h4>Section A – Fish</h4>
                <div class="stalls">
                  <div class="stall pin"><span class="no">A-12</span><span class="nm">Pedro's Fresh Catch</span><span class="cat">🐟 Fish</span></div>
                  <div class="stall"><span class="no">A-14</span><span class="nm">Ong's Seafood</span><span class="cat">🐟 Fish</span></div>
                </div>
              </div>
              <div class="section" style="margin-bottom: 8px;">
                <h4>Section B – Vegetables</h4>
                <div class="stalls">
                  <div class="stall pin"><span class="no">B-07</span><span class="nm">Rosa's Gulay Stand</span><span class="cat">🥬 Vegetables</span></div>
                  <div class="stall"><span class="no">B-09</span><span class="nm">Aling Nena's Gulay</span><span class="cat">🥬 Vegetables</span></div>
                </div>
              </div>
              <div class="section" style="margin-bottom: 8px;">
                <h4>Section C – Meat & Poultry</h4>
                <div class="stalls">
                  <div class="stall pin"><span class="no">C-03</span><span class="nm">Bautista Meat Shop</span><span class="cat">🥩 Meat</span></div>
                  <div class="stall pin"><span class="no">C-09</span><span class="nm">Nena's Manok</span><span class="cat">🍗 Poultry</span></div>
                </div>
              </div>
              <div class="section" style="margin-bottom: 8px;">
                <h4>Section D – Fruits</h4>
                <div class="stalls">
                  <div class="stall pin"><span class="no">D-02</span><span class="nm">Villamor Fruits & Gulay</span><span class="cat">🍎 Fruits</span></div>
                  <div class="stall"><span class="no">D-05</span><span class="nm">Cebu Fruit Corner</span><span class="cat">🍎 Fruits</span></div>
                </div>
              </div>
              <div class="section" style="margin-bottom: 0;">
                <h4>Section E – Dry Goods</h4>
                <div class="stalls">
                  <div class="stall pin"><span class="no">E-01</span><span class="nm">Tan's Rice & Dry Goods</span><span class="cat">🍚 Rice</span></div>
                  <div class="stall"><span class="no">E-03</span><span class="nm">Mandaue Grocery Stall</span><span class="cat">🫙 Dry goods</span></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Search Results with Filters Sidebar -->
        <section v-if="search || selectedCategory || hasActiveFilters">
          <div class="grid grid-side" style="gap: 24px;">

            <!-- Filters Sidebar -->
            <aside
              v-show="showFilters || windowWidth > 860"
              class="card"
              style="position: sticky; top: 80px; height: fit-content;"
            >
              <!-- Mobile filter toggle -->
              <button
                v-if="showFilters === false && windowWidth <= 860"
                @click="showFilters = true"
                class="btn btn-primary btn-block mb12"
                style="display: none;"
              >
                Filters
              </button>

              <div class="stack" style="gap: 16px;">

                <!-- Category Filters -->
                <div>
                  <h4 class="mb8">Category</h4>
                  <div class="stack" style="gap: 6px;">
                    <label v-for="cat in categories" :key="cat.id" class="check">
                      <input
                        type="checkbox"
                        :value="String(cat.id)"
                        v-model="selectedCategories"
                        @change="page = 1"
                      >
                      <span>{{ getCategoryIcon(cat.name) }} {{ cat.name }}</span>
                    </label>
                  </div>
                </div>

                <div class="divider"></div>

                <!-- Price Range -->
                <div>
                  <h4 class="mb8">Price (₱/kg)</h4>
                  <div class="row-wrap" style="gap: 8px;">
                    <div class="field" style="flex: 1;">
                      <label class="small muted">Min</label>
                      <input
                        type="number"
                        v-model.number="priceMin"
                        @change="page = 1"
                        class="input"
                        placeholder="0"
                        min="0"
                        step="0.01"
                      >
                    </div>
                    <div class="field" style="flex: 1;">
                      <label class="small muted">Max</label>
                      <input
                        type="number"
                        v-model.number="priceMax"
                        @change="page = 1"
                        class="input"
                        placeholder="500"
                        min="0"
                        step="0.01"
                      >
                    </div>
                  </div>
                </div>

                <div class="divider"></div>

                <!-- Availability Filters -->
                <div>
                  <h4 class="mb8">Availability</h4>
                  <div class="stack" style="gap: 6px;">
                    <label v-for="opt in availabilityOptions" :key="opt.value" class="check">
                      <input
                        type="checkbox"
                        :value="opt.value"
                        v-model="selectedAvailabilities"
                        @change="page = 1"
                      >
                      <span>{{ opt.label }}</span>
                    </label>
                  </div>
                </div>

                <div class="divider"></div>

                <!-- Vendor Filters -->
                <div>
                  <h4 class="mb8">Vendors</h4>
                  <div class="stack" style="gap: 6px; max-height: 200px; overflow-y: auto;">
                    <label v-for="vendor in vendors" :key="vendor.id" class="check">
                      <input
                        type="checkbox"
                        :value="String(vendor.id)"
                        v-model="selectedVendors"
                        @change="page = 1"
                      >
                      <span>{{ vendor.name }}</span>
                    </label>
                    <div v-if="vendors.length === 0" class="small muted">Loading vendors…</div>
                  </div>
                </div>

                <!-- Apply/Clear Buttons -->
                <div class="stack" style="gap: 8px; margin-top: 8px;">
                  <button
                    @click="page = 1; fetchProducts()"
                    class="btn btn-primary btn-block"
                    :disabled="loading"
                  >
                    Apply filters
                  </button>
                  <button
                    v-if="hasActiveFilters"
                    @click="clearFilters"
                    class="btn btn-ghost btn-block"
                  >
                    Clear all filters
                  </button>
                </div>

              </div>
            </aside>

            <!-- Results Panel -->
            <div class="stack" style="gap: 16px;">
              <!-- Results Toolbar -->
              <div class="row-between" style="flex-wrap: wrap; gap: 12px; align-items: center;">
                <div class="row-wrap" style="gap: 8px; align-items: center;">
                  <span class="muted small"><strong>{{ totalCount }}</strong> result{{ totalCount !== 1 ? 's' : '' }}</span>
                  <span v-if="hasActiveFilters" class="badge badge-brand small">Filtered</span>
                </div>
                <label class="row small" style="gap: 8px;">
                  <span class="muted">Sort</span>
                  <select
                    v-model="sortBy"
                    @change="page = 1; fetchProducts()"
                    class="input"
                    style="width: auto"
                    aria-label="Sort results"
                  >
                    <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </label>
              </div>

              <!-- Product Grid -->
              <div v-if="loading" class="text-center py-12">Loading…</div>

              <div v-else-if="products.length > 0" class="grid grid-3">
                <article
                  v-for="product in products"
                  :key="product.id"
                  :class="['pcard', { 'is-best': isBestValue(product) }]"
                  @click="goToProduct(product)"
                >
                  <!-- Best Value Badge -->
                  <div v-if="isBestValue(product)" class="absolute top-2 left-2 z-10">
                    <span class="badge badge-accent tiny">Best value</span>
                  </div>

                  <div class="thumb">{{ getCategoryIcon(product.category_name || product.category) }}</div>
                  <div class="body">
                    <h3 class="name">{{ product.name }}</h3>
                    <p class="vendor">{{ product.vendor_name }} · {{ product.stall_location }}</p>
                    <div class="row-wrap">
                      <span class="badge" :class="product.availability === 'IN_STOCK' ? 'badge-ok' : (product.availability === 'LOW_STOCK' ? 'badge-warn' : 'badge-danger')">
                        <i class="dot" v-if="product.availability === 'IN_STOCK'"></i>
                        {{ product.availability === 'IN_STOCK' ? 'In stock' : (product.availability === 'LOW_STOCK' ? 'Low stock' : 'Out of stock') }}
                      </span>
                      <span class="unit" v-if="product.stock_quantity">{{ product.stock_quantity }} {{ product.unit || 'kg' }} available</span>
                    </div>
                    <div class="foot">
                      <div class="price-wrap">
                        <span class="price">{{ formatPrice(product.price) }} <span class="unit">/ {{ product.unit || 'kg' }}</span></span>
                        <!-- Price Delta Badge -->
                        <span v-if="getPriceDelta(product)" class="badge badge-danger tiny ml8" style="font-weight: 500; margin-top: 2px; display: inline-block;">
                          {{ getPriceDelta(product) }}
                        </span>
                      </div>
                      <button
                        @click.stop="toggleFavorite(product)"
                        :disabled="favoriting.has(product.id)"
                        :class="['btn btn-sm', isFavorited(product) ? 'btn-danger' : 'btn-ghost']"
                        title="Add to favorites"
                      >
                        {{ isFavorited(product) ? '♥' : '♡' }}
                      </button>
                      <button
                        @click.stop="addToCart(product)"
                        :disabled="product.availability !== 'IN_STOCK'"
                        class="btn btn-sm btn-primary"
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </article>
              </div>

              <div v-else class="text-center py-12">
                <p class="muted">No products found matching your criteria.</p>
              </div>

              <!-- Pagination -->
              <div v-if="totalCount > pageSize" class="flex justify-center gap-2 mt-6">
                <button
                  @click="page > 1 && (page--, fetchProducts())"
                  :disabled="page === 1"
                  class="btn btn-sm"
                  :class="{ 'opacity-50': page === 1 }"
                >
                  Previous
                </button>
                <span class="flex items-center px-4 small muted">Page {{ page }}</span>
                <button
                  @click="page * pageSize < totalCount && (page++, fetchProducts())"
                  :disabled="page * pageSize >= totalCount"
                  class="btn btn-sm"
                  :class="{ 'opacity-50': page * pageSize >= totalCount }"
                >
                  Next
                </button>
              </div>

              <!-- Second Result Group: "Also in [Category]" -->
              <section v-if="alsoInCategory.length > 0" class="card">
                <div class="card-head">
                  <h3>Also in {{ categories.find(c => String(c.id) === selectedCategory)?.name || 'this category' }}</h3>
                </div>
                <div class="grid grid-4">
                  <article
                    v-for="product in alsoInCategory"
                    :key="product.id"
                    class="pcard"
                    @click="goToProduct(product)"
                  >
                    <div class="thumb">{{ getCategoryIcon(product.category_name || product.category) }}</div>
                    <div class="body">
                      <h3 class="name">{{ product.name }}</h3>
                      <p class="vendor">{{ product.vendor_name }} · {{ product.stall_location }}</p>
                      <div class="row-wrap">
                        <span class="badge" :class="product.availability === 'IN_STOCK' ? 'badge-ok' : 'badge-danger'">
                          <i class="dot" v-if="product.availability === 'IN_STOCK'"></i>
                          {{ product.availability === 'IN_STOCK' ? 'In stock' : 'Out of stock' }}
                        </span>
                        <span class="unit" v-if="product.stock_quantity">{{ product.stock_quantity }} {{ product.unit || 'kg' }} left</span>
                      </div>
                      <div class="foot">
                        <span class="price">{{ formatPrice(product.price) }} <span class="unit">/ {{ product.unit || 'kg' }}</span></span>
                        <button
                          @click.stop="toggleFavorite(product)"
                          :disabled="favoriting.has(product.id)"
                          :class="['btn btn-sm', isFavorited(product) ? 'btn-danger' : 'btn-ghost']"
                          title="Add to favorites"
                        >
                          {{ isFavorited(product) ? '♥' : '♡' }}
                        </button>
                        <button
                          @click.stop="addToCart(product)"
                          :disabled="product.availability !== 'IN_STOCK'"
                          class="btn btn-sm btn-primary"
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
        </section>

      </div>
    </main>

    <footer class="foot">
      <div class="wrap row-between">
        <span>E-Compra · CCS630 Advance Database Systems capstone</span>
        <span>All prices in Philippine pesos (₱)</span>
      </div>
    </footer  >
  </div>
</template>

<style scoped>
/* Hero gradient background override */
.hero {
  background: linear-gradient(135deg, var(--color-brand) 0%, var(--color-brand-dark) 100%);
  color: #fff;
  padding: 40px 0 44px;
  margin-bottom: 26px;
}

.hero h1 {
  font-size: 2.1rem;
  letter-spacing: -.03em;
  margin: 0 0 8px;
}

.hero p {
  margin: 0 0 16px;
  opacity: .92;
  max-width: 68ch;
}

.hero .row-wrap {
  margin-top: 16px;
}

.hero .searchbar {
  gap: 8px;
}

.hero .input {
  flex: 1;
  background: #fff;
  color: var(--color-ink);
  border: 1px solid var(--color-line);
}

.hero .input::placeholder {
  color: var(--color-muted);
}

.hero .input:focus {
  outline: 2px solid var(--color-brand-line);
  outline-offset: 0;
  border-color: var(--color-brand);
}

.hero .btn-accent {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.hero .btn-accent:hover {
  background: var(--color-accent-dark);
}

.hero a {
  color: #fff;
  text-decoration: underline;
}

.hero a:hover {
  opacity: .8;
}

/* Chip active state uses design system .chip.on */
.chip.on {
  background: var(--color-brand);
  border-color: var(--color-brand);
  color: #fff;
}

/* Product card thumb emoji sizing */
.pcard .thumb {
  font-size: 2.5rem;
}

/* Vendor card hover */
.card-tight:hover {
  background: var(--color-brand-light);
  border-color: var(--color-brand-line);
}

/* Map section styling */
.map .section {
  border: 2px dashed var(--color-brand-line);
  border-radius: var(--radius-sm);
  padding: 10px;
  background: rgba(255,255,255,.72);
}

.map .section > h4 {
  font-size: .75rem;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--color-brand-dark);
  margin-bottom: 8px;
}

.map .stalls {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.map .stall {
  border: 1px solid var(--color-line);
  background: #fff;
  border-radius: var(--radius-sm);
  padding: 6px 9px;
  font-size: .76rem;
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 104px;
}

.map .stall .no {
  font-weight: 700;
  font-size: .72rem;
  color: var(--color-brand-dark);
}

.map .stall .nm {
  font-weight: 600;
}

.map .stall .cat {
  color: var(--color-muted);
  font-size: .7rem;
}

.map .stall.pin {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-light);
}

/* Pagination buttons */
.btn-sm.opacity-50 {
  opacity: .5;
  cursor: not-allowed;
}

/* Filters Sidebar */
@media (max-width: 860px) {
  .grid-side {
    grid-template-columns: 1fr !important;
  }

  aside.card {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    z-index: 40;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow-y: auto !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-lg) !important;
    padding: 16px !important;
  }

  aside.card .btn-block {
    display: block !important;
  }

  .filter-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,.4);
    z-index: 35;
  }
}

/* Best Value Badge Positioning */
.pcard.is-best {
  position: relative;
  border-color: var(--color-accent) !important;
  box-shadow: 0 0 0 2px var(--color-accent-light) !important;
}

.pcard.is-best .badge-accent {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Checkbox styling */
.check {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: .9rem;
  padding: 4px 0;
}

.check input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-brand);
  flex-shrink: 0;
}

/* Filter section spacing */
aside.card .stack > div:last-child {
  margin-top: 8px;
}

/* Price inputs in sidebar */
aside .field {
  min-width: 0;
}

aside .field label {
  display: block;
  margin-bottom: 4px;
}

aside .field .input {
  width: 100%;
}

/* Results toolbar */
.row-between .muted.small {
  white-space: nowrap;
}

/* Grid responsive */
@media (max-width: 1024px) {
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .grid-3 { grid-template-columns: 1fr; }
  .grid-4 { grid-template-columns: 1fr; }
}

/* Card head for "Also in" section */
.card-head {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-line);
}

.card-head h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}
</style>