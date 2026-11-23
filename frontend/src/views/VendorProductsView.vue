<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const productsData = ref(null)
const activeFilter = ref('All')
const selectedProduct = ref(null)
const showEditModal = ref(false)
const showRestockModal = ref(false)
const restockProduct = ref(null)

// Mock data - in production this would come from API endpoints
const mockProductsData = {
  vendorName: "Pedro's Fresh Catch",
  stall: 'Stall A-12',
  products: [
    { id: 1, name: 'Bangus (Milkfish)', emoji: '🐟', category: 'Fish · fresh', comparisonGroup: 'BANGUS', price: '180.00', unit: 'kg', onHand: 12, threshold: 5, availability: 'IN_STOCK', soldMonth: '42 kg', isLowStock: false },
    { id: 2, name: 'Galunggong (Round Scad)', emoji: '🐟', category: 'Fish · fresh', comparisonGroup: 'GALUNGGONG', price: '160.00', unit: 'kg', onHand: 17, threshold: 5, availability: 'IN_STOCK', soldMonth: '28 kg', isLowStock: false },
    { id: 3, name: 'Tilapia', emoji: '🐟', category: 'Fish · fresh', comparisonGroup: 'TILAPIA', price: '140.00', unit: 'kg', onHand: 25, threshold: 5, availability: 'IN_STOCK', soldMonth: '22 kg', isLowStock: false },
    { id: 4, name: 'Tulingan (Bullet Tuna)', emoji: '🐟', category: 'Fish · fresh', comparisonGroup: 'TULINGAN', price: '190.00', unit: 'kg', onHand: 14, threshold: 4, availability: 'IN_STOCK', soldMonth: '15 kg', isLowStock: false },
    { id: 5, name: 'Hipon (Shrimp)', emoji: '🦐', category: 'Seafood · fresh', comparisonGroup: 'HIPON', price: '380.00', unit: 'kg', onHand: 6, threshold: 5, availability: 'LOW_STOCK', soldMonth: '6 kg', isLowStock: true },
    { id: 6, name: 'Dried Fish (Tuyo)', emoji: '🐟', category: 'Fish · dried', comparisonGroup: 'TUYO', price: '420.00', unit: 'kg', onHand: 5, threshold: 3, availability: 'LOW_STOCK', soldMonth: '2 kg', isLowStock: true }
  ],
  ledger: [
    { when: '09 Nov, 6:00 AM', reason: 'RECEIVED', order: '— opening balance', delta: +15, running: 15, reasonColor: 'ok' },
    { when: '10 Nov, 9:14 AM', reason: 'SOLD_ONLINE', order: 'ECO-20261110-0001', delta: -2, running: 13, reasonColor: 'info' },
    { when: '11 Nov, 2:30 PM', reason: 'SOLD_WALKIN', order: 'ECO-20261111-0003', delta: -1, running: 12, reasonColor: '' }
  ],
  ledgerBalance: 12,
  ledgerProduct: 'Bangus',
  restockProducts: [
    { id: 5, name: '🦐 Hipon (Shrimp)', onHand: 6 }
  ],
  inventoryReasons: [
    'RECEIVED — delivery from supplier',
    'ADJUSTMENT — correction',
    'RETURNED — customer return',
    'SPOILAGE — damaged or spoiled'
  ]
}

const filters = [
  { key: 'All', label: 'All (6)' },
  { key: 'In stock', label: 'In stock (4)' },
  { key: 'Low stock', label: 'Low stock (2)' },
  { key: 'Unavailable', label: 'Unavailable (0)' }
]

const filteredProducts = computed(() => {
  if (activeFilter.value === 'All') return productsData.value.products
  if (activeFilter.value === 'In stock') return productsData.value.products.filter(p => p.availability === 'IN_STOCK')
  if (activeFilter.value === 'Low stock') return productsData.value.products.filter(p => p.availability === 'LOW_STOCK')
  if (activeFilter.value === 'Unavailable') return productsData.value.products.filter(p => p.availability === 'OUT_OF_STOCK' || p.availability === 'UNAVAILABLE')
  return productsData.value.products
})

const totalCount = computed(() => productsData.value?.products.length || 0)
const inStockCount = computed(() => productsData.value?.products.filter(p => p.availability === 'IN_STOCK').length || 0)
const lowStockCount = computed(() => productsData.value?.products.filter(p => p.availability === 'LOW_STOCK').length || 0)

