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
const ordersData = ref(null)
const activeFilter = ref('Active')

// Mock data - in production this would come from API endpoints
const mockOrdersData = {
  stats: {
    awaitingAction: 3,
    readyForPickup: 1,
    completedToday: 3,
    completedTodayAmount: '1300.00',
    cashToCollect: '90.00',
    cashToCollectCount: 1
  },
  orders: [
    {
      ref: 'ECO-20261116-0007',
      buyer: 'Maria Santos',
      placed: '16 Nov 2026, 8:05 AM',
      channel: 'ONLINE_ORDER',
      fulfillment: 'PICKUP',
      status: 'CONFIRMED',
      statusClass: 'badge-brand',
      items: [
        { name: 'Bangus (Milkfish)', emoji: '🐟', qty: '2 kg', price: '180.00', subtotal: '360.00' },
        { name: 'Galunggong (Round Scad)', emoji: '🐟', qty: '1 kg', price: '160.00', subtotal: '160.00' }
      ],
      paymentRef: 'SBX-PM-20261116-B7E21D90',
      total: '520.00',
      paymentStatus: 'VERIFIED',
      nextStep: 'PREPARING',
      nextStepLabel: 'Mark as PREPARING',
      nextStepClass: 'btn-primary',
      canCancel: true,
      canPrintPickList: true,
      note: 'Payment is already VERIFIED, so the order reached CONFIRMED on its own. Nothing to collect at the counter.'
    },
    {
      ref: 'ECO-20261116-0008',
      buyer: 'Juan Dela Cruz',
      placed: '16 Nov 2026, 9:40 AM',
      channel: 'ONLINE_ORDER',
      fulfillment: 'DELIVERY',
      status: 'PREPARING',
      statusClass: 'badge-info',
      borderColor: 'info',
      items: [
        { name: 'Tilapia', emoji: '🐟', qty: '3 kg', price: '140.00', subtotal: '420.00' },
        { name: 'Delivery fee — Lalamove', emoji: '🛵', qty: '', price: '', subtotal: '95.00', isDelivery: true }
      ],
      paymentRef: 'SBX-PM-20261116-C3A77E15',
      total: '515.00',
      paymentStatus: 'VERIFIED',
      deliveryBooking: {
        provider: 'Lalamove',
        bookingRef: 'SBX-LM-80934',
        fee: '95.00',
        status: 'BOOKED',
        customer: 'Juan Dela Cruz',
        address: '12 Plaridel St., Mandaue City',
        phone: '0917-555-0142'
      },
      nextStep: 'OUT_FOR_DELIVERY',
      nextStepLabel: 'Mark as OUT_FOR_DELIVERY',
      nextStepClass: 'btn-primary',
      canCancel: false,
      canPrintPickList: true,
      canRebookCourier: true,
      note: 'Hand the packed order to the rider, then mark it OUT_FOR_DELIVERY. The courier\'s own status stays on the booking — it does not overwrite the order status.',
      skipReadyForPickup: true
    },
    {
      ref: 'ECO-20261116-0009',
      buyer: 'Ana Lim',
      placed: '16 Nov 2026, 6:15 AM',
      channel: 'PICKUP_RESERVATION',
      fulfillment: 'PICKUP',
      status: 'READY_FOR_PICKUP',
      statusClass: 'badge-accent',
      borderColor: 'accent',
      items: [
        { name: 'Bangus (Milkfish)', emoji: '🐟', qty: '1 kg', price: '180.00', subtotal: '180.00' }
      ],
      paymentRef: 'SBX-PM-20261116-D91B4C33',
      downPayment: '90.00',
      balanceDue: '90.00',
      total: '180.00',
      paymentStatus: 'VERIFIED',
      holdExpiry: '6:00 PM today',
      nextStep: 'COMPLETED',
      nextStepLabel: 'Collect ₱90.00 & complete',
      nextStepClass: 'btn-accent',
      canCancel: false,
      canPrintPickList: false,
      canNotifyBuyer: true,
      canOpenPOS: true,
      note: 'The buyer holds this reservation until 6:00 PM today. Collect ₱90.00 in cash, record it at the POS, and only then mark the order COMPLETED.'
    }
  ],
  completedOrders: [
    { ref: 'ECO-20261116-0006', buyer: 'Rico Bautista', channel: 'WALK_IN', items: 3, total: '620.00', payment: 'CASH', paymentClass: 'badge-ok', closed: '11:52 AM' },
    { ref: 'ECO-20261116-0005', buyer: 'Liza Tan', channel: 'WALK_IN', items: 2, total: '340.00', payment: 'CASH', paymentClass: 'badge-ok', closed: '10:18 AM' },
    { ref: 'ECO-20261116-0004', buyer: 'Mark Villanueva', channel: 'WALK_IN', items: 2, total: '340.00', payment: 'CASH', paymentClass: 'badge-ok', closed: '9:05 AM' },
    { ref: 'ECO-20261116-0003', buyer: 'Maria Santos', channel: 'ONLINE', items: 2, total: '520.00', payment: 'E-WALLET', paymentClass: 'badge-info', closed: 'Yesterday' }
  ]
}

