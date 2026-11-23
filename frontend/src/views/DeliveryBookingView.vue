<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const props = defineProps(['id'])

// State
const loading = ref(true)
const error = ref(null)
const deliveryBooking = ref(null)
const copied = ref(false)

// Mock data - in production this would come from an API endpoint
const mockDeliveryBooking = {
  id: 1,
  orderRef: 'ECO-20261110-0001',
  provider: 'Lalamove',
  bookingRef: 'SBX-LM-77120',
  trackingUrl: 'https://sandbox.example/track/SBX-LM-77120',
  fee: '95.00',
  status: 'DELIVERED',
  bookedAt: '10 Nov 2026, 9:20 AM',
  deliveredAt: '10 Nov 2026, 3:40 PM',
  pickup: {
    vendor: "Pedro's Fresh Catch",
    stall: 'Stall A-12',
    section: 'Section A – Fish',
    address: 'Mandaue Public Market, Mandaue City, Cebu',
    phone: '0917-555-0101'
  },
  dropoff: {
    customer: 'Maria Santos',
    address: 'Unit 4B, A.C. Cortes Ave., Mandaue City, Cebu',
    phone: '0917-555-0110'
  },
  timeline: [
    { status: 'done', title: 'Booked', detail: '<span class="mono">BOOKED</span> · 10 Nov 2026, 9:20 AM · provider accepted the booking' },
    { status: 'done', title: 'In transit', detail: '<span class="mono">IN_TRANSIT</span> · 10 Nov 2026, 2:05 PM · rider collected from Stall A-12' },
    { status: 'done', title: 'Delivered', detail: '<span class="mono">DELIVERED</span> · 10 Nov 2026, 3:40 PM · received by Maria Santos' }
  ],
  partners: [
    { name: 'GrabExpress', fee: '110.00', eta: '40 min', chosen: false },
    { name: 'Lalamove', fee: '95.00', eta: '45 min', chosen: true },
    { name: 'Maxim', fee: '85.00', eta: '55 min', chosen: false },
    { name: 'Local market rider', fee: '60.00', eta: '90 min', chosen: false }
  ],
  orderItems: [
    { name: 'Bangus 2 kg', price: '360.00' },
    { name: 'Galunggong 1 kg', price: '160.00' }
  ],
  goodsSubtotal: '520.00',
  paymentRef: 'SBX-PM-20261110-8F31A2C4'
}