async function fetchProducts() {
  try {
    // In production: await api.get('/vendor/products/')
    productsData.value = mockProductsData
  } catch (e) {
    error.value = 'Failed to load products'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function setFilter(filterKey) {
  activeFilter.value = filterKey
}

function getAvailabilityBadge(availability) {
  const classes = {
    'IN_STOCK': 'badge badge-ok',
    'LOW_STOCK': 'badge badge-warn',
    'OUT_OF_STOCK': 'badge badge-danger',
    'UNAVAILABLE': 'badge'
  }
  const texts = {
    'IN_STOCK': 'IN_STOCK',
    'LOW_STOCK': 'LOW_STOCK',
    'OUT_OF_STOCK': 'Out of stock',
    'UNAVAILABLE': 'Unavailable'
  }
  return { class: classes[availability] || 'badge', text: texts[availability] || availability }
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

function openEditModal(product) {
  selectedProduct.value = product
  showEditModal.value = true
}

function openRestockModal(product) {
  restockProduct.value = product
  showRestockModal.value = true
}

function closeModals() {
  showEditModal.value = false
  showRestockModal.value = false
  selectedProduct.value = null
  restockProduct.value = null
}

function postRestockMovement() {
  // In production: POST /vendor/inventory-movements/
  alert(`Record stock movement: +${restockProduct.value?.onHand || 0} kg for ${restockProduct.value?.name}`)
  closeModals()
}

onMounted(() => {
  fetchProducts()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Vendor console</div>
        <h1>My products</h1>
        <p>{{ productsData?.vendorName || "Pedro's Fresh Catch" }} · {{ productsData?.stall || 'Stall A-12' }}. Price and availability are yours to set; <strong>stock is not</strong> — it is the sum of the inventory ledger, so it changes only when you record a movement.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading products...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchProducts">Retry</button>
      </div>

      <div v-else>
        <!-- Filter Chips & Actions -->
        <div class="row-between">
          <div class="chips">
            <a v-for="filter in filters" :key="filter.key" class="chip" :class="{ on: activeFilter === filter.key }" @click.prevent="setFilter(filter.key)">{{ filter.label }}</a>
          </div>
          <div class="row-wrap">
            <button class="btn" type="button">📥 Record stock received</button>
            <button class="btn btn-primary" type="button">＋ Add product</button>
          </div>
        </div>

        <!-- Products Table -->
        <section class="card">
          <div class="card-head">
            <h3>Listings</h3>
            <span class="small muted">{{ productsData?.vendorName || "Pedro's Fresh Catch" }} · {{ productsData?.stall || 'Stall A-12' }}</span>
          </div>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Product</th><th>Comparison group</th>
                  <th class="num">Price</th><th class="num">On hand</th><th class="num">Threshold</th>
                  <th>Availability</th><th class="num">Sold (mo.)</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in filteredProducts" :key="product.id" :style="{ background: product.isLowStock ? 'var(--warn-bg)' : '' }">
                  <td>
                    <strong>{{ product.emoji }} {{ product.name }}</strong>
                    <div class="tiny muted">{{ product.category }}</div>
                  </td>
                  <td class="tiny mono">{{ product.comparisonGroup }}</td>
                  <td class="num"><strong>{{ formatCurrency(product.price) }}</strong> <span class="unit tiny">/ {{ product.unit }}</span></td>
                  <td class="num"><strong v-if="product.isLowStock">{{ product.onHand }} {{ product.unit }}</strong><span v-else>{{ product.onHand }} {{ product.unit }}</span></td>
                  <td class="num">{{ product.threshold }} {{ product.unit }}</td>
                  <td><span :class="getAvailabilityBadge(product.availability).class"><i class="dot"></i>{{ getAvailabilityBadge(product.availability).text }}</span></td>
                  <td class="num">{{ product.soldMonth }}</td>
                  <td>
                    <div class="row-wrap">
                      <button class="btn btn-sm" type="button" @click="openEditModal(product)">Edit</button>
                      <button class="btn btn-sm" :class="product.isLowStock ? 'btn-accent' : ''" type="button" @click="openRestockModal(product)">Restock</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredProducts.length">
                  <td colspan="8" class="center muted small">No products match the current filter</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-foot tiny muted">
            <strong>LOW_STOCK</strong> is derived, not typed: on hand (6 kg) is at or below the threshold you set (5 kg).
            Buyers still see the product — it just carries a warning badge.
          </div>
        </section>

        <!-- Ledger + Sidebar -->
        <div class="grid-side" style="grid-template-columns: 1fr 340px">
          <!-- Inventory Ledger -->
          <section class="card">
            <div class="card-head">
              <h3>Inventory ledger — {{ productsData?.ledgerProduct || 'Bangus' }}</h3>
              <span class="small muted">every movement, newest last</span>
            </div>
            <div class="table-wrap">
              <table class="table">
                <thead>
                  <tr><th>When</th><th>Reason</th><th>Order</th><th class="num">Δ</th><th class="num">Running</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(entry, index) in productsData?.ledger" :key="index">
                    <td class="small">{{ entry.when }}</td>
                    <td><span class="badge" :class="entry.reasonColor ? 'badge-' + entry.reasonColor : ''">{{ entry.reason }}</span></td>
                    <td class="tiny mono">{{ entry.order }}</td>
                    <td class="num" :style="{ color: entry.delta > 0 ? 'var(--ok)' : 'var(--danger)' }">
                      <span v-if="entry.delta > 0">+</span>{{ entry.delta }}
                    </td>
                    <td class="num"><strong v-if="index === productsData.ledger.length - 1">{{ entry.running }}</strong><span v-else>{{ entry.running }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="card-foot">
              <div class="row-between">
                <span class="small muted">Ledger balance</span>
                <span class="price">{{ productsData?.ledgerBalance || 12 }} kg</span>
              </div>
              <div class="row-between mt8">
                <span class="small muted">Cached on <span class="mono">Product.stock_quantity</span></span>
                <span class="badge badge-ok"><i class="dot"></i>{{ productsData?.ledgerBalance || 12 }} kg — matches</span>
              </div>
            </div>
            <div class="note mt12 tiny">
              <strong>Why both.</strong> The ledger is the source of truth and the audit trail. The cached column exists
              only so product listings do not have to <span class="mono">SUM()</span> the ledger on every page view — a
              database trigger keeps the two in step.
            </div>
          </section>

          <!-- Sidebar: Edit + Restock -->
          <aside class="stack">
            <!-- Edit Listing Modal -->
            <div class="card" v-if="showEditModal && selectedProduct">
              <div class="card-head"><h3>Edit listing — {{ selectedProduct.name }}</h3></div>
              <div class="field">
                <span>Product name</span>
                <input class="input" type="text" :value="selectedProduct.name" aria-label="Product name" readonly>
              </div>
              <div class="field">
                <span>Price per {{ selectedProduct.unit }} (₱)</span>
                <input class="input" type="text" :value="selectedProduct.price" aria-label="Price">
              </div>
              <div class="field">
                <span>Unit of measure</span>
                <select class="input" aria-label="Unit">
                  <option>kg — kilogram</option>
                  <option>pc — piece</option>
                  <option>bundle</option>
                </select>
              </div>
              <div class="field">
                <span>Comparison group</span>
                <select class="input" aria-label="Comparison group">
                  <option>{{ selectedProduct.comparisonGroup }} — {{ selectedProduct.name }}</option>
                </select>
              </div>
              <div class="field">
                <span>Low-stock threshold</span>
                <input class="input" type="text" :value="selectedProduct.threshold" aria-label="Threshold">
              </div>
              <div class="field mb0">
                <span>Availability</span>
                <select class="input" aria-label="Availability">
                  <option>Auto (from stock)</option>
                  <option>UNAVAILABLE — hide from buyers</option>
                </select>
              </div>
              <div class="card-foot row-wrap">
                <button class="btn btn-primary" type="button">Save changes</button>
                <button class="btn" type="button" @click="closeModals">Cancel</button>
              </div>
              <div class="note note-warn mt12 tiny mb0">
                There is no stock field on this form — that is deliberate. Stock moves through the ledger only.
              </div>
            </div>

            <!-- Record Stock Received -->
            <div class="card" v-if="showRestockModal && restockProduct">
              <div class="card-head"><h3>Record stock received</h3></div>
              <div class="field">
                <span>Product</span>
                <select class="input" aria-label="Product">
                  <option v-for="p in productsData?.restockProducts" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>
              <div class="field">
                <span>Quantity received</span>
                <input class="input" type="text" value="10" aria-label="Quantity">
              </div>
              <div class="field">
                <span>Reason</span>
                <select class="input" aria-label="Reason">
                  <option v-for="reason in productsData?.inventoryReasons" :key="reason">{{ reason }}</option>
                </select>
              </div>
              <div class="field mb0">
                <span>Note</span>
                <input class="input" type="text" placeholder="e.g. Morning catch, 10 kg" aria-label="Note">
              </div>
              <div class="card-foot">
                <button class="btn btn-primary btn-block" type="button" @click="postRestockMovement">Post movement · +10 kg</button>
              </div>
              <div class="tiny muted mt8">
                Posting writes one <span class="mono">InventoryMovement</span> row and the trigger updates the cached
                balance. {{ restockProduct.name }} would go from {{ restockProduct.onHand }} kg to 16 kg and its badge back to <span class="mono">IN_STOCK</span>.
              </div>
            </div>

            <!-- Default sidebar content when no modal open -->
            <div v-if="!showEditModal && !showRestockModal" class="card">
              <div class="card-head"><h3>Quick actions</h3></div>
              <div class="stack" style="--gap: 10px">
                <button class="btn btn-primary btn-block" type="button">＋ Add new product</button>
                <button class="btn btn-block" type="button">📥 Record stock received</button>
              </div>
              <div class="note mt12 tiny">
                Adding a product creates a <span class="mono">Product</span> row with price, unit, comparison group and threshold.
                Stock starts at zero until you post a <span class="mono">RECEIVED</span> movement.
              </div>
            </div>
          </aside>
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

.center { text-align: center; }
.row-between { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.row-wrap { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.mb12 { margin-bottom: 12px; }
.mt12 { margin-top: 12px; }
.mt8 { margin-top: 8px; }
.mb0 { margin-bottom: 0; }

.badge-brand { background: var(--brand-light); color: var(--brand-dark); }
.badge-ok { background: var(--ok-bg); color: var(--ok); }
.badge-warn { background: var(--warn-bg); color: var(--warn); }
.badge-info { background: var(--info-bg); color: var(--info); }
.badge-accent { background: var(--accent-light); color: var(--accent-dark); }
.badge-danger { background: var(--danger-bg); color: var(--danger); }

.num { text-align: right; font-variant-numeric: tabular-nums; }
.mono { font-family: var(--font-mono); font-size: 0.875rem; }
.tiny { font-size: 0.75rem; }
.small { font-size: 0.8125rem; }
.muted { color: var(--muted); }

.card-foot { padding-top: 12px; border-top: 1px solid var(--line); margin-top: 12px; }
.card-head { padding-bottom: 12px; border-bottom: 1px solid var(--line); margin-bottom: 12px; }
.card-tight { padding: 12px; }

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

.grid-side { display: grid; gap: 24px; }
.grid-side { grid-template-columns: 1fr 340px; }

.meter { height: 6px; background: var(--line); border-radius: 3px; overflow: hidden; }
.meter i { display: block; height: 100%; background: var(--brand); border-radius: 3px; }
.meter i.mid { background: var(--warn); }

.note { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 0.8125rem; background: var(--info-bg); color: var(--info); border-left: 4px solid var(--info); }
.note-warn { background: var(--warn-bg); color: var(--warn); border-left-color: var(--warn); }
.note-accent { background: var(--accent-light); color: var(--accent-dark); border-left-color: var(--accent); }
.note.tiny { font-size: 0.75rem; }

.divider { border: none; border-top: 1px solid var(--line); margin: 16px 0; }

.btn-block { width: 100%; }
.btn-sm { padding: 6px 10px; font-size: 0.75rem; }
.btn-primary { background: var(--brand); border-color: var(--brand); color: white; }
.btn-primary:hover { background: var(--brand-dark); border-color: var(--brand-dark); }
.btn-accent { background: var(--accent); border-color: var(--accent); color: white; }
.btn-accent:hover { background: var(--accent-dark); border-color: var(--accent-dark); }

.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 12px; border-radius: var(--radius-pill); border: 1px solid var(--brand-line); background: var(--card); color: var(--ink); text-decoration: none; font-size: 0.8125rem; transition: all 0.15s; }
.chip:hover { border-color: var(--brand); color: var(--brand); }
.chip.on { background: var(--brand); border-color: var(--brand); color: white; }

.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.field mb0 { margin-bottom: 0; }
.field span { font-size: 0.8125rem; font-weight: 500; color: var(--ink-2); }
.field .input { padding: 8px 12px; border: 1px solid var(--line); border-radius: var(--radius-sm); font-size: 0.875rem; background: var(--card); }
.field .input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 2px var(--brand-light); }

.searchbar { display: flex; gap: 8px; }
.searchbar .input { flex: 1; }

.row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

@media (max-width: 860px) {
  .grid-side { grid-template-columns: 1fr; }
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .stat .v { font-size: 1.25rem; }
}

@media (max-width: 520px) {
  .kv { grid-template-columns: 1fr; gap: 4px; }
  .kv dt { margin-bottom: 2px; }
  .chips { gap: 6px; }
  .chip { padding: 4px 10px; font-size: 0.75rem; }
  .table th, .table td { padding: 8px; font-size: 0.8125rem; }
}
</style>