const filters = [
  { key: 'Active', label: 'Active (3)' },
  { key: 'Pickup', label: 'Pickup' },
  { key: 'Delivery', label: 'Delivery' },
  { key: 'Completed', label: 'Completed' },
  { key: 'Cancelled', label: 'Cancelled' }
]

async function fetchOrders() {
  try {
    // In production: await api.get('/vendor/orders/')
    ordersData.value = mockOrdersData
  } catch (e) {
    error.value = 'Failed to load orders'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function setFilter(filterKey) {
  activeFilter.value = filterKey
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

function getChannelBadgeClass(channel) {
  const classes = {
    'WALK_IN': 'badge-warn',
    'ONLINE_ORDER': 'badge-info',
    'ONLINE': 'badge-info',
    'PICKUP_RESERVATION': 'badge-accent'
  }
  return classes[channel] || 'badge'
}

function handleNextStep(order) {
  // In production: call vendor POS API to transition status
  const nextStatus = order.nextStep
  alert(`Transition order ${order.ref} to ${nextStatus}`)
}

function handleCancel(order) {
  if (confirm(`Cancel order ${order.ref}? This will return items to the ledger and refund the payment.`)) {
    alert(`Order ${order.ref} cancelled`)
  }
}

function handlePrintPickList(order) {
  alert(`Print pick list for ${order.ref}`)
}

function handleRebookCourier(order) {
  alert(`Rebook courier for ${order.ref}`)
}

function handleNotifyBuyer(order) {
  alert(`Notify buyer for ${order.ref}`)
}

function handleOpenPOS(order) {
  router.push('/vendor/pos')
}

function handleCollectBalance(order) {
  router.push('/vendor/pos')
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Vendor console</div>
        <h1>Order queue</h1>
        <p>Every order a buyer placed with your stall. Move each one along the lifecycle — the buttons below are the only legal transitions from where the order currently sits.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading orders...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchOrders">Retry</button>
      </div>

      <div v-else>
        <!-- Stats -->
        <div class="grid grid-4">
          <div class="stat"><div class="k">Awaiting action</div><div class="v">{{ ordersData.stats.awaitingAction }}</div><div class="sub">needs you today</div></div>
          <div class="stat"><div class="k">Ready for pickup</div><div class="v" style="color: var(--accent-dark)">{{ ordersData.stats.readyForPickup }}</div><div class="sub">buyer notified</div></div>
          <div class="stat"><div class="k">Completed today</div><div class="v">{{ ordersData.stats.completedToday }}</div><div class="sub">{{ formatCurrency(ordersData.stats.completedTodayAmount) }}</div></div>
          <div class="stat"><div class="k">Cash still to collect</div><div class="v" style="color: var(--accent-dark)">{{ formatCurrency(ordersData.stats.cashToCollect) }}</div><div class="sub">{{ ordersData.stats.cashToCollectCount }} reservation balance</div></div>
        </div>

        <!-- Filter Chips -->
        <div class="chips">
          <a v-for="filter in filters" :key="filter.key" class="chip" :class="{ on: activeFilter === filter.key }" @click.prevent="setFilter(filter.key)">{{ filter.label }}</a>
        </div>

        <!-- Orders -->
        <section class="card" v-for="order in ordersData.orders" :key="order.ref" :style="{ borderColor: order.borderColor ? 'var(--' + order.borderColor + ')' : '' }">
          <div class="card-head">
            <div>
              <h3 class="mb0">{{ order.ref }} · {{ order.buyer }}</h3>
              <span class="small muted">Placed {{ order.placed }} · <span class="mono">{{ order.channel }}</span> · <span class="mono">{{ order.fulfillment }}</span></span>
            </div>
            <span class="badge" :class="order.statusClass">{{ order.status }}</span>
          </div>

          <div class="grid-side" style="grid-template-columns: 1fr 300px">
            <div>
              <div class="table-wrap">
                <table class="table">
                  <thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Subtotal</th></tr></thead>
                  <tbody>
                    <tr v-for="(item, index) in order.items" :key="index">
                      <td>
                        <strong v-if="!item.isDelivery">{{ item.emoji }} {{ item.name }}</strong>
                        <span v-else class="muted">{{ item.emoji }} {{ item.name }}</span>
                      </td>
                      <td class="num">{{ item.qty }} × {{ formatCurrency(item.price) }}</td>
                      <td class="num">{{ formatCurrency(item.subtotal) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="row-between mt12">
                <span class="small muted">Paid online — <span class="mono">{{ order.paymentRef }}</span></span>
                <span class="price price-lg">{{ formatCurrency(order.total) }}</span>
              </div>

              <!-- Delivery booking card for delivery orders -->
              <div class="card card-tight mt12" v-if="order.deliveryBooking" style="box-shadow: none">
                <div class="row-between">
                  <div>
                    <div class="small" style="font-weight: 650">🛵 Delivery booking</div>
                    <div class="tiny muted">{{ order.deliveryBooking.provider }} · <span class="mono">{{ order.deliveryBooking.bookingRef }}</span> · {{ formatCurrency(order.deliveryBooking.fee) }}</div>
                  </div>
                  <span class="badge badge-warn">{{ order.deliveryBooking.status }}</span>
                </div>
                <hr class="divider">
                <div class="small muted">Drop off to <strong>{{ order.deliveryBooking.customer }}</strong>, {{ order.deliveryBooking.address }}</div>
                <div class="tiny muted">📞 {{ order.deliveryBooking.phone }}</div>
              </div>

              <!-- Balance due for pickup reservations -->
              <div class="mt12" v-if="order.balanceDue !== undefined">
                <div class="row-between mb8">
                  <span class="small muted">Total</span><span>{{ formatCurrency(order.total) }}</span>
                </div>
                <div class="row-between mb8">
                  <span class="small muted">Down payment — <span class="mono">{{ order.paymentRef }}</span></span>
                  <span style="color: var(--ok); font-weight: 650">− {{ formatCurrency(order.downPayment) }}</span>
                </div>
                <div class="row-between">
                  <span style="font-weight: 650">Balance due at the stall</span>
                  <span class="price price-lg">{{ formatCurrency(order.balanceDue) }}</span>
                </div>
              </div>

              <div class="note mt12 tiny" :class="order.balanceDue !== undefined ? 'note-warn' : ''">
                {{ order.note }}
                <span v-if="order.skipReadyForPickup" class="note-accent tiny mt8" style="display: block">Delivery orders skip <span class="mono">READY_FOR_PICKUP</span> entirely — that state belongs to the pickup flow.</span>
              </div>
            </div>

            <!-- Sidebar with actions -->
            <aside>
              <div class="card card-tight" :style="{ boxShadow: 'none', background: order.status === 'CONFIRMED' ? 'var(--brand-light)' : order.status === 'PREPARING' ? 'var(--info-bg)' : order.status === 'READY_FOR_PICKUP' ? 'var(--accent-light)' : '' }">
                <div class="small" style="font-weight: 650">Next step</div>
                <div class="tiny muted mb8">{{ order.nextStep === 'PREPARING' ? 'Start preparing this order for collection.' : order.nextStep === 'OUT_FOR_DELIVERY' ? 'Fish is cleaned and packed. Release it to the courier.' : 'Buyer arrives, pays the balance in cash, takes the fish.' }}</div>
                <button class="btn btn-block" :class="order.nextStepClass" type="button" @click="handleNextStep(order)">{{ order.nextStepLabel }}</button>
              </div>
              <div class="row-wrap mt12">
                <button v-if="order.canPrintPickList" class="btn btn-sm" type="button" @click="handlePrintPickList(order)">Print pick list</button>
                <button v-if="order.canRebookCourier" class="btn btn-sm" type="button" @click="handleRebookCourier(order)">Rebook courier</button>
                <button v-if="order.canCancel" class="btn btn-sm btn-danger" type="button" @click="handleCancel(order)">Cancel order</button>
                <a v-if="order.canOpenPOS" class="btn btn-sm" href="/vendor/pos" @click="handleOpenPOS(order)">Open POS</a>
                <button v-if="order.canNotifyBuyer" class="btn btn-sm" type="button" @click="handleNotifyBuyer(order)">Notify buyer</button>
              </div>
              <div class="tiny muted mt8" v-if="order.balanceDue !== undefined">
                Taking the cash records a <span class="mono">Payment</span> row — it does not by itself complete the order.
              </div>
              <div class="tiny muted mt8" v-if="order.canCancel">
                Cancelling returns both items to the ledger and refunds the payment.
              </div>
            </aside>
          </div>
        </section>

        <!-- Recently Completed -->
        <section class="card">
          <div class="card-head">
            <h3 class="mb0">Recently completed</h3>
            <span class="small muted">today</span>
          </div>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr><th>Reference</th><th>Buyer</th><th>Channel</th><th class="num">Items</th><th class="num">Total</th><th>Payment</th><th>Closed</th></tr>
              </thead>
              <tbody>
                <tr v-for="order in ordersData.completedOrders" :key="order.ref">
                  <td class="mono">{{ order.ref }}</td>
                  <td>{{ order.buyer }}</td>
                  <td><span class="badge" :class="getChannelBadgeClass(order.channel)">{{ order.channel }}</span></td>
                  <td class="num">{{ order.items }}</td>
                  <td class="num">{{ formatCurrency(order.total) }}</td>
                  <td><span class="badge" :class="order.paymentClass">{{ order.payment }}</span></td>
                  <td class="small">{{ order.closed }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-foot tiny muted">
            Cash sales appear here as <span class="mono">COMPLETED</span> the moment the POS closes them, because the money
            and the goods change hands at the same instant.
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
.mt8 { margin-top: 8px; }
.mb8 { margin-bottom: 8px; }

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
.grid-side { grid-template-columns: 1fr 300px; }

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
.btn-danger { background: var(--danger); border-color: var(--danger); color: white; }
.btn-danger:hover { background: #991111; border-color: #991111; }

.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 12px; border-radius: var(--radius-pill); border: 1px solid var(--brand-line); background: var(--card); color: var(--ink); text-decoration: none; font-size: 0.8125rem; transition: all 0.15s; }
.chip:hover { border-color: var(--brand); color: var(--brand); }
.chip.on { background: var(--brand); border-color: var(--brand); color: white; }

@media (max-width: 860px) {
  .grid-side { grid-template-columns: 1fr; }
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .stat .v { font-size: 1.25rem; }
}

@media (max-width: 520px) {
  .table th, .table td { padding: 8px; font-size: 0.8125rem; }
  .chips { gap: 6px; }
  .chip { padding: 4px 10px; font-size: 0.75rem; }
}
</style>