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
const posData = ref(null)

// Current sale state
const currentSaleItems = ref([
  { id: 1, product: { name: 'Bangus (Milkfish)', emoji: '🐟', onHand: 12 }, qty: 1, price: '180.00', subtotal: '180.00' },
  { id: 2, product: { name: 'Galunggong (Round Scad)', emoji: '🐟', onHand: 17 }, qty: 1, price: '160.00', subtotal: '160.00' }
])
const searchQuery = ref('')
const cashTendered = ref('500.00')
const quickCashAmount = ref('1000')

// Mock data - in production this would come from API endpoints
const mockPosData = {
  vendorName: "Pedro's Fresh Catch",
  stall: 'Stall A-12',
  section: 'Section A – Fish',
  counterQueue: [
    { ref: 'ECO-20261116-0009', status: 'READY_FOR_PICKUP', statusClass: 'badge-accent', buyer: 'Ana Lim', items: 'Bangus 1 kg · ₱180.00', balanceDue: '90.00', paidOnline: '₱180.00', actionLabel: 'Collect balance', actionClass: 'btn-accent', action: 'collect' },
    { ref: 'ECO-20261116-0007', status: 'CONFIRMED', statusClass: 'badge-brand', buyer: 'Maria Santos', items: 'Bangus 2 kg, Galunggong 1 kg', balanceDue: '', paidOnline: 'Paid online · ₱520.00', actionLabel: 'Start preparing', actionClass: '', action: 'prepare' },
    { ref: 'ECO-20261116-0008', status: 'PREPARING', statusClass: 'badge-info', buyer: 'Juan Dela Cruz', items: 'Tilapia 3 kg', balanceDue: '', paidOnline: 'For Lalamove · SBX-LM-80934', actionLabel: 'Release to rider', actionClass: '', action: 'release' },
    { ref: 'ECO-20261116-0006', status: 'COMPLETED', statusClass: 'badge-ok', buyer: 'Rico Bautista', items: 'Walk-in · 3 items', balanceDue: '', paidOnline: '₱620.00 · cash', actionLabel: 'Reprint receipt', actionClass: '', action: 'reprint', isCompleted: true }
  ],
  availableProducts: [
    { id: 1, name: 'Bangus (Milkfish)', emoji: '🐟', onHand: 12, price: '180.00', unit: 'kg' },
    { id: 2, name: 'Galunggong (Round Scad)', emoji: '🐟', onHand: 17, price: '160.00', unit: 'kg' },
    { id: 3, name: 'Tilapia', emoji: '🐟', onHand: 25, price: '140.00', unit: 'kg' },
    { id: 4, name: 'Tulingan (Bullet Tuna)', emoji: '🐟', onHand: 14, price: '190.00', unit: 'kg' },
    { id: 5, name: 'Hipon (Shrimp)', emoji: '🦐', onHand: 6, price: '380.00', unit: 'kg' },
    { id: 6, name: 'Dried Fish (Tuyo)', emoji: '🐟', onHand: 5, price: '420.00', unit: 'kg' }
  ]
}

const subtotal = computed(() => {
  return currentSaleItems.value.reduce((sum, item) => sum + Number(item.subtotal), 0)
})

const totalDue = computed(() => subtotal.value) // walk-in has no delivery fee

const changeDue = computed(() => {
  const tendered = Number(cashTendered.value) || 0
  return Math.max(0, tendered - totalDue.value)
})

const itemCount = computed(() => currentSaleItems.value.length)

