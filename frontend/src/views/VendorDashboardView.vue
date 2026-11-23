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
const dashboardData = ref(null)

// Mock data - in production this would come from API endpoints
const mockDashboardData = {
  kpis: {
    todaySales: '1300.00',
    todayWalkIns: 3,
    weekSales: '8450.00',
    weekChange: '+12%',
    monthSales: '31200.00',
    monthLabel: 'Nov 2026 to date',
    openOrders: 3,
    openOrdersBreakdown: '1 confirmed · 1 preparing · 1 ready'
  },
  salesChart: [
    { label: 'Tue 10', value: 1180, height: '62%', isBest: false },
    { label: 'Wed 11', value: 1340, height: '71%', isBest: false },
    { label: 'Thu 12', value: 980, height: '52%', isBest: false },
    { label: 'Fri 13', value: 1890, height: '100%', isBest: true },
    { label: 'Sat 14', value: 1560, height: '83%', isBest: false },
    { label: 'Sun 15', value: 260, height: '14%', isBest: false },
    { label: 'Mon 16', value: 1300, height: '69%', isBest: true, isToday: true }
  ],
  bestSellers: [
    { product: '🐟 Bangus (Milkfish)', qtySold: '42 kg', revenue: '7560.00', share: '37%' },
    { product: '🐟 Galunggong (Round Scad)', qtySold: '28 kg', revenue: '4480.00', share: '22%' },
    { product: '🐟 Tilapia', qtySold: '22 kg', revenue: '3080.00', share: '15%' },
    { product: '🐟 Tulingan (Bullet Tuna)', qtySold: '15 kg', revenue: '2850.00', share: '14%' },
    { product: '🦐 Hipon (Shrimp)', qtySold: '6 kg', revenue: '2280.00', share: '11%' }
  ],
  channelMix: [
    { label: 'Walk-in (POS)', count: 34, code: 'POS_WALKIN' },
    { label: 'Online orders', count: 18, code: 'ONLINE_ORDER' },
    { label: 'Pickup reservations', count: 5, code: 'PICKUP_RESERVATION' }
  ],
  inventoryMovement: [
    { product: '🐟 Bangus', change: -2, reason: 'SOLD_ONLINE', color: 'danger' },
    { product: '🐟 Bangus', change: -1, reason: 'SOLD_WALKIN', color: 'danger' },
    { product: '🦐 Hipon', change: +1, reason: 'ADJUSTMENT', color: 'ok' },
    { product: '🐟 Galunggong', change: -1, reason: 'SOLD_ONLINE', color: 'danger' },
    { product: '🐟 Tilapia', change: -1, reason: 'SOLD_WALKIN', color: 'danger' },
    { product: '🐟 Bangus', change: +15, reason: 'RECEIVED', color: 'ok' }
  ],
  lowStock: [
    { product: '🦐 Hipon (Shrimp)', status: 'LOW_STOCK', onHand: '6 kg', threshold: '5 kg', meter: '40%' },
    { product: '🐟 Dried Fish (Tuyo)', status: 'LOW_STOCK', onHand: '5 kg', threshold: '3 kg', meter: '35%' }
  ],
  vendorName: "Pedro's Fresh Catch",
  stall: 'Stall A-12',
  section: 'Section A – Fish'
}

