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
const reservation = ref(null)
const activeTab = ref('summary') // summary, payment, timeline

// Mock data - in production this would come from an API endpoint
const mockReservation = {
  reference: 'ECO-20261112-0002',
  type: 'PICKUP_RESERVATION',
  status: 'READY_FOR_PICKUP',
  vendor: {
    name: "Rosa's Gulay Stand",
    stall_location: 'Stall B-07',
    market_section: 'Section B – Vegetables',
    contact_phone: '0917-555-0102'
  },
  pickupWindow: '12 Nov 2026, 4:00–6:00 PM',
  reservedOn: '12 Nov 2026, 7:45 AM',
  orderNumber: '2 of 4',
  items: [
    { name: 'Tomatoes', emoji: '🍅', unitPrice: '80.00', unit: 'kg', qty: 3, subtotal: '240.00' },
    { name: 'Kangkong (Water Spinach)', emoji: '🥬', unitPrice: '15.00', unit: 'bundle', qty: 2, subtotal: '30.00' },
    { name: 'Pechay (Chinese Cabbage)', emoji: '🥬', unitPrice: '20.00', unit: 'bundle', qty: 1, subtotal: '20.00' }
  ],
  total: '290.00',
  downPaymentPercent: 50,
  downPaymentPaid: '145.00',
  balanceDue: '145.00',
  downPayment: {
    provider: 'GCash',
    providerRef: 'SBX-PM-20261112-C19D4E77',
    amount: '145.00',
    status: 'VERIFIED',
    paidAt: '12 Nov 2026, 7:47 AM'
  },
  timeline: [
    { status: 'done', title: 'Reservation placed', detail: '12 Nov 2026, 7:45 AM' },
    { status: 'done', title: 'Down payment confirmed', detail: '₱145.00 verified · 7:47 AM' },
    { status: 'done', title: 'Vendor preparing your order', detail: "Rosa's Gulay Stand · 11:05 AM" },
    { status: 'now', title: 'Ready for pickup', detail: 'Collect at Stall B-07 before 6:00 PM' },
    { status: 'todo', title: 'Full payment upon pickup', detail: '₱145.00 in cash at the stall' },
    { status: 'todo', title: 'Completed', detail: 'Order closed' }
  ],
  holdExpiresAt: '6:00 PM'
}

