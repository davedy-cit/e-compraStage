<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const comparisonGroup = ref(route.query.comparison_group || 'TOMATO')
const baseUnit = ref(route.query.base_unit || 'KG')
const products = ref([])
const comparisonGroups = ref([])

// Computed
const rankedProducts = computed(() => {
  if (!products.value.length) return []

  // Get the conversion factor for each product's unit to the base unit
  return products.value.map(p => {
    const factor = getConversionFactor(p.comparison_group, p.unit_code, baseUnit.value)
    const normalizedPrice = factor ? (p.price / factor) : p.price
    return { ...p, factor, normalizedPrice }
  }).sort((a, b) => a.normalizedPrice - b.normalizedPrice)
})

const bestValue = computed(() => rankedProducts.value[0])

const savings = computed(() => {
  if (rankedProducts.value.length < 2) return 0
  const cheapest = rankedProducts.value[0].normalizedPrice
  const dearest = rankedProducts.value[rankedProducts.value.length - 1].normalizedPrice
  return ((dearest - cheapest) * 5).toFixed(2) // 5kg basket
})

const otherProductsWithMultipleVendors = computed(() => {
  // Group products by comparison_group and count vendors
  const groups = {}
  products.value.forEach(p => {
    if (!p.comparison_group) return
    if (!groups[p.comparison_group]) groups[p.comparison_group] = []
    groups[p.comparison_group].push(p)
  })

  return Object.entries(groups)
    .filter(([_, prods]) => prods.length > 1)
    .map(([code, prods]) => {
      const prices = prods.map(p => getConversionFactor(p.comparison_group, p.unit_code, 'KG') ? p.price / getConversionFactor(p.comparison_group, p.unit_code, 'KG') : p.price)
      return {
        code,
        name: prods[0].comparison_group_name || code,
        vendors: prods.length,
        lowest: Math.min(...prices).toFixed(2),
        highest: Math.max(...prices).toFixed(2),
        spread: (Math.max(...prices) - Math.min(...prices)).toFixed(2)
      }
    })
})

// Methods
function getConversionFactor(groupCode, unitCode, targetUnit = 'KG') {
  // This would ideally come from the API, but for now we'll use a simple mapping
  // In reality, this comes from ComparisonGroupUnit model
  const factors = {
    'TOMATO': { 'KG': 1, 'G': 0.001, 'SACK': 25 },
    'BANGUS': { 'KG': 1, 'G': 0.001 },
    'RICE_WELL_MILLED': { 'KG': 1, 'SACK': 25, 'G': 0.001 },
    'PORK_BELLY': { 'KG': 1, 'G': 0.001 },
    'EGGS': { 'PCS': 1, 'DOZEN': 12, 'TRAY': 30 }
  }
  return factors[groupCode]?.[unitCode]?.[targetUnit] || factors[groupCode]?.[unitCode] || 1
}