async function fetchPOSData() {
  try {
    // In production: await api.get('/vendor/pos/')
    posData.value = mockPosData
  } catch (e) {
    error.value = 'Failed to load POS data'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount) {
  return `₱${Number(amount).toFixed(2)}`
}

// Counter queue actions
function handleQueueAction(queueItem) {
  switch (queueItem.action) {
    case 'collect':
      router.push('/vendor/orders')
      break
    case 'prepare':
      alert(`Mark ${queueItem.ref} as PREPARING`)
      break
    case 'release':
      alert(`Mark ${queueItem.ref} as OUT_FOR_DELIVERY`)
      break
    case 'reprint':
      alert(`Reprint receipt for ${queueItem.ref}`)
      break
  }
}

// Current sale actions
function addProduct(product) {
  const existing = currentSaleItems.value.find(item => item.id === product.id)
  if (existing) {
    existing.qty += 1
    existing.subtotal = (existing.qty * Number(existing.price)).toFixed(2)
  } else {
    currentSaleItems.value.push({
      id: product.id,
      product: { name: product.name, emoji: product.emoji, onHand: product.onHand },
      qty: 1,
      price: product.price,
      subtotal: product.price
    })
  }
}

function removeItem(itemId) {
  currentSaleItems.value = currentSaleItems.value.filter(item => item.id !== itemId)
}

function updateQty(item, delta) {
  const newQty = item.qty + delta
  if (newQty <= 0) {
    removeItem(item.id)
  } else if (newQty <= item.product.onHand) {
    item.qty = newQty
    item.subtotal = (newQty * Number(item.price)).toFixed(2)
  }
}

function setQuickCash(amount) {
  quickCashAmount.value = amount
  cashTendered.value = amount.toFixed(2)
}

function completeSale() {
  if (currentSaleItems.value.length === 0) {
    alert('No items in sale')
    return
  }
  if (Number(cashTendered.value) < totalDue.value) {
    alert('Insufficient cash tendered')
    return
  }

  // In production: POST /vendor/pos/complete-sale/ with items and cash tendered
  const receiptSerial = `RC-ECO-20261116-0010-${Math.floor(Math.random() * 10) + 1}`
  alert(`Sale completed!\nReceipt: ${receiptSerial}\nChange: ${formatCurrency(changeDue.value)}`)

  // Clear current sale
  currentSaleItems.value = []
  cashTendered.value = '0.00'
}

function printReceipt() {
  window.print()
}

// Search products
function searchProducts() {
  // In production: filter availableProducts or call API
  console.log('Search:', searchQuery.value)
}

onMounted(() => {
  fetchPOSData()
})
</script>

<template>
  <div class="page">
    <div class="wrap stack">
      <!-- Page Header -->
      <div class="pagehead">
        <div class="eyebrow">Point of sale</div>
        <h1>Counter terminal</h1>
        <p>For buyers standing at {{ posData?.stall || 'Stall A-12' }}. A walk-in sale is created and closed in one motion — the order, the payment and the stock movement all happen together.</p>
      </div>

      <!-- Loading/Error -->
      <div v-if="loading" class="card center" style="padding: 48px; grid-column: 1 / -1;">
        <div class="spinner"></div>
        <p class="muted mt12">Loading POS terminal...</p>
      </div>

      <div v-else-if="error" class="card center" style="padding: 48px; border-color: var(--danger); grid-column: 1 / -1;">
        <p class="muted">{{ error }}</p>
        <button class="btn btn-primary mt12" @click="fetchPOSData">Retry</button>
      </div>

      <div v-else>
        <!-- ===== Counter Queue ===== -->
        <section class="card">
          <div class="card-head">
            <h3 class="mb0">Counter queue</h3>
            <span class="small muted">reservations and orders to hand over</span>
          </div>
          <div class="grid grid-4">
            <div class="card card-tight" style="box-shadow: none" v-for="item in posData.counterQueue" :key="item.ref" :class="{ 'is-completed': item.isCompleted }" :style="{ background: item.isCompleted ? 'var(--ok-bg)' : '', borderColor: item.isCompleted ? 'var(--ok)' : '' }">
              <div class="row-between mb8">
                <span class="mono small">{{ item.ref }}</span>
                <span class="badge" :class="item.statusClass">{{ item.status }}</span>
              </div>
              <div class="small" style="font-weight: 650">{{ item.buyer }}</div>
              <div class="tiny muted">{{ item.items }}</div>
              <div class="tiny muted mb8" v-if="item.balanceDue">Balance due <strong>{{ formatCurrency(item.balanceDue) }}</strong></div>
              <div class="tiny muted mb8" v-else>{{ item.paidOnline }}</div>
              <button class="btn btn-sm btn-block" :class="item.actionClass" type="button" @click="handleQueueAction(item)">{{ item.actionLabel }}</button>
            </div>
          </div>
          <div class="card-foot tiny muted">
            The queue mixes all three channels on purpose: <span class="mono">POS_WALKIN</span> sales you ring up,
            <span class="mono">ONLINE_ORDER</span> orders to prepare, and <span class="mono">PICKUP_RESERVATION</span>
            balances to collect. One counter, one screen.
          </div>
        </section>

        <!-- ===== The Till ===== -->
        <div class="grid-side" style="grid-template-columns: 1fr 380px">
          <section class="card">
            <div class="card-head">
              <div>
                <h3 class="mb0">Current sale</h3>
                <span class="small muted">Walk-in customer · <span class="mono">POS_WALKIN</span></span>
              </div>
              <span class="badge">OPEN</span>
            </div>

            <div class="searchbar mb12">
              <input class="input" type="search" placeholder="Scan or type a product…" aria-label="Add product" v-model="searchQuery" @keyup.enter="searchProducts">
              <button class="btn" type="button" @click="searchProducts">Add</button>
            </div>

            <div class="table-wrap">
              <table class="table">
                <thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Price</th><th class="num">Subtotal</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="item in currentSaleItems" :key="item.id">
                    <td>
                      <strong>{{ item.product.emoji }} {{ item.product.name }}</strong>
                      <div class="tiny muted">{{ item.product.onHand }} {{ item.product.unit || 'kg' }} on hand</div>
                    </td>
                    <td class="num">
                      <div class="row" style="justify-content: flex-end; gap: 4px;">
                        <button class="btn btn-sm" type="button" @click="updateQty(item, -1)">−</button>
                        <span style="min-width: 2rem; text-align: center; font-variant-numeric: tabular-nums;">{{ item.qty }}</span>
                        <button class="btn btn-sm" type="button" @click="updateQty(item, 1)">+</button>
                      </div>
                    </td>
                    <td class="num">{{ formatCurrency(item.price) }}</td>
                    <td class="num"><strong>{{ formatCurrency(item.subtotal) }}</strong></td>
                    <td class="num"><button class="btn btn-sm btn-danger" type="button" @click="removeItem(item.id)">✕</button></td>
                  </tr>
                  <tr v-if="!currentSaleItems.length">
                    <td colspan="5" class="center muted" style="padding: 24px;">No items in sale. Search or scan a product to begin.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <hr class="divider">

            <div class="row-between mb8"><span class="small muted">Items</span><span>{{ itemCount }}</span></div>
            <div class="row-between mb8"><span class="small muted">Subtotal</span><span>{{ formatCurrency(subtotal) }}</span></div>
            <div class="row-between mb8"><span class="small muted">Delivery fee</span><span class="muted">₱0.00 — walk-in</span></div>
            <div class="row-between">
              <span style="font-weight: 650; font-size: 1.02rem">Total due</span>
              <span class="price price-lg">{{ formatCurrency(totalDue) }}</span>
            </div>

            <div class="note mt16 tiny">
              <strong>Stock moves on checkout, not on add.</strong> Both items leave the ledger when you press
              <em>Complete sale</em>. Abandoning this sale changes nothing.
            </div>
          </section>

          <!-- Cash Panel -->
          <aside class="stack">
            <div class="card" style="border-color: var(--accent)">
              <div class="card-head"><h3>💵 Cash payment</h3><span class="badge badge-accent">CASH</span></div>

              <div class="row-between mb12">
                <span class="small muted">Amount due</span>
                <span class="price price-lg">{{ formatCurrency(totalDue) }}</span>
              </div>

              <div class="field">
                <span>Cash tendered (₱)</span>
                <input class="input" type="text" v-model="cashTendered" aria-label="Cash tendered">
              </div>

              <div class="chips mb12">
                <button class="chip" type="button" @click="setQuickCash(totalDue)">₱{{ totalDue.toFixed(0) }}</button>
                <button class="chip" type="button" @click="setQuickCash(500)">₱500</button>
                <button class="chip" :class="{ on: quickCashAmount === 1000 }" type="button" @click="setQuickCash(1000)">₱1,000</button>
              </div>

              <div class="card card-tight" style="box-shadow: none; background: var(--accent-light); border-color: var(--accent)">
                <div class="row-between">
                  <span style="font-weight: 650">Change due</span>
                  <span class="price price-lg">{{ formatCurrency(changeDue) }}</span>
                </div>
                <div class="tiny muted mt8">₱{{ Number(cashTendered).toFixed(2) }} tendered − {{ formatCurrency(totalDue) }} due</div>
              </div>

              <div class="card-foot">
                <button class="btn btn-accent btn-block btn-lg" type="button" @click="completeSale">Complete sale & print receipt</button>
              </div>
            </div>

            <div class="card">
              <div class="card-head"><h3>What gets written</h3></div>
              <div class="stack" style="--gap: 10px">
                <div class="row small">
                  <span class="badge badge-brand">1</span>
                  <span><span class="mono">Order</span> — one row, <span class="mono">POS_WALKIN</span>, straight to <span class="mono">COMPLETED</span></span>
                </div>
                <div class="row small">
                  <span class="badge badge-brand">2</span>
                  <span><span class="mono">OrderItem</span> × {{ itemCount || 2 }} — price snapshotted at today's prices</span>
                </div>
                <div class="row small">
                  <span class="badge badge-brand">3</span>
                  <span><span class="mono">Payment</span> — provider <span class="mono">CASH</span>, status <span class="mono">VERIFIED</span></span>
                </div>
                <div class="row small">
                  <span class="badge badge-brand">4</span>
                  <span><span class="mono">InventoryMovement</span> × {{ itemCount || 2 }} — reason <span class="mono">SOLD_WALKIN</span></span>
                </div>
              </div>
              <div class="card-foot">
                <div class="note note-accent tiny mb0">
                  All four writes sit inside a single <span class="mono">transaction.atomic()</span> block. If the receipt
                  printer jams, nothing is committed and the sale stays open.
                </div>
              </div>
            </div>
          </aside>
        </div>

        <!-- ===== Receipt Preview ===== -->
        <section class="card">
          <div class="card-head">
            <h3 class="mb0">Receipt preview</h3>
            <span class="small muted">72 mm thermal · BIR-style layout</span>
          </div>

          <div class="grid-side" style="grid-template-columns: 1fr 1fr">
            <div>
              <div class="receipt">
                <div class="c b">E-COMPRA</div>
                <div class="c sm">Mandaue Public Market</div>
                <div class="c sm">A.C. Cortes Ave., Mandaue City, Cebu</div>
                <div class="c sm">Vendor: {{ posData?.vendorName?.toUpperCase() || "PEDRO'S FRESH CATCH" }}</div>
                <div class="c sm">{{ posData?.stall || 'Stall A-12' }} · {{ posData?.section || 'Section A – Fish' }}</div>
                <div class="c sm">TIN 123-456-789-000</div>
                <hr>
                <div class="line sm"><span>OR No.</span><span>RC-ECO-20261116-0010-1</span></div>
                <div class="line sm"><span>Date</span><span>16 Nov 2026 11:58 AM</span></div>
                <div class="line sm"><span>Order</span><span>ECO-20261116-0010</span></div>
                <div class="line sm"><span>Type</span><span>POS_WALKIN</span></div>
                <hr>
                <div class="line" v-for="item in currentSaleItems" :key="item.id">
                  <span>{{ item.product.name }}</span>
                  <span>{{ formatCurrency(item.subtotal) }}</span>
                </div>
                <div class="line sm" v-for="item in currentSaleItems" :key="item.id + '-detail'">
                  <span>&nbsp;&nbsp;{{ item.qty }} {{ item.product.unit || 'kg' }} @ {{ formatCurrency(item.price) }}</span>
                  <span></span>
                </div>
                <hr>
                <div class="line"><span>Subtotal</span><span>{{ formatCurrency(subtotal) }}</span></div>
                <div class="line sm"><span>Delivery fee</span><span>0.00</span></div>
                <div class="tot"><span>TOTAL</span><span>PHP {{ totalDue.toFixed(2) }}</span></div>
                <hr>
                <div class="line"><span>Cash</span><span>{{ formatCurrency(Number(cashTendered) || 0) }}</span></div>
                <div class="line"><span>Change</span><span>{{ formatCurrency(changeDue) }}</span></div>
                <div class="line sm"><span>Payment</span><span>CASH · VERIFIED</span></div>
                <hr>
                <div class="line sm"><span>VATable sales</span><span>{{ formatCurrency(totalDue / 1.12) }}</span></div>
                <div class="line sm"><span>VAT (12%)</span><span>{{ formatCurrency(totalDue - totalDue / 1.12) }}</span></div>
                <div class="line sm"><span>VAT-exempt</span><span>0.00</span></div>
                <hr>
                <div class="c sm">Items: {{ itemCount }} &nbsp;|&nbsp; Qty: {{ currentSaleItems.reduce((sum, i) => sum + i.qty, 0) }} kg</div>
                <div class="c sm">Served by: P. REYES</div>
                <div class="c sm">Thank you — palit na mo!</div>
                <div class="c sm">This serves as your official receipt.</div>
                <div class="c sm">Receipt attempt 1 of this order</div>
              </div>
              <div class="row mt12 no-print">
                <button class="btn btn-primary" type="button" @click="printReceipt">🖨 Print 72 mm</button>
                <button class="btn" type="button" @click="completeSale">Close sale</button>
              </div>
            </div>

            <div class="stack">
              <div class="note tiny">
                <strong>Serial format.</strong> <span class="mono">receipt_serial = RC-{reference_no}-{receipt_attempt}</span>.
                The order reference is <span class="mono">ECO-20261116-0010</span> and this is attempt 1, so the serial is
                <span class="mono">RC-ECO-20261116-0010-1</span>.
              </div>

              <div class="card card-tight">
                <div class="card-head" style="margin-bottom: 8px"><h4 class="mb0">Reprinting does not mint a new serial</h4></div>
                <div class="table-wrap">
                  <table class="table">
                    <thead><tr><th>Attempt</th><th>Serial</th><th>Printed at</th><th>Why</th></tr></thead>
                    <tbody>
                      <tr>
                        <td>1</td>
                        <td class="mono tiny">RC-ECO-20261116-0010-1</td>
                        <td class="small">11:58 AM</td>
                        <td class="small muted">Original</td>
                      </tr>
                      <tr>
                        <td>2</td>
                        <td class="mono tiny">RC-ECO-20261116-0010-2</td>
                        <td class="small">12:04 PM</td>
                        <td class="small muted">Buyer asked for a copy</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="tiny muted mt8">
                  A receipt is never re-issued under the same number. The attempt counter keeps every copy traceable, so
                  two pieces of paper can never claim to be the same receipt.
                </div>
              </div>

              <div class="note note-warn tiny">
                <strong>Cash is a payment event, not a status transition.</strong> Completing this sale records a
                <span class="mono">Payment</span> with provider <span class="mono">CASH</span> and status
                <span class="mono">VERIFIED</span>. It does not push the order through
                <span class="mono">CONFIRMED → PREPARING → …</span> — a walk-in order is created already
                <span class="mono">COMPLETED</span>, because goods and money move at the same moment.
              </div>

              <div class="note tiny">
                <strong>Printing.</strong> The browser's own print dialog does the work, scoped by
                <span class="mono">@media print</span> to a 72 mm page. No printer driver or ESC/POS library is needed for
                the prototype.
              </div>
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
.row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.mb12 { margin-bottom: 12px; }
.mt12 { margin-top: 12px; }
.mt8 { margin-top: 8px; }
.mt16 { margin-top: 16px; }
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
.grid-side { grid-template-columns: 1fr 380px; }

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

.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 12px; border-radius: var(--radius-pill); border: 1px solid var(--brand-line); background: var(--card); color: var(--ink); text-decoration: none; font-size: 0.8125rem; transition: all 0.15s; }
.chip:hover { border-color: var(--brand); color: var(--brand); }
.chip.on { background: var(--brand); border-color: var(--brand); color: white; }