async function fetchDashboard() {
  try {
    // In production: await api.get('/vendor/dashboard/')
    dashboardData.value = mockDashboardData
  } catch (e) {
    error.value = 'Failed to load dashboard'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

function goToProducts() {
  router.push('/vendor/products')
}

function goToPOS() {
  router.push('/vendor/pos')
}

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Vendor console</div>
        <h1>Sales dashboard</h1>
        <p>{{ dashboardData?.vendorName || "Pedro's Fresh Catch" }} · {{ dashboardData?.stall || 'Stall A-12' }} · {{ dashboardData?.section || 'Section A – Fish' }}. Figures cover walk-in sales recorded at the POS as well as online orders and pickup reservations.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading dashboard...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchDashboard">Retry</button>
      </div>

      <div v-else>
        <!-- KPIs -->
        <div class="grid grid-4">
          <div class="stat">
            <div class="k">Today's sales</div>
            <div class="v">{{ formatCurrency(dashboardData.kpis.todaySales) }}</div>
            <div class="sub">{{ dashboardData.kpis.todayWalkIns }} walk-in sales</div>
          </div>
          <div class="stat">
            <div class="k">This week</div>
            <div class="v">{{ formatCurrency(dashboardData.kpis.weekSales) }}</div>
            <div class="sub">{{ dashboardData.kpis.weekChange }} on last week</div>
          </div>
          <div class="stat">
            <div class="k">This month</div>
            <div class="v">{{ formatCurrency(dashboardData.kpis.monthSales) }}</div>
            <div class="sub">{{ dashboardData.kpis.monthLabel }}</div>
          </div>
          <div class="stat" style="border-color: var(--accent)">
            <div class="k">Open orders</div>
            <div class="v" style="color: var(--accent-dark)">{{ dashboardData.kpis.openOrders }}</div>
            <div class="sub">{{ dashboardData.kpis.openOrdersBreakdown }}</div>
          </div>
        </div>

        <div class="grid-side" style="grid-template-columns: 1fr 320px">
          <!-- Main Content -->
          <div class="stack">
            <!-- Sales Chart -->
            <section class="card">
              <div class="card-head">
                <h3>Sales, last 7 days</h3>
                <span class="small muted">Best day highlighted</span>
              </div>
              <div class="bars">
                <div class="bar" v-for="day in dashboardData.salesChart" :key="day.label">
                  <span class="lab">{{ formatCurrency(day.value) }}</span>
                  <i class="fill" :class="{ hi: day.isBest }" :style="{ height: day.height }"></i>
                  <span class="lab">{{ day.label }}</span>
                </div>
              </div>
              <div class="card-foot tiny muted">
                Friday is the peak — market day. Sunday is short because the stall closes at noon. The last bar is
                <strong>today</strong>, and it is still climbing.
              </div>
            </section>

            <!-- Best Sellers -->
            <section class="card">
              <div class="card-head">
                <h3>Best sellers, this month</h3>
                <span class="small muted">by revenue</span>
              </div>
              <div class="table-wrap">
                <table class="table">
                  <thead>
                    <tr><th>Product</th><th class="num">Qty sold</th><th class="num">Revenue</th><th class="num">Share</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in dashboardData.bestSellers" :key="item.product">
                      <td>{{ item.product }}</td>
                      <td class="num">{{ item.qtySold }}</td>
                      <td class="num"><strong>{{ formatCurrency(item.revenue) }}</strong></td>
                      <td class="num">
                        <div class="meter" style="min-width: 70px"><i :style="{ width: item.share }"></i></div>
                        <span class="tiny muted">{{ item.share }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <!-- Channel Mix -->
            <section class="card">
              <div class="card-head"><h3>Where the sales come from</h3></div>
              <div class="grid grid-3">
                <div class="stat" style="box-shadow: none" v-for="channel in dashboardData.channelMix" :key="channel.code">
                  <div class="k">{{ channel.label }}</div>
                  <div class="v">{{ channel.count }}</div>
                  <div class="sub"><span class="mono tiny">{{ channel.code }}</span></div>
                </div>
              </div>
              <div class="note mt12 tiny">
                Walk-in still dominates — which is why the POS is part of the system rather than an afterthought.
                The digital store adds reach without replacing the counter.
              </div>
            </section>
          </div>

          <!-- Sidebar -->
          <aside class="stack">
            <!-- Inventory Movement -->
            <div class="card">
              <div class="card-head"><h3>Inventory movement</h3><span class="small muted">recent</span></div>
              <div class="table-wrap">
                <table class="table">
                  <thead><tr><th>Product</th><th class="num">Change</th><th>Reason</th></tr></thead>
                  <tbody>
                    <tr v-for="(movement, index) in dashboardData.inventoryMovement" :key="index">
                      <td>{{ movement.product }}</td>
                      <td class="num" :style="{ color: 'var(--' + movement.color + ')' }">
                        <span v-if="movement.change > 0">+</span>{{ movement.change }}
                      </td>
                      <td class="tiny mono">{{ movement.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="card-foot tiny muted">
                <strong>Bangus ledger:</strong> +15 received, −2 online, −1 walk-in → balance <strong>12 kg</strong>.
              </div>
            </div>

            <!-- Low Stock -->
            <div class="card" style="border-color: var(--warn)">
              <div class="card-head"><h3>⚠️ Low stock</h3><span class="badge badge-warn">{{ dashboardData.lowStock.length }} items</span></div>
              <div class="stack" style="--gap: 10px">
                <div v-for="item in dashboardData.lowStock" :key="item.product">
                  <div class="row-between small"><span>{{ item.product }}</span><span class="badge badge-warn">{{ item.status }}</span></div>
                  <div class="meter mt8"><i class="mid" :style="{ width: item.meter }"></i></div>
                  <div class="tiny muted mt8">{{ item.onHand }} on hand · threshold {{ item.threshold }}</div>
                </div>
              </div>
              <div class="card-foot">
                <a class="btn btn-sm btn-block" @click="goToProducts">Restock in Products</a>
              </div>
            </div>

            <div class="note tiny">
              Stock is <strong>derived from the movement ledger</strong>, not typed in by hand. Every sale, receipt and
              spoilage entry is a row; the balance is their sum.
            </div>

            <a class="btn btn-primary btn-block" @click="goToPOS">Open POS terminal</a>
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

.stat { text-align: center; padding: 16px; background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); }
.stat .k { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
.stat .v { font-size: 1.5rem; font-weight: 700; color: var(--ink); }
.stat .sub { font-size: 0.75rem; color: var(--muted); margin-top: 4px; }

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
.grid-side { grid-template-columns: 1fr 320px; }

.bars { display: flex; align-items: flex-end; gap: 12px; height: 160px; padding: 12px 0; }
.bar { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 0; }
.bar .lab { font-size: 0.625rem; color: var(--muted); white-space: nowrap; }
.bar .fill { width: 100%; background: var(--brand-line); border-radius: 2px 2px 0 0; transition: height 0.3s; }
.bar .fill.hi { background: var(--brand); }

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
.btn-lg { padding: 14px 20px; font-size: 1rem; }
.btn-primary { background: var(--brand); border-color: var(--brand); color: white; }
.btn-primary:hover { background: var(--brand-dark); border-color: var(--brand-dark); }
.btn-accent { background: var(--accent); border-color: var(--accent); color: white; }
.btn-accent:hover { background: var(--accent-dark); border-color: var(--accent-dark); }
.btn-danger { background: var(--danger); border-color: var(--danger); color: white; }
.btn-danger:hover { background: #991111; border-color: #991111; }
.btn-ghost { background: transparent; color: var(--ink); }
.btn-ghost:hover { background: var(--neutral-bg); }

.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 12px; border-radius: var(--radius-pill); border: 1px solid var(--brand-line); background: var(--card); color: var(--ink); text-decoration: none; font-size: 0.8125rem; transition: all 0.15s; }
.chip:hover { border-color: var(--brand); color: var(--brand); }
.chip.on { background: var(--brand); border-color: var(--brand); color: white; }

.searchbar { display: flex; gap: 8px; }
.searchbar .input { flex: 1; }

.row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

@media (max-width: 860px) {
  .grid-side { grid-template-columns: 1fr; }
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .bars { height: 120px; }
  .stat .v { font-size: 1.25rem; }
}

@media (max-width: 520px) {
  .bars { height: 100px; gap: 8px; }
  .bar .lab { font-size: 0.5625rem; }
  .kv { grid-template-columns: 1fr; gap: 4px; }
  .kv dt { margin-bottom: 2px; }
  .chips { gap: 6px; }
  .chip { padding: 4px 10px; font-size: 0.75rem; }
}
</style>