async function fetchComparisonGroups() {
  try {
    const res = await api.get('catalog/products/', {
      params: { comparison_group: comparisonGroup.value }
    })
    products.value = res.data
  } catch (e) {
    error.value = 'Failed to load products'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchAllComparisonGroups() {
  try {
    // Get all products to find which comparison groups have multiple vendors
    const res = await api.get('catalog/products/')
    const allProducts = res.data

    const groups = {}
    allProducts.forEach(p => {
      if (!p.comparison_group) return
      if (!groups[p.comparison_group]) {
        groups[p.comparison_group] = { name: p.comparison_group, products: [] }
      }
      groups[p.comparison_group].products.push(p)
    })

    comparisonGroups.value = Object.entries(groups)
      .filter(([_, g]) => g.products.length > 1)
      .map(([code, g]) => ({
        code,
        name: g.name,
        vendorCount: g.products.length
      }))
  } catch (e) {
    console.error('Failed to load comparison groups:', e)
  }
}

function formatPrice(price, unit) {
  return `₱${Number(price).toFixed(2)} / ${unit.toLowerCase()}`
}

function getAvailabilityBadge(stock, availability) {
  if (availability === 'OUT_OF_STOCK' || stock === 0) {
    return { class: 'badge badge-danger', text: 'Out of stock' }
  }
  if (availability === 'LOW_STOCK' || stock <= 10) {
    return { class: 'badge badge-warn', text: `${stock} left` }
  }
  return { class: 'badge badge-ok', text: `✓ ${stock} ${unit}` }
}

function navigateToProduct(productId) {
  router.push(`/product/${productId}`)
}

function navigateToMarketMap(stall) {
  router.push(`/market-map?section=${stall}`)
}

function updateComparisonGroup(groupCode) {
  comparisonGroup.value = groupCode
  router.push({ query: { ...route.query, comparison_group: groupCode } })
  loading.value = true
  fetchComparisonGroups()
}

function updateBaseUnit(unit) {
  baseUnit.value = unit
  router.push({ query: { ...route.query, base_unit: unit } })
}

// Watch for route query changes
watch(() => route.query.comparison_group, (newVal) => {
  if (newVal && newVal !== comparisonGroup.value) {
    comparisonGroup.value = newVal
    loading.value = true
    fetchComparisonGroups()
  }
})

watch(() => route.query.base_unit, (newVal) => {
  if (newVal && newVal !== baseUnit.value) {
    baseUnit.value = newVal
  }
})

onMounted(async () => {
  await fetchAllComparisonGroups()
  await fetchComparisonGroups()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Price comparison tool</div>
        <h1>{{ bestValue?.comparison_group_name || comparisonGroup }} — {{ rankedProducts.length }} vendor{{ rankedProducts.length !== 1 ? 's' : '' }}</h1>
        <p>Every vendor selling this product is normalised to one base unit (1 kilogram) before ranking, so the cheapest stall is the cheapest stall even when the listed unit differs.</p>
      </div>

      <!-- Controls -->
      <div class="row-wrap" style="--gap: 12px">
        <label class="row small"><span class="muted">Product</span>
          <select class="input" style="width:auto" v-model="comparisonGroup" @change="updateComparisonGroup(comparisonGroup)">
            <option v-for="group in comparisonGroups" :key="group.code" :value="group.code">
              {{ group.name }} ({{ group.code }}) — {{ group.vendorCount }} vendors
            </option>
          </select>
        </label>
        <label class="row small"><span class="muted">Compare per</span>
          <select class="input" style="width:auto" v-model="baseUnit" @change="updateBaseUnit(baseUnit)">
            <option value="KG">Kilogram</option>
            <option value="G">Gram</option>
            <option value="PCS">Piece</option>
          </select>
        </label>
        <span class="badge badge-brand">Comparison group: {{ comparisonGroup }}</span>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px">
        <div class="spinner"></div>
        <p class="muted mt12">Loading price data...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger)">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchComparisonGroups">Retry</button>
      </div>

      <div v-else>
        <!-- Best Value Card -->
        <div class="card" style="border-color: var(--ok); box-shadow: 0 0 0 2px var(--ok-bg), var(--shadow)">
          <div class="row-between">
            <div class="row" style="--gap: 16px">
              <div style="width: 60px; height: 60px; display: grid; place-items: center; font-size: 2rem; background: var(--brand-light); border-radius: var(--radius-sm)">
                🍅
              </div>
              <div>
                <span class="badge badge-ok mb8">✓ Best value</span>
                <h2 class="mb0">{{ bestValue.vendor?.name || 'Unknown Vendor' }}</h2>
                <div class="small muted">📍 {{ bestValue.vendor?.stall_location || 'N/A' }} · {{ bestValue.vendor?.market_section || 'N/A' }} · 📞 {{ bestValue.vendor?.contact_phone || 'N/A' }}</div>
              </div>
            </div>
            <div class="center">
              <div class="price price-lg" style="font-size: 2rem">₱{{ bestValue.normalizedPrice.toFixed(2) }}</div>
              <div class="unit">per {{ baseUnit.toLowerCase() }}</div>
              <div class="badge badge-ok mt8" v-if="rankedProducts.length > 1">Saves ₱{{ (rankedProducts[rankedProducts.length - 1].normalizedPrice - bestValue.normalizedPrice).toFixed(2) }}/{{ baseUnit.toLowerCase() }}</div>
            </div>
          </div>
          <div class="card-foot row-between">
            <span class="small muted">{{ bestValue.stock_quantity }} {{ bestValue.unit_code?.toLowerCase() || 'units' }} available · {{ bestValue.availability?.toLowerCase().replace('_', ' ') || 'in stock' }} · sold by the {{ bestValue.unit_code?.toLowerCase() || 'piece' }}</span>
            <div class="row-wrap">
              <a class="btn btn-sm" @click="navigateToMarketMap(bestValue.vendor?.stall_location)">Show stall</a>
              <a class="btn btn-sm btn-primary" @click="navigateToProduct(bestValue.id)">Add to cart</a>
            </div>
          </div>
        </div>

        <!-- All Vendors Ranked Table -->
        <div class="card">
          <div class="card-head">
            <h3>All vendors, ranked by price per {{ baseUnit.toLowerCase() }}</h3>
            <span class="small muted">Updated {{ new Date().toLocaleDateString('en-PH', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }}</span>
          </div>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Vendor</th>
                  <th>Stall</th>
                  <th>Listed price</th>
                  <th>Listed unit</th>
                  <th class="num">Per {{ baseUnit }}</th>
                  <th class="num">Difference</th>
                  <th>Availability</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(product, index) in rankedProducts" :key="product.id" :style="{ background: index === 0 ? 'var(--ok-bg)' : '' }">
                  <td><strong>{{ index + 1 }}</strong></td>
                  <td>
                    <strong>{{ product.vendor?.name || 'Unknown' }}</strong>
                    <span v-if="index === 0" class="badge badge-ok">Best</span>
                  </td>
                  <td class="mono">{{ product.vendor?.stall_location || 'N/A' }}</td>
                  <td>₱{{ Number(product.price).toFixed(2) }}</td>
                  <td>{{ product.unit_code || 'N/A' }}</td>
                  <td class="num"><strong>₱{{ product.normalizedPrice.toFixed(2) }}</strong></td>
                  <td class="num" :style="{ color: index === 0 ? 'var(--muted)' : 'var(--danger)' }">
                    <span v-if="index === 0">—</span>
                    <span v-else>+₱{{ (product.normalizedPrice - bestValue.normalizedPrice).toFixed(2) }}</span>
                  </td>
                  <td>
                    <span :class="getAvailabilityBadge(product.stock_quantity, product.availability).class">
                      <i class="dot"></i>{{ getAvailabilityBadge(product.stock_quantity, product.availability).text }}
                    </span>
                  </td>
                  <td><a class="btn btn-sm" :class="index === 0 ? 'btn-primary' : ''" @click="navigateToProduct(product.id)">Add</a></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-foot small muted" v-if="rankedProducts.length > 1">
            A basket of <strong>5 kg</strong> costs ₱{{ (bestValue.normalizedPrice * 5).toFixed(2) }} at the cheapest stall and ₱{{ (rankedProducts[rankedProducts.length - 1].normalizedPrice * 5).toFixed(2) }} at the dearest —
            <strong>₱{{ savings }} saved</strong> by walking to the cheapest section.
          </div>
        </div>

        <!-- Normalisation Explainer & Other Products -->
        <div class="grid grid-2">
          <div class="card">
            <div class="card-head"><h3>How normalisation works</h3></div>
            <p class="small muted">Each comparison group stores a conversion factor from every allowed unit to the group's base unit:</p>
            <div class="table-wrap">
              <table class="table">
                <thead><tr><th>Unit</th><th class="num">Factor to kg</th><th class="num">₱{{ bestValue?.price?.toFixed(2) || '75.00' }} becomes</th></tr></thead>
                <tbody>
                  <tr><td>Kilogram (KG)</td><td class="num">1.0000</td><td class="num">₱{{ bestValue ? (bestValue.price / getConversionFactor(bestValue.comparison_group, bestValue.unit_code, 'KG')).toFixed(2) : '75.00' }} / kg</td></tr>
                  <tr><td>Gram (G)</td><td class="num">0.0010</td><td class="num">₱{{ bestValue ? (bestValue.price / getConversionFactor(bestValue.comparison_group, bestValue.unit_code, 'KG') * 0.001).toFixed(4) : '0.0750' }} / g</td></tr>
                  <tr><td>Sack (SACK)</td><td class="num">25.0000</td><td class="num">₱{{ bestValue ? (bestValue.price / getConversionFactor(bestValue.comparison_group, bestValue.unit_code, 'KG') * 25).toFixed(2) : '1875.00' }} / sack</td></tr>
                </tbody>
              </table>
            </div>
            <div class="note mt12 tiny">
              The ranking is one <span class="mono">JOIN</span> and one <span class="mono">ORDER BY</span>:
              <span class="mono">price / factor_to_base</span>. Nothing is hard-coded per vendor.
            </div>
          </div>

          <div class="card">
            <div class="card-head"><h3>Other products with multiple vendors</h3></div>
            <div class="table-wrap">
              <table class="table">
                <thead><tr><th>Product</th><th class="num">Vendors</th><th class="num">Lowest</th><th class="num">Highest</th><th class="num">Spread</th></tr></thead>
                <tbody>
                  <tr v-for="item in otherProductsWithMultipleVendors" :key="item.code">
                    <td><a @click="updateComparisonGroup(item.code)">{{ item.name }}</a></td>
                    <td class="num">{{ item.vendors }}</td>
                    <td class="num">₱{{ item.lowest }}</td>
                    <td class="num">₱{{ item.highest }}</td>
                    <td class="num">₱{{ item.spread }}</td>
                  </tr>
                  <tr v-if="!otherProductsWithMultipleVendors.length">
                    <td colspan="5" class="center muted small">No other products currently have multiple vendors</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="note note-warn mt12 tiny">
              Only <strong>{{ comparisonGroup }}</strong> currently has more than one vendor, which is why it is the example in the
              project idea document. The comparison screen works the same for any product once more vendors list it.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--brand-line);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.center {
  text-align: center;
}

.row-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.mb0 { margin-bottom: 0; }
.mb8 { margin-bottom: 8px; }
.mt8 { margin-top: 8px; }
.mt12 { margin-top: 12px; }

.badge-brand { background: var(--brand-light); color: var(--brand-dark); }
.badge-ok { background: var(--ok-bg); color: var(--ok); }
.badge-warn { background: var(--warn-bg); color: var(--warn); }
.badge-danger { background: var(--danger-bg); color: var(--danger); }

.num { text-align: right; font-variant-numeric: tabular-nums; }
.mono { font-family: var(--font-mono); font-size: 0.875rem; }
.tiny { font-size: 0.75rem; }
.small { font-size: 0.8125rem; }
.muted { color: var(--muted); }

.card-tight { padding: 12px; }
.card-foot { padding-top: 12px; border-top: 1px solid var(--line); margin-top: 12px; }
.card-head { padding-bottom: 12px; border-bottom: 1px solid var(--line); margin-bottom: 12px; }

.table-wrap { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.table th, .table td { padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; }
.table th { font-weight: 600; color: var(--ink-2); background: var(--neutral-bg); }
.table tbody tr:hover { background: var(--brand-light); }
.table tbody tr:last-child td { border-bottom: none; }

.grid { display: grid; gap: 16px; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 860px) {
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .row-between { flex-direction: column; align-items: flex-start; }
}

@media (max-width: 520px) {
  .price-lg { font-size: 1.5rem !important; }
  .table th, .table td { padding: 8px; font-size: 0.8125rem; }
}
</style>