async function fetchReservation() {
  try {
    // In production: await api.get(`/orders/reservations/${route.params.id}/`)
    // For now using mock data
    reservation.value = mockReservation
  } catch (e) {
    error.value = 'Failed to load reservation'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

function printReservation() {
  window.print()
}

function goBack() {
  router.push('/order-tracking')
}

onMounted(() => {
  fetchReservation()
})
</script>

<template>
  <div class="page">
    <div class="wrap-narrow stack">
      <!-- Page Header -->
      <div class="pagehead center">
        <div class="eyebrow">Reservation confirmed</div>
        <h1>Your vegetables are being held</h1>
        <p style="margin:0 auto">{{ reservation?.vendor?.name }} has reserved your items. Pay a small down payment now, then settle the balance in cash when you collect.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px">
        <div class="spinner"></div>
        <p class="muted mt12">Loading reservation...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger)">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchReservation">Retry</button>
      </div>

      <div v-else>
        <!-- Reference Card -->
        <div class="card center" style="border-color: var(--brand); background: var(--brand-light)">
          <div class="tiny" style="text-transform: uppercase; letter-spacing: .08em; font-weight: 700; color: var(--brand-dark)">Reservation reference</div>
          <div class="mono" style="font-size: 1.75rem; font-weight: 700; letter-spacing: .02em; margin: 6px 0">{{ reservation.reference }}</div>
          <div class="small muted">Show this number at the stall when you collect.</div>
          <div class="row-wrap mt12" style="justify-content: center">
            <span class="badge badge-brand">{{ reservation.type }}</span>
            <span class="badge badge-ok"><i class="dot"></i>{{ reservation.status }}</span>
          </div>
        </div>

        <!-- Summary Card -->
        <div class="card">
          <div class="card-head"><h3>Reservation summary</h3><span class="badge badge-info">Order {{ reservation.orderNumber }}</span></div>
          <dl class="kv">
            <dt>Vendor</dt><dd>{{ reservation.vendor.name }}</dd>
            <dt>Stall</dt><dd>{{ reservation.vendor.stall_location }} · {{ reservation.vendor.market_section }}</dd>
            <dt>Contact</dt><dd>{{ reservation.vendor.contact_phone }}</dd>
            <dt>Pickup window</dt><dd>{{ reservation.pickupWindow }}</dd>
            <dt>Reserved on</dt><dd>{{ reservation.reservedOn }}</dd>
          </dl>

          <hr class="divider">

          <div class="table-wrap">
            <table class="table">
              <thead><tr><th>Item</th><th class="num">Unit price</th><th class="num">Qty</th><th class="num">Subtotal</th></tr></thead>
              <tbody>
                <tr v-for="item in reservation.items" :key="item.name">
                  <td>{{ item.emoji }} {{ item.name }}</td>
                  <td class="num">₱{{ item.unitPrice }} / {{ item.unit }}</td>
                  <td class="num">{{ item.qty }}</td>
                  <td class="num">₱{{ item.subtotal }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card-foot">
            <div class="row-between mb8"><span class="muted">Reservation total</span><span class="price price-lg">₱{{ reservation.total }}</span></div>
            <div class="row-between mb8"><span class="muted">Down payment ({{ reservation.downPaymentPercent }}%)</span><span style="color: var(--ok); font-weight: 650">− {{ formatCurrency(reservation.downPaymentPaid) }} paid</span></div>
            <div class="row-between"><span style="font-weight: 650">Balance due at the stall</span><span class="price">{{ formatCurrency(reservation.balanceDue) }}</span></div>
          </div>
        </div>

        <!-- Down Payment Card -->
        <div class="card">
          <div class="card-head"><h3>Down payment</h3><span class="badge badge-ok">✓ Verified</span></div>
          <p class="small muted">A {{ reservation.downPaymentPercent }}% down payment secures the stock so the vendor does not sell it to a walk-in customer. The remaining balance is paid in cash on collection.</p>
          <div class="opt on">
            <input type="radio" name="dp" checked aria-label="GCash">
            <span><span class="t">📱 GCash</span><span class="d">{{ formatCurrency(reservation.downPayment.amount) }} · sandbox</span></span>
          </div>
          <div class="opt">
            <input type="radio" name="dp" aria-label="Maya">
            <span><span class="t">📱 Maya</span><span class="d">{{ formatCurrency(reservation.downPayment.amount) }} · sandbox</span></span>
          </div>
          <dl class="kv mt12">
            <dt>Provider</dt><dd class="mono">{{ reservation.downPayment.provider }}</dd>
            <dt>Provider reference</dt><dd class="mono">{{ reservation.downPayment.providerRef }}</dd>
            <dt>Amount</dt><dd>{{ formatCurrency(reservation.downPayment.amount) }}</dd>
            <dt>Payment status</dt><dd><span class="badge badge-ok">{{ reservation.downPayment.status }}</span></dd>
            <dt>Paid at</dt><dd>{{ reservation.downPayment.paidAt }}</dd>
          </dl>
          <div class="note mt12 tiny">
            Payments run in <strong>sandbox / test mode</strong> — no real money moves. A redirect alone is not proof of payment; the server verifies it before the reservation is confirmed.
          </div>
        </div>

        <!-- Timeline Card -->
        <div class="card">
          <div class="card-head"><h3>What happens next</h3></div>
          <ul class="timeline">
            <li v-for="(step, index) in reservation.timeline" :key="index" :class="step.status">
              <span class="node"></span>
              <div class="t">{{ step.title }}</div>
              <div class="d">{{ step.detail }}</div>
            </li>
          </ul>
        </div>

        <!-- Hold Expiry Warning -->
        <div class="note note-warn">
          <strong>Hold expires at {{ reservation.holdExpiresAt }}.</strong> If the reservation is not collected within the pickup window it is released and the items go back on sale. The down payment is forfeited — this is the same rule as a market vendor holding stock for a regular customer.
        </div>

        <!-- Actions -->
        <div class="row-wrap no-print" style="--gap: 12px">
          <button class="btn btn-primary" type="button" @click="printReservation">🖨️ Print this reservation</button>
          <a class="btn" href="/order-tracking">Track this order</a>
          <a class="btn" href="/market-map">Show stall {{ reservation.vendor.stall_location }} on the map</a>
          <a class="btn btn-ghost" href="/catalog">Back to marketplace</a>
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
.mb0 { margin-bottom: 0; }
.mb8 { margin-bottom: 8px; }
.mt8 { margin-top: 8px; }
.mt12 { margin-top: 12px; }
.mb12 { margin-bottom: 12px; }

.badge-brand { background: var(--brand-light); color: var(--brand-dark); }
.badge-ok { background: var(--ok-bg); color: var(--ok); }
.badge-warn { background: var(--warn-bg); color: var(--warn); }
.badge-info { background: var(--info-bg); color: var(--info); }
.badge-danger { background: var(--danger-bg); color: var(--danger); }

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

.table-wrap { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.table th, .table td { padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; }
.table th { font-weight: 600; color: var(--ink-2); background: var(--neutral-bg); }
.table tbody tr:last-child td { border-bottom: none; }

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

.opt { display: flex; align-items: center; gap: 12px; padding: 12px; border: 1px solid var(--line); border-radius: var(--radius-sm); margin-bottom: 8px; cursor: pointer; }
.opt.on { border-color: var(--brand); background: var(--brand-light); }
.opt input { accent-color: var(--brand); }
.opt .t { font-weight: 500; }
.opt .d { font-size: 0.8125rem; color: var(--muted); }

.note { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 0.8125rem; background: var(--info-bg); color: var(--info); border-left: 4px solid var(--info); }
.note-warn { background: var(--warn-bg); color: var(--warn); border-left-color: var(--warn); }
.note.tiny { font-size: 0.75rem; }

.divider { border: none; border-top: 1px solid var(--line); margin: 16px 0; }

.no-print { display: flex; }
@media print { .no-print { display: none !important; } }

@media (max-width: 860px) {
  .kv { grid-template-columns: 120px 1fr; }
  .row-between { flex-direction: column; align-items: flex-start; }
  .no-print { flex-direction: column; }
  .no-print .btn { width: 100%; }
}

@media (max-width: 520px) {
  .kv { grid-template-columns: 1fr; gap: 4px; }
  .kv dt { margin-bottom: 2px; }
}
</style>