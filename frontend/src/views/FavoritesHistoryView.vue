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
const activeTab = ref('favorites') // favorites, orders, reservations
const favorites = ref(null)

// Mock data - in production this would come from API endpoints
const mockFavorites = {
  stats: {
    totalOrders: 4,
    completedOrders: 2,
    totalSpent: '1325.00',
    sinceDate: '10 Nov 2026',
    favoriteVendors: 2,
    totalVendors: 6,
    reservationsHeld: 1,
    balanceDue: '145.00'
  },
  favoriteProducts: [
    { id: 1, name: 'Bangus (Milkfish)', emoji: '🐟', vendor: "Pedro's Fresh Catch", stall: 'Stall A-12', availability: 'IN_STOCK', stock: 12, unit: 'kg', price: '180.00' },
    { id: 2, name: 'Tomatoes', emoji: '🍅', vendor: "Rosa's Gulay Stand", stall: 'Stall B-07', availability: 'IN_STOCK', stock: 15, unit: 'kg', price: '80.00' },
    { id: 3, name: 'Mango (Carabao)', emoji: '🥭', vendor: 'Villamor Fruits & Gulay', stall: 'Stall D-02', availability: 'IN_STOCK', stock: 15, unit: 'kg', price: '160.00' }
  ],
  favoriteVendors: [
    { name: "Pedro's Fresh Catch", stall: 'Stall A-12', section: 'Section A – Fish', phone: '0917-555-0101', products: 6 },
    { name: "Rosa's Gulay Stand", stall: 'Stall B-07', section: 'Section B – Vegetables', phone: '0917-555-0102', products: 7 }
  ],
  orderHistory: [
    { ref: 'ECO-20261116-0001', date: '16 Nov 2026', vendor: 'Villamor Fruits & Gulay', fulfillment: 'DELIVERY', total: '320.00', status: 'CONFIRMED', payment: 'VERIFIED', canReorder: true },
    { ref: 'ECO-20261116-0002', date: '16 Nov 2026', vendor: "Rosa's Gulay Stand", fulfillment: 'PICKUP', total: '50.00', status: 'CONFIRMED', payment: 'VERIFIED', canReorder: true },
    { ref: 'ECO-20261111-0003', date: '11 Nov 2026', vendor: "Pedro's Fresh Catch", fulfillment: 'WALK_IN', total: '340.00', status: 'COMPLETED', payment: 'VERIFIED', canReorder: true },
    { ref: 'ECO-20261110-0001', date: '10 Nov 2026', vendor: "Pedro's Fresh Catch", fulfillment: 'DELIVERY', total: '615.00', status: 'COMPLETED', payment: 'VERIFIED', canReorder: false, viewUrl: '/order-tracking' }
  ],
  reservationHistory: [
    { ref: 'ECO-20261112-0002', date: '12 Nov 2026', vendor: "Rosa's Gulay Stand", total: '290.00', downPayment: '145.00', balanceDue: '145.00', status: 'READY_FOR_PICKUP', detailUrl: '/pickup-reservation' }
  ]
}

