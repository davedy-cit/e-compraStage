<script setup>
import { ref, computed, onMounted, watch as vueWatch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const activeFilter = ref('All')
const searchQuery = ref('')
const marketData = ref(null)

// Mock data - in production this would come from an API endpoint
const mockMarketData = {
  sections: [
    {
      name: 'Section A — Fish',
      stalls: [
        { no: 'A-12', name: "Pedro's Fresh Catch", category: 'Fish', products: 6, registered: true },
        { no: 'A-14', name: "Ong's Seafood", category: 'Fish', products: 0, registered: false }
      ]
    },
    {
      name: 'Section B — Vegetables',
      stalls: [
        { no: 'B-07', name: "Rosa's Gulay Stand", category: 'Vegetables', products: 7, registered: true },
        { no: 'B-09', name: "Aling Nena's Gulay", category: 'Vegetables', products: 0, registered: false }
      ]
    },
    {
      name: 'Section C — Meat & Poultry',
      stalls: [
        { no: 'C-03', name: 'Bautista Meat Shop', category: 'Meat', products: 4, registered: true },
        { no: 'C-09', name: "Nena's Manok", category: 'Poultry', products: 4, registered: true }
      ]
    },
    {
      name: 'Section D — Fruits',
      stalls: [
        { no: 'D-02', name: 'Villamor Fruits & Gulay', category: 'Fruits', products: 5, registered: true },
        { no: 'D-05', name: 'Cebu Fruit Corner', category: 'Fruits', products: 0, registered: false }
      ]
    },
    {
      name: 'Section E — Dry Goods',
      stalls: [
        { no: 'E-01', name: "Tan's Rice & Dry Goods", category: 'Rice', products: 8, registered: true },
        { no: 'E-03', name: 'Mandaue Grocery Stall', category: 'Dry goods', products: 0, registered: false }
      ]
    }
  ],
  vendors: [
    { name: "Pedro's Fresh Catch", stall: 'A-12', section: 'A — Fish', category: 'Fish', products: 6, phone: '0917-555-0101' },
    { name: "Rosa's Gulay Stand", stall: 'B-07', section: 'B — Vegetables', category: 'Vegetables', products: 7, phone: '0917-555-0102' },
    { name: 'Bautista Meat Shop', stall: 'C-03', section: 'C — Meat & Poultry', category: 'Meat', products: 4, phone: '0917-555-0103' },
    { name: "Nena's Manok", stall: 'C-09', section: 'C — Meat & Poultry', category: 'Poultry', products: 4, phone: '0917-555-0104' },
    { name: 'Villamor Fruits & Gulay', stall: 'D-02', section: 'D — Fruits', category: 'Fruits', products: 5, phone: '0917-555-0105' },
    { name: "Tan's Rice & Dry Goods", stall: 'E-01', section: 'E — Dry Goods', category: 'Rice', products: 8, phone: '0917-555-0106' }
  ],
  sectionStats: [
    { section: 'A — Fish', stalls: 2, online: 1 },
    { section: 'B — Vegetables', stalls: 2, online: 1 },
    { section: 'C — Meat & Poultry', stalls: 2, online: 2 },
    { section: 'D — Fruits', stalls: 2, online: 1 },
    { section: 'E — Dry Goods', stalls: 2, online: 1 }
  ]
}

const filters = [
  'All',
  '🐟 Fish',
  '🥩 Meat',
  '🍗 Poultry',
  '🍎 Fruits',
  '🥬 Vegetables',
  '🍚 Rice',
  '🫙 Dry goods',
  '🧂 Spices'
]

const filteredSections = computed(() => {
  if (activeFilter.value === 'All') return marketData.value.sections

  const categoryMap = {
    '🐟 Fish': 'Fish',
    '🥩 Meat': 'Meat',
    '🍗 Poultry': 'Poultry',
    '🍎 Fruits': 'Fruits',
    '🥬 Vegetables': 'Vegetables',
    '🍚 Rice': 'Rice',
    '🫙 Dry goods': 'Dry goods',
    '🧂 Spices': 'Spices'
  }

  const targetCategory = categoryMap[activeFilter.value]
  return marketData.value.sections.map(section => ({
    ...section,
    stalls: section.stalls.filter(stall => stall.category === targetCategory)
  })).filter(section => section.stalls.length > 0)
})

const filteredVendors = computed(() => {
  if (!searchQuery.value) return marketData.value.vendors
  const q = searchQuery.value.toLowerCase()
  return marketData.value.vendors.filter(v =>
    v.name.toLowerCase().includes(q) ||
    v.stall.toLowerCase().includes(q) ||
    v.category.toLowerCase().includes(q)
  )
})

const totalStalls = computed(() => marketData.value.sections.reduce((sum, s) => sum + s.stalls.length, 0))
const registeredVendors = computed(() => marketData.value.vendors.length)

async function fetchMarketData() {
  try {
    // In production: await api.get('/catalog/market-map/')
    marketData.value = mockMarketData
  } catch (e) {
    error.value = 'Failed to load market map'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function setFilter(filter) {
  activeFilter.value = filter
  // Update URL query param for shareable state
  router.replace({ query: { ...route.query, filter: filter } })
}

function initFromRoute() {
  // Initialize from URL query
  if (route.query.filter) {
    activeFilter.value = route.query.filter
  }
}

onMounted(() => {
  initFromRoute()
  fetchMarketData()
})

// Watch for route query changes
vueWatch(() => route.query.filter, (newVal) => {
  if (newVal && newVal !== activeFilter.value) {
    activeFilter.value = newVal
  }
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Interactive market map</div>
        <h1>Mandaue Public Market</h1>
        <p>Every section, stall number and vendor at a glance. Filter by category to plan your route before you leave home.</p>
      </div>

      <!-- Filter + Finder -->
      <div class="card card-tight">
        <div class="row-between">
          <div class="chips">
            <a v-for="filter in filters" :key="filter" class="chip" :class="{ on: activeFilter === filter }" @click.prevent="setFilter(filter)">{{ filter }}</a>
          </div>
          <div class="searchbar" style="max-width: 290px">
            <input class="input" type="search" placeholder="Find a stall or vendor…" aria-label="Find a stall" v-model="searchQuery">
            <button class="btn" type="button">Find</button>
          </div>
        </div>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading market map...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchMarketData">Retry</button>
      </div>

      <div v-else class="grid-side" style="grid-template-columns: 1fr 280px">
        <!-- The Map -->
        <div class="map">
          <div class="row-between mb12">
            <span class="badge badge-brand">⬆ Main entrance — A.C. Cortes Ave. side</span>
            <span class="tiny muted">{{ totalStalls }} stalls shown · {{ registeredVendors }} registered vendors</span>
          </div>

          <div class="section" v-for="section in filteredSections" :key="section.name">
            <h4>{{ section.name }}</h4>
            <div class="stalls">
              <div v-for="stall in section.stalls" :key="stall.no" class="stall" :class="{ pin: stall.registered }">
                <span class="no">{{ stall.no }}</span>
                <span class="nm">{{ stall.name }}</span>
                <span class="cat">{{ getCategoryEmoji(stall.category) }} {{ stall.category }} · {{ stall.registered ? stall.products + ' products listed' : 'not registered' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <aside class="stack">
          <!-- Legend -->
          <div class="card">
            <div class="card-head"><h3>Legend</h3></div>
            <div class="stack" style="--gap: 8px">
              <div class="row small">
                <span class="stall pin" style="min-width: 0; padding: 4px 8px"><span class="no">A-12</span></span>
                <span>Vendor selling on E-Compra</span>
              </div>
              <div class="row small">
                <span class="stall" style="min-width: 0; padding: 4px 8px"><span class="no">A-14</span></span>
                <span>Stall with no online store</span>
              </div>
              <div class="row small">
                <span style="display: inline-block; width: 14px; height: 14px; border: 2px dashed var(--brand-line); border-radius: 4px"></span>
                <span>Market section</span>
              </div>
            </div>
          </div>

          <!-- Sections -->
          <div class="card">
            <div class="card-head"><h3>Sections</h3><span class="small muted">{{ marketData.sections.length }}</span></div>
            <div class="table-wrap">
              <table class="table">
                <thead><tr><th>Section</th><th class="num">Stalls</th><th class="num">Online</th></tr></thead>
                <tbody>
                  <tr v-for="stat in marketData.sectionStats" :key="stat.section">
                    <td><a href="/catalog">{{ stat.section }}</a></td>
                    <td class="num">{{ stat.stalls }}</td>
                    <td class="num">{{ stat.online }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Registered Vendors -->
          <div class="card">
            <div class="card-head"><h3>Registered vendors</h3></div>
            <div class="stack" style="--gap: 10px">
              <div v-for="vendor in filteredVendors" :key="vendor.name">
                <div class="small" style="font-weight: 650"><a href="/catalog">{{ vendor.name }}</a></div>
                <div class="tiny muted">{{ vendor.stall }} · {{ getCategoryEmoji(vendor.category) }} {{ vendor.category }}</div>
              </div>
            </div>
          </div>

          <div class="note tiny">
            This is a <strong>stall layout inside one market building</strong> — not a street map. That is why no
            mapping library is needed: sections, stall numbers and vendor pins are all the data the feature requires.
          </div>
        </aside>
      </div>

      <!-- Vendors in a section (example: Section B) -->
      <section class="card">
        <div class="card-head"><h3>Vendors in Section B — Vegetables</h3><span class="badge badge-brand">1 registered</span></div>
        <div class="grid grid-2">
          <div class="pcard">
            <div class="thumb">🥬</div>
            <div class="body">
              <div class="name">Rosa's Gulay Stand <span style="color: var(--danger)">♥</span></div>
              <div class="vendor">📍 Stall B-07 · Section B – Vegetables</div>
              <div class="row-wrap">
                <span class="badge badge-ok"><i class="dot"></i>7 products listed</span>
                <span class="badge">📞 0917-555-0102</span>
              </div>
              <div class="foot">
                <a class="btn btn-sm btn-primary" href="/catalog">View store</a>
                <a class="btn btn-sm" href="/favorites-history">♡ Favorite</a>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card-head"><h3>Getting there</h3></div>
            <p class="small muted">Enter from the <strong>A.C. Cortes Ave. side</strong>, walk past Section A (Fish) and
               turn right. Section B is the second row of stalls on your left; B-07 is midway down.</p>
            <div class="note tiny">Stall numbers ascend along each row — even numbers on one side, odd on the other.</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    getCategoryEmoji(category) {
      const emojis = {
        'Fish': '🐟',
        'Meat': '🥩',
        'Poultry': '🍗',
        'Fruits': '🍎',
        'Vegetables': '🥬',
        'Rice': '🍚',
        'Dry goods': '🫙',
        'Spices': '🧂'
      }
      return emojis[category] || '📦'
    }
  }
}
</script>

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
.row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.row-wrap { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.mb12 { margin-bottom: 12px; }
.mt12 { margin-top: 12px; }
.mt8 { margin-top: 8px; }

.badge-brand { background: var(--brand-light); color: var(--brand-dark); }
.badge-ok { background: var(--ok-bg); color: var(--ok); }

.num { text-align: right; font-variant-numeric: tabular-nums; }
.mono { font-family: var(--font-mono); font-size: 0.875rem; }
.tiny { font-size: 0.75rem; }
.small { font-size: 0.8125rem; }
.muted { color: var(--muted); }

.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 12px; border-radius: var(--radius-pill); border: 1px solid var(--brand-line); background: var(--card); color: var(--ink); text-decoration: none; font-size: 0.8125rem; transition: all 0.15s; }
.chip:hover { border-color: var(--brand); color: var(--brand); }
.chip.on { background: var(--brand); border-color: var(--brand); color: white; }

.searchbar { display: flex; gap: 8px; }
.searchbar .input { flex: 1; }

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

.grid-side { display: grid; gap: 24px; }
.grid-side { grid-template-columns: 1fr 280px; }

.map { display: flex; flex-direction: column; gap: 16px; }
.section { border: 1px solid var(--brand-line); border-radius: var(--radius); overflow: hidden; background: var(--card); }
.section h4 { margin: 0; padding: 12px 16px; background: var(--brand-light); color: var(--brand-dark); font-size: 0.9375rem; font-weight: 600; border-bottom: 1px solid var(--brand-line); }
.stalls { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.stall { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: var(--radius-sm); background: var(--bg); border: 1px solid var(--line); transition: all 0.15s; }
.stall:hover { border-color: var(--brand-line); background: var(--brand-light); }
.stall.pin { border-color: var(--brand); background: var(--brand-light); box-shadow: 0 0 0 1px var(--brand); }
.stall .no { font-family: var(--font-mono); font-weight: 700; font-size: 0.875rem; color: var(--brand); min-width: 56px; }
.stall .nm { font-weight: 600; flex: 1; }
.stall .cat { font-size: 0.75rem; color: var(--muted); }

.note { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 0.8125rem; background: var(--info-bg); color: var(--info); border-left: 4px solid var(--info); }
.note.tiny { font-size: 0.75rem; }

.divider { border: none; border-top: 1px solid var(--line); margin: 16px 0; }

.pcard { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; background: var(--card); }
.pcard .thumb { width: 100%; height: 140px; display: grid; place-items: center; font-size: 3rem; background: var(--brand-light); }
.pcard .body { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.pcard .name { font-weight: 600; }
.pcard .vendor { font-size: 0.8125rem; color: var(--muted); }
.pcard .foot { display: flex; gap: 8px; padding-top: 8px; border-top: 1px solid var(--line); margin-top: 4px; }

.kv { display: grid; grid-template-columns: 140px 1fr; gap: 8px 16px; font-size: 0.875rem; }
.kv dt { color: var(--muted); }
.kv dd { margin: 0; font-weight: 500; }

@media (max-width: 860px) {
  .grid-side { grid-template-columns: 1fr; }
  .chips { order: 2; width: 100%; }
  .searchbar { order: 1; width: 100%; max-width: none; }
  .row-between { flex-direction: column; align-items: flex-start; }
  .grid-2 { grid-template-columns: 1fr; }
}

@media (max-width: 520px) {
  .stall { flex-direction: column; align-items: flex-start; gap: 4px; }
  .stall .no { min-width: auto; }
  .kv { grid-template-columns: 1fr; gap: 4px; }
  .kv dt { margin-bottom: 2px; }
  .chips { gap: 6px; }
  .chip { padding: 4px 10px; font-size: 0.75rem; }
}
</style>