async function fetchDeliveryBooking() {
  try {
    // In production: await api.get(`/orders/delivery-bookings/${props.id}/`)
    deliveryBooking.value = mockDeliveryBooking
  } catch (e) {
    error.value = 'Failed to load delivery booking'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

async function copyTrackingUrl() {
  if (deliveryBooking.value) {
    await navigator.clipboard.writeText(deliveryBooking.value.trackingUrl)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function goBack() {
  router.push('/order-tracking')
}

onMounted(() => {
  fetchDeliveryBooking()
})

// Watch for prop changes
watch(() => props.id, () => {
  loading.value = true
  fetchDeliveryBooking()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Delivery booking</div>
        <h1>Order {{ deliveryBooking?.orderRef || props.id }}</h1>
        <p>One delivery order from {{ deliveryBooking?.pickup?.vendor || 'Pedro\'s Fresh Catch' }}, handed to a courier partner. Delivery is <strong>mocked</strong> in this project — the partner is simulated end to end.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading delivery booking...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchDeliveryBooking">Retry</button>
      </div>

      <div v-else class="grid-side" style="grid-template-columns: 1fr 330px">
        <!-- Main Content -->
        <div class="stack">
          <!-- Booking Record -->
          <section class="card">
            <div class="card-head">
              <div>
                <h3 class="mb0">🛵 {{ deliveryBooking.provider }}</h3>
                <span class="small muted">Booking reference <span class="mono">{{ deliveryBooking.bookingRef }}</span></span>
              </div>
              <span class="badge" :class="deliveryBooking.status === 'DELIVERED' ? 'badge-ok' : 'badge-info'">{{ deliveryBooking.status }}</span>
            </div>

            <dl class="kv">
              <dt>Provider</dt><dd class="mono">{{ deliveryBooking.provider }}</dd>
              <dt>Booking reference</dt><dd class="mono">{{ deliveryBooking.bookingRef }}</dd>
              <dt>Delivery fee</dt><dd>{{ formatCurrency(deliveryBooking.fee) }}</dd>
              <dt>Delivery status</dt><dd><span class="badge" :class="deliveryBooking.status === 'DELIVERED' ? 'badge-ok' : 'badge-info'">{{ deliveryBooking.status }}</span></dd>
              <dt>Booked at</dt><dd>{{ deliveryBooking.bookedAt }}</dd>
              <dt v-if="deliveryBooking.deliveredAt">Delivered at</dt><dd v-if="deliveryBooking.deliveredAt">{{ deliveryBooking.deliveredAt }}</dd>
            </dl>

            <hr class="divider">

            <div class="field mb0">
              <span>Tracking link</span>
              <div class="row">
                <input class="input mono" type="text" readonly :value="deliveryBooking.trackingUrl" aria-label="Tracking link">
                <button class="btn no-print" type="button" @click="copyTrackingUrl">{{ copied ? '✓ Copied!' : 'Copy' }}</button>
              </div>
            </div>
            <div class="note note-warn mt12 tiny">
              This URL points at a <strong>sandbox host</strong>. No live courier account exists for this project.
            </div>
          </section>

          <!-- Route -->
          <section class="card">
            <div class="card-head"><h3>Route</h3></div>
            <div class="grid grid-2">
              <div class="card card-tight" style="box-shadow: none">
                <div class="badge badge-brand mb8">Pickup from</div>
                <div style="font-weight: 650">{{ deliveryBooking.pickup.vendor }}</div>
                <div class="small muted">{{ deliveryBooking.pickup.stall }} · {{ deliveryBooking.pickup.section }}</div>
                <div class="small muted">{{ deliveryBooking.pickup.address }}</div>
                <div class="small muted mt8">📞 {{ deliveryBooking.pickup.phone }}</div>
              </div>
              <div class="card card-tight" style="box-shadow: none">
                <div class="badge badge-accent mb8">Drop off to</div>
                <div style="font-weight: 650">{{ deliveryBooking.dropoff.customer }}</div>
                <div class="small muted">{{ deliveryBooking.dropoff.address }}</div>
                <div class="small muted mt8">📞 {{ deliveryBooking.dropoff.phone }}</div>
              </div>
            </div>
          </section>

          <!-- Courier Timeline -->
          <section class="card">
            <div class="card-head"><h3>Courier progress</h3><span class="small muted">DeliveryBooking.status</span></div>
            <ul class="timeline">
              <li v-for="(step, index) in deliveryBooking.timeline" :key="index" :class="step.status">
                <span class="node"></span>
                <div class="t">{{ step.title }}</div>
                <div class="d" v-html="step.detail"></div>
              </li>
            </ul>
            <div class="note mt12 tiny">
              <strong>Why this is separate from the order status.</strong> <span class="mono">DeliveryBooking.status</span> tracks the courier. <span class="mono">Order.status</span> tracks the order. A delivery order reaches <span class="mono">COMPLETED</span> only when the courier reports <span class="mono">DELIVERED</span>.
            </div>
          </section>
        </div>

        <!-- Sidebar -->
        <aside class="stack">
          <!-- Compare Partners -->
          <div class="card">
            <div class="card-head"><h3>Compare partners</h3></div>
            <div class="table-wrap">
              <table class="table">
                <thead><tr><th>Partner</th><th class="num">Fee</th><th class="num">ETA</th></tr></thead>
                <tbody>
                  <tr v-for="partner in deliveryBooking.partners" :key="partner.name" :style="{ background: partner.chosen ? 'var(--brand-light)' : '' }">
                    <td>
                      <strong v-if="partner.chosen">{{ partner.name }}</strong>
                      <span v-else>{{ partner.name }}</span>
                      <span v-if="partner.chosen" class="badge badge-brand">Chosen</span>
                    </td>
                    <td class="num"><strong v-if="partner.chosen">{{ formatCurrency(partner.fee) }}</strong><span v-else>{{ formatCurrency(partner.fee) }}</span></td>
                    <td class="num">{{ partner.eta }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="tiny muted mt8">Cheapest is not always chosen — ETA and reliability matter for fresh fish.</div>
          </div>

          <!-- Order Total -->
          <div class="card">
            <div class="card-head"><h3>Order total</h3></div>
            <dl class="kv">
              <dt v-for="item in deliveryBooking.orderItems" :key="item.name">{{ item.name }}</dt>
              <dd v-for="item in deliveryBooking.orderItems" :key="item.name">{{ formatCurrency(item.price) }}</dd>
              <dt>Goods subtotal</dt><dd>{{ formatCurrency(deliveryBooking.goodsSubtotal) }}</dd>
              <dt>Delivery fee</dt><dd>{{ formatCurrency(deliveryBooking.fee) }}</dd>
            </dl>
            <hr class="divider">
            <div class="row-between">
              <span style="font-weight: 650">Total paid</span>
              <span class="price price-lg">{{ formatCurrency(Number(deliveryBooking.goodsSubtotal) + Number(deliveryBooking.fee)) }}</span>
            </div>
            <div class="tiny muted mt8">Payment <span class="mono">{{ deliveryBooking.paymentRef }}</span> · VERIFIED</div>
          </div>

          <!-- Pickup Alternative -->
          <div class="card">
            <div class="card-head"><h3>Pickup alternative</h3></div>
            <p class="small muted">The same order could have been collected at {{ deliveryBooking.pickup.stall }} with no delivery fee — saving {{ formatCurrency(deliveryBooking.fee) }}.</p>
            <a class="btn btn-block" href="/market-map">Show {{ deliveryBooking.pickup.stall }}</a>
          </div>

          <a class="btn btn-primary btn-block" href="/order-tracking">Back to order tracking</a>
        </aside>
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
.row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.row-wrap { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.mb0 { margin-bottom: 0; }
.mb8 { margin-bottom: 8px; }
.mt8 { margin-top: 8px; }
.mt12 { margin-top: 12px; }

.badge-brand { background: var(--brand-light); color: var(--brand-dark); }
.badge-ok { background: var(--ok-bg); color: var(--ok); }
.badge-info { background: var(--info-bg); color: var(--info); }
.badge-accent { background: var(--accent-light); color: var(--accent-dark); }

.num { text-align: right; font-variant-numeric: tabular-nums; }
.mono { font-family: var(--font-mono); font-size: 0.875rem; }
.tiny { font-size: 0.75rem; }
.small { font-size: 0.8125rem; }
.muted { color: var(--muted); }

.kv { display: grid; grid-template-columns: 140px 1fr; gap: 8px 16px; font-size: 0.875rem; }
.kv dt { color: var(--muted); }
.kv dd { margin: 0; font-weight: 500; }

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

.grid-side { display: grid; gap: 24px; }
.grid-side { grid-template-columns: 1fr 330px; }

.timeline { list-style: none; padding: 0; margin: 0; position: relative; }
.timeline::before { content: ''; position: absolute; left: 10px; top: 0; bottom: 0; width: 2px; background: var(--brand-line); }
.timeline li { position: relative; padding-left: 36px; padding-bottom: 20px; }
.timeline li:last-child { padding-bottom: 0; }
.timeline .node { position: absolute; left: 2px; top: 2px; width: 18px; height: 18px; border-radius: 50%; background: var(--card); border: 2px solid var(--brand-line); z-index: 1; }
.timeline li.done .node { background: var(--ok); border-color: var(--ok); }
.timeline li.done .node::after { content: '✓'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 0.625rem; color: white; }
.timeline li.now .node { background: var(--brand); border-color: var(--brand); animation: pulse 2s infinite; }
.timeline li.todo .node { background: var(--card); border-color: var(--brand-line); opacity: 0.5; }
@keyframes pulse { 0%, 100% { box-shadow: 0 0 0 0 var(--brand); } 50% { box-shadow: 0 0 0 6px var(--brand-light); } }
.timeline .t { font-weight: 600; }
.timeline .d { font-size: 0.8125rem; color: var(--muted); margin-top: 2px; }

.note { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 0.8125rem; background: var(--info-bg); color: var(--info); border-left: 4px solid var(--info); }
.note-warn { background: var(--warn-bg); color: var(--warn); border-left-color: var(--warn); }
.note.tiny { font-size: 0.75rem; }

.divider { border: none; border-top: 1px solid var(--line); margin: 16px 0; }

.btn-block { width: 100%; }
.no-print { display: inline-flex; }
@media print { .no-print { display: none !important; } }

@media (max-width: 860px) {
  .grid-side { grid-template-columns: 1fr; }
  .kv { grid-template-columns: 120px 1fr; }
}

@media (max-width: 520px) {
  .kv { grid-template-columns: 1fr; gap: 4px; }
  .kv dt { margin-bottom: 2px; }
  .grid-2 { grid-template-columns: 1fr; }
}
</style>