async function fetchFavorites() {
  try {
    // In production: await api.get('/accounts/favorites/')
    favorites.value = mockFavorites
  } catch (e) {
    error.value = 'Failed to load favorites & history'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

function getStatusBadgeClass(status) {
  const classes = {
    'CONFIRMED': 'badge-brand',
    'COMPLETED': 'badge-ok',
    'PENDING_PAYMENT': 'badge-warn',
    'CANCELLED': 'badge-danger',
    'PREPARING': 'badge-info',
    'OUT_FOR_DELIVERY': 'badge-info',
    'VERIFIED': 'badge-ok',
    'READY_FOR_PICKUP': 'badge-accent'
  }
  return classes[status] || 'badge'
}

function getFulfillmentBadgeClass(fulfillment) {
  const classes = {
    'DELIVERY': 'badge-info',
    'PICKUP': 'badge',
    'WALK_IN': 'badge-warn'
  }
  return classes[fulfillment] || 'badge'
}

function getAvailabilityBadge(availability, stock) {
  if (availability === 'OUT_OF_STOCK' || stock === 0) {
    return { class: 'badge badge-danger', text: 'Out of stock' }
  }
  if (availability === 'LOW_STOCK' || stock <= 10) {
    return { class: 'badge badge-warn', text: `${stock} left` }
  }
  return { class: 'badge badge-ok', text: `✓ ${stock} ${stock === 1 ? '' : 'kg'}` }
}

function navigateToProduct(productId) {
  router.push(`/product/${productId}`)
}

async function handleReorder(orderRef) {
  // In production: call reorder API
  alert(`Reorder for ${orderRef} - would refill cart with same items at today's prices`)
}

onMounted(() => {
  fetchFavorites()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">{{ authStore.user?.username || 'Maria Santos' }}</div>
        <h1>Favorites & history</h1>
        <p>Your saved products and vendors, plus everything you have ordered or reserved at the market.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading favorites & history...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchFavorites">Retry</button>
      </div>

      <div v-else>
        <!-- Stats -->
        <div class="grid grid-4">
          <div class="stat"><div class="k">Total orders</div><div class="v">{{ favorites.stats.totalOrders }}</div><div class="sub">{{ favorites.stats.completedOrders }} completed</div></div>
          <div class="stat"><div class="k">Total spent</div><div class="v">{{ formatCurrency(favorites.stats.totalSpent) }}</div><div class="sub">since {{ favorites.stats.sinceDate }}</div></div>
          <div class="stat"><div class="k">Favorite vendors</div><div class="v">{{ favorites.stats.favoriteVendors }}</div><div class="sub">of {{ favorites.stats.totalVendors }} at the market</div></div>
          <div class="stat"><div class="k">Reservations held</div><div class="v">{{ favorites.stats.reservationsHeld }}</div><div class="sub">{{ formatCurrency(favorites.stats.balanceDue) }} balance due</div></div>
        </div>

        <!-- Tab Navigation -->
        <div class="chips mb12" style="justify-content: flex-start;">
          <a class="chip" :class="{ on: activeTab === 'favorites' }" @click.prevent="activeTab = 'favorites'">♡ Favorites</a>
          <a class="chip" :class="{ on: activeTab === 'orders' }" @click.prevent="activeTab = 'orders'">📦 Orders</a>
          <a class="chip" :class="{ on: activeTab === 'reservations' }" @click.prevent="activeTab = 'reservations'">📋 Reservations</a>
        </div>

        <!-- Favorites Tab -->
        <section v-if="activeTab === 'favorites'">
          <!-- Favorite Products -->
          <div class="row-between mb12">
            <h2 class="mb0">♡ Favorite products</h2>
            <span class="small muted">{{ favorites.favoriteProducts.length }} saved</span>
          </div>
          <div class="grid grid-3">
            <article class="pcard" v-for="product in favorites.favoriteProducts" :key="product.id">
              <div class="thumb">{{ product.emoji }}</div>
              <div class="body">
                <div class="row-between">
                  <span class="name">{{ product.name }}</span>
                  <span style="color: var(--danger); font-size: 1.1rem">♥</span>
                </div>
                <div class="vendor">{{ product.vendor }} · {{ product.stall }}</div>
                <div class="row-wrap">
                  <span :class="getAvailabilityBadge(product.availability, product.stock).class"><i class="dot"></i>{{ getAvailabilityBadge(product.availability, product.stock).text }}</span>
                  <span class="unit">{{ product.stock }} {{ product.unit }}</span>
                </div>
                <div class="foot">
                  <span class="price">{{ formatCurrency(product.price) }} <span class="unit">/ {{ product.unit }}</span></span>
                  <a class="btn btn-sm btn-primary" @click="navigateToProduct(product.id)">Add</a>
                </div>
              </div>
            </article>
          </div>
          <div class="note mt12 tiny">
            A favorite is stored as a <span class="mono">FavoriteProduct</span> row keyed on
            <span class="mono">(user, product)</span> — so the same product can never be saved twice.
          </div>

          <!-- Favorite Vendors -->
          <section class="mt24">
            <div class="row-between mb12">
              <h2 class="mb0">♡ Favorite vendors</h2>
              <span class="small muted">{{ favorites.favoriteVendors.length }} saved</span>
            </div>
            <div class="grid grid-2">
              <div class="card" v-for="vendor in favorites.favoriteVendors" :key="vendor.name">
                <div class="row-between">
                  <div>
                    <div style="font-weight: 650">{{ vendor.name }} <span style="color: var(--danger)">♥</span></div>
                    <div class="small muted">📍 {{ vendor.stall }} · {{ vendor.section }}</div>
                    <div class="small muted">📞 {{ vendor.phone }}</div>
                  </div>
                  <span class="badge badge-ok">{{ vendor.products }} products</span>
                </div>
                <div class="card-foot row-wrap">
                  <a class="btn btn-sm btn-primary" href="/catalog">View store</a>
                  <a class="btn btn-sm" href="/market-map">Show stall</a>
                </div>
              </div>
            </div>
          </section>
        </section>

        <!-- Orders Tab -->
        <section v-else-if="activeTab === 'orders'" class="card">
          <div class="card-head">
            <h2 class="mb0">Order history</h2>
            <span class="small muted">Newest first</span>
          </div>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Reference</th><th>Date</th><th>Vendor</th><th>Fulfillment</th>
                  <th class="num">Total</th><th>Status</th><th>Payment</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in favorites.orderHistory" :key="order.ref">
                  <td class="mono">{{ order.ref }}</td>
                  <td>{{ order.date }}</td>
                  <td>{{ order.vendor }}</td>
                  <td><span class="badge" :class="getFulfillmentBadgeClass(order.fulfillment)">{{ order.fulfillment }}</span></td>
                  <td class="num">{{ formatCurrency(order.total) }}</td>
                  <td><span class="badge" :class="getStatusBadgeClass(order.status)">{{ order.status }}</span></td>
                  <td><span class="badge" :class="getStatusBadgeClass(order.payment)">{{ order.payment }}</span></td>
                  <td>
                    <button v-if="order.canReorder" class="btn btn-sm" type="button" @click="handleReorder(order.ref)">Reorder</button>
                    <a v-else class="btn btn-sm" :href="order.viewUrl">View</a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-foot tiny muted">
            <strong>Reorder</strong> refills your cart with the same items and quantities at today's prices — you still
            confirm before anything is created.
          </div>
        </section>

        <!-- Reservations Tab -->
        <section v-else-if="activeTab === 'reservations'" class="card">
          <div class="card-head">
            <h2 class="mb0">Reservation history</h2>
            <span class="small muted">Pickup reservations</span>
          </div>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Reference</th><th>Date</th><th>Vendor</th><th class="num">Total</th>
                  <th class="num">Down payment</th><th class="num">Balance due</th><th>Status</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="res in favorites.reservationHistory" :key="res.ref">
                  <td class="mono">{{ res.ref }}</td>
                  <td>{{ res.date }}</td>
                  <td>{{ res.vendor }}</td>
                  <td class="num">{{ formatCurrency(res.total) }}</td>
                  <td class="num">{{ formatCurrency(res.downPayment) }}</td>
                  <td class="num"><strong style="color: var(--accent)">{{ formatCurrency(res.balanceDue) }}</strong></td>
                  <td><span class="badge" :class="getStatusBadgeClass(res.status)">{{ res.status }}</span></td>
                  <td><a class="btn btn-sm btn-accent" :href="res.detailUrl">Details</a></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-foot">
            <div class="note note-warn tiny mb0">
              Balance is settled in cash at the stall. If the pickup window closes without collection, the reservation is
              released and the down payment is forfeited.
            </div>
          </div>
        </section>
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
.mt24 { margin-top: 24px; }
.mb0 { margin-bottom: 0; }
.mt8 { margin-top: 8px; }

.badge-brand { background: var(--brand-light); color: var(--brand-dark); }
.badge-ok { background: var(--ok-bg); color: var(--ok); }
.badge-warn { background: var(--warn-bg); color: var(--warn); }
.badge-info { background: var(--info-bg); color: var(--info); }
.badge-accent { background: var(--accent-light); color: var(--accent-dark); }
.badge-danger { background: var(--danger-bg); color: var(--danger); }

.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 12px; border-radius: var(--radius-pill); border: 1px solid var(--brand-line); background: var(--card); color: var(--ink); text-decoration: none; font-size: 0.8125rem; transition: all 0.15s; }
.chip:hover { border-color: var(--brand); color: var(--brand); }
.chip.on { background: var(--brand); border-color: var(--brand); color: white; }

.num { text-align: right; font-variant-numeric: tabular-nums; }
.mono { font-family: var(--font-mono); font-size: 0.875rem; }
.tiny { font-size: 0.75rem; }
.small { font-size: 0.8125rem; }
.muted { color: var(--muted); }

.stat { text-align: center; padding: 16px; background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); }
.stat .k { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
.stat .v { font-size: 1.5rem; font-weight: 700; color: var(--ink); }
.stat .sub { font-size: 0.75rem; color: var(--muted); margin-top: 4px; }

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

.pcard { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; background: var(--card); }
.pcard .thumb { width: 100%; height: 140px; display: grid; place-items: center; font-size: 3rem; background: var(--brand-light); }
.pcard .body { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.pcard .name { font-weight: 600; }
.pcard .vendor { font-size: 0.8125rem; color: var(--muted); }
.pcard .foot { display: flex; gap: 8px; padding-top: 8px; border-top: 1px solid var(--line); margin-top: 4px; }

.note { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 0.8125rem; background: var(--info-bg); color: var(--info); border-left: 4px solid var(--info); }
.note-warn { background: var(--warn-bg); color: var(--warn); border-left-color: var(--warn); }
.note.tiny { font-size: 0.75rem; }

.divider { border: none; border-top: 1px solid var(--line); margin: 16px 0; }

.kv { display: grid; grid-template-columns: 140px 1fr; gap: 8px 16px; font-size: 0.875rem; }
.kv dt { color: var(--muted); }
.kv dd { margin: 0; font-weight: 500; }

@media (max-width: 860px) {
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .chips { width: 100%; }
}

@media (max-width: 520px) {
  .stat .v { font-size: 1.25rem; }
  .pcard .thumb { height: 100px; font-size: 2rem; }
}
</style>