.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.field span { font-size: 0.8125rem; font-weight: 500; color: var(--ink-2); }
.field .input { padding: 8px 12px; border: 1px solid var(--line); border-radius: var(--radius-sm); font-size: 0.875rem; background: var(--card); }
.field .input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 2px var(--brand-light); }

.searchbar { display: flex; gap: 8px; }
.searchbar .input { flex: 1; }

/* Receipt styles for 72mm thermal */
.receipt {
  width: 200px; /* ~72mm at 96dpi */
  font-family: var(--font-mono);
  font-size: 0.7rem;
  line-height: 1.3;
  background: white;
  padding: 12px;
  border: 1px dashed var(--brand-line);
  border-radius: var(--radius-sm);
}
.receipt .c { text-align: center; }
.receipt .b { font-weight: 700; font-size: 0.875rem; }
.receipt .sm { font-size: 0.625rem; }
.receipt hr { border: none; border-top: 1px dashed var(--brand-line); margin: 8px 0; }
.receipt .line { display: flex; justify-content: space-between; }
.receipt .line.sm { font-size: 0.625rem; }
.receipt .tot { font-weight: 700; font-size: 0.875rem; border-top: 1px dashed var(--brand-line); padding-top: 4px; margin-top: 4px; }

.no-print { display: inline-flex; }
@media print { .no-print { display: none !important; } }

@media (max-width: 860px) {
  .grid-side { grid-template-columns: 1fr; }
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
  .stat .v { font-size: 1.25rem; }
}

@media (max-width: 520px) {
  .grid-4 { grid-template-columns: 1fr; }
  .kv { grid-template-columns: 1fr; gap: 4px; }
  .kv dt { margin-bottom: 2px; }
  .chips { gap: 6px; }
  .chip { padding: 4px 10px; font-size: 0.75rem; }
  .table th, .table td { padding: 8px; font-size: 0.8125rem; }
  .receipt { width: 100%; max-width: 200px; }
}
</style>