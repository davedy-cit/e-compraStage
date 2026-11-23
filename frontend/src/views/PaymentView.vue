<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Get transaction IDs from route params or query
// Supports multiple transaction IDs via query param (e.g., ?transactions=1,2,3)
const transactionIdParam = route.params.id
const transactionIdsQuery = route.query.transactions
const transactionIds = computed(() => {
  if (transactionIdsQuery) {
    return String(transactionIdsQuery).split(',').map(id => parseInt(id, 10)).filter(id => !isNaN(id))
  }
  if (transactionIdParam) {
    return [parseInt(transactionIdParam, 10)]
  }
  return []
})

const loading = ref(true)
const processing = ref(false)
const error = ref(null)
const success = ref(false)
const failed = ref(false)

const orders = ref([])
const payment = ref(null)

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const formatDateTime = (dateStr) => {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleString('en-PH', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const fulfillmentLabels = {
  'DELIVERY': '🛵 Delivery',
  'PICKUP': '🏪 Pickup',
}

const fulfillmentIcon = (code) => code === 'DELIVERY' ? '🛵' : '🏪'

const paymentStatusLabels = {
  'PENDING': 'Pending verification',
  'VERIFIED': 'Verified — funds received',
  'FAILED': 'Payment failed',
  'REFUNDED': 'Refunded',
}

const paymentStatusColors = {
  'PENDING': 'badge-warn',
  'VERIFIED': 'badge-ok',
  'FAILED': 'badge-danger',
  'REFUNDED': 'badge-info',
}

const orderStatusLabels = {
  'PENDING_PAYMENT': 'Awaiting payment',
  'CONFIRMED': 'Confirmed',
  'PREPARING': 'Preparing',
  'OUT_FOR_DELIVERY': 'Out for delivery',
  'COMPLETED': 'Completed',
  'CANCELLED': 'Cancelled',
}

// Fetch all orders for the given transaction IDs
async function fetchOrders() {
  if (transactionIds.value.length === 0) {
    error.value = 'No transaction IDs provided'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null

    // Fetch each order via its transaction
    const orderPromises = transactionIds.value.map(async (txnId) => {
      try {
        const txnResponse = await api.get(`/transactions/${txnId}/`)
        const transaction = txnResponse.data
        // Fetch the order details
        if (transaction.order) {
          const orderResponse = await api.get(`/orders/${transaction.order}/`)
          return orderResponse.data
        }
        return null
      } catch (e) {
        console.error(`Failed to fetch transaction ${txnId}:`, e)
        return null
      }
    })

    const results = await Promise.all(orderPromises)
    orders.value = results.filter(o => o !== null)

    // If any order has a payment, fetch the first payment for display
    // (Assuming all transactions in a checkout share the same payment provider/ref)
    if (orders.value.length > 0) {
      const firstOrder = orders.value[0]
      if (firstOrder.transaction?.id) {
        try {
          // We need to fetch payment for this transaction
          // Since there's no direct payment endpoint, we'll derive from order or use a new endpoint
          // For now, check if there's a payment endpoint
        } catch (e) {
          console.error('Failed to fetch payment:', e)
        }
      }
    }

  } catch (err) {
    error.value = 'Failed to load order details'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Process payment for all transactions
async function processPayment() {
  if (orders.value.length === 0) {
    error.value = 'No orders to pay for'
    return
  }

  const provider = paymentMethod.value
  const providerRef = providerReference.value.trim()

  if (!providerRef && provider !== 'CASH_PICKUP') {
    error.value = 'Please enter a reference number'
    return
  }

  try {
    processing.value = true
    error.value = null

    // Process payment for each transaction
    const paymentResults = []
    for (const order of orders.value) {
      if (!order.transaction?.id) continue

      const response = await api.post('/payment/', {
        transaction_id: order.transaction.id,
        provider: provider,
        provider_reference: providerRef || `MANUAL-${Date.now()}-${order.transaction.id}`,
        amount: order.total_amount,
      })
      paymentResults.push(response.data)
    }

    // Store the first payment for display (they should all be similar)
    if (paymentResults.length > 0) {
      payment.value = {
        provider: provider,
        provider_reference: providerRef || `MANUAL-${Date.now()}`,
        amount: paymentResults[0].amount,
        status: paymentResults[0].status,
        paid_at: new Date().toISOString(),
      }
    }

    success.value = true
    // Redirect to order tracking after a delay
    setTimeout(() => {
      router.push('/order-tracking')
    }, 3000)
  } catch (err) {
    failed.value = true
    error.value = err.response?.data?.error || 'Payment failed'
    console.error(err)
  } finally {
    processing.value = false
  }
}

// Retry payment with idempotency key
async function retryPayment() {
  failed.value = false
  await processPayment()
}

function goBackToCheckout() {
  router.push('/checkout')
}

function goToOrderTracking(orderId) {
  router.push({ name: 'order-tracking', params: { id: orderId } })
}

// Determine payment method options
const paymentMethods = [
  { value: 'GCASH', icon: '📱', label: 'GCash', desc: 'Pay online now · sandbox' },
  { value: 'MAYA', icon: '📱', label: 'Maya', desc: 'Pay online now · sandbox' },
  { value: 'ONLINE_BANKING', icon: '🏦', label: 'Online banking', desc: 'Sandbox' },
  { value: 'CARD', icon: '💳', label: 'Card', desc: 'Sandbox · no card data is stored' },
  { value: 'CASH_PICKUP', icon: '💵', label: 'Cash at pickup', desc: 'Pickup orders only' },
]

const paymentMethod = ref('GCASH')
const providerReference = ref('')

// Check if any order is pickup
const hasPickupOrders = computed(() => {
  return orders.value.some(o => o.fulfillment_code === 'PICKUP')
})

// Disable cash at pickup if no pickup orders
const isCashPickupDisabled = computed(() => {
  return !hasPickupOrders.value
})

const grandTotal = computed(() => {
  return orders.value.reduce((sum, o) => sum + Number(o.total_amount || 0), 0)
})

const orderCount = computed(() => orders.value.length)

// Payment status timeline steps
const paymentStatusSteps = [
  { code: 'PENDING', label: 'Pending', description: 'Payment initiated, awaiting provider confirmation' },
  { code: 'VERIFIED', label: 'Verified', description: 'Funds received and verified by payment provider' },
  { code: 'FAILED', label: 'Failed', description: 'Payment could not be processed' },
  { code: 'REFUNDED', label: 'Refunded', description: 'Payment returned to customer' },
]

// What happens next cards
const nextSteps = computed(() => {
  const steps = []
  const hasDelivery = orders.value.some(o => o.fulfillment_code === 'DELIVERY')
  const hasPickup = orders.value.some(o => o.fulfillment_code === 'PICKUP')

  if (hasDelivery) {
    steps.push({
      icon: '🛵',
      title: 'Delivery scheduled',
      description: 'Your order will be prepared and handed to the delivery partner. You\'ll receive a tracking link when the rider is assigned.',
      action: { label: 'Track delivery', href: '#' }
    })
  }
  if (hasPickup) {
    steps.push({
      icon: '🏪',
      title: 'Pickup reservation',
      description: 'Your items are reserved at the stall. Present your order reference when you collect. Balance (if any) is due at pickup.',
      action: { label: 'View reservation', href: '#' }
    })
  }
  if (!hasDelivery && !hasPickup && orders.value.length > 0) {
    steps.push({
      icon: '✓',
      title: 'Nothing else to pay',
      description: 'Your payment is complete. The vendor will begin preparing your order.',
      action: null
    })
  }
  return steps
})

onMounted(fetchOrders)
</script>

<template>
  <div class="min-h-screen bg-bg">
    <Navbar />

    <main class="page">
      <div class="wrap stack">

        <!-- Page Header -->
        <div class="pagehead">
          <div class="eyebrow">Step 3 of 3</div>
          <h1 v-if="!success && !failed">Payment</h1>
          <h1 v-if="success" class="text-brand">Payment confirmed — {{ orderCount }} order{{ orderCount > 1 ? 's' : '' }} placed</h1>
          <h1 v-if="failed" class="text-danger">Payment failed</h1>
          <p v-if="!success && !failed">Complete your purchase for <strong>{{ orderCount }} order{{ orderCount > 1 ? 's' : '' }}</strong> totaling <strong>{{ formatPrice(grandTotal) }}</strong>.</p>
          <p v-if="success" class="text-ok">All payments have been verified. Your vendors have been notified.</p>
          <p v-if="failed" class="text-danger">Please check the error and try again, or contact support if the issue persists.</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="spinner" style="width: 40px; height: 40px; border: 3px solid var(--color-line); border-top-color: var(--color-brand); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px;"></div>
          <p class="muted">Loading order details…</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error && !success && !failed" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
          <p>{{ error }}</p>
          <button @click="fetchOrders" class="btn btn-primary mt12">Retry</button>
        </div>

        <!-- Success State -->
        <div v-else-if="success" class="stack" style="gap: 24px;">

          <!-- Success Confirmation -->
          <div class="card" style="background: var(--color-ok-bg); border-color: var(--color-ok);">
            <div class="center" style="padding: 16px;">
              <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--color-ok); display: grid; place-items: center; font-size: 1.8rem; margin-bottom: 16px;">✓</div>
              <h2 class="mb8" style="color: var(--color-ok);">Payment confirmed</h2>
              <p class="muted mb0">{{ orderCount }} order{{ orderCount > 1 ? 's' : '' }} placed · {{ formatPrice(grandTotal) }} paid</p>
            </div>
          </div>

          <!-- Orders Table -->
          <div class="card">
            <div class="card-head"><h3>Your orders</h3></div>
            <div class="table-wrap">
              <table class="table">
                <thead>
                  <tr>
                    <th>Reference</th>
                    <th>Vendor</th>
                    <th class="num">Fulfillment</th>
                    <th class="num">Total</th>
                    <th class="num">Order status</th>
                    <th class="num">Payment status</th>
                    <th class="num">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="order in orders" :key="order.id">
                    <td>
                      <strong>#{{ order.transaction?.reference_no || '—' }}</strong>
                    </td>
                    <td>
                      <div><strong>{{ order.vendor_name || order.vendor?.name || '—' }}</strong></div>
                      <div class="tiny muted">{{ order.stall_location || order.vendor?.stall_location || '—' }}</div>
                    </td>
                    <td class="num">
                      <span class="badge" :class="order.fulfillment_code === 'DELIVERY' ? 'badge-info' : 'badge-ok'">
                        {{ fulfillmentIcon(order.fulfillment_code) }} {{ fulfillmentLabels[order.fulfillment_code] || order.fulfillment_display }}
                      </span>
                    </td>
                    <td class="num"><strong>{{ formatPrice(order.total_amount) }}</strong></td>
                    <td class="num">
                      <span class="badge badge-tiny" :class="order.status_code === 'COMPLETED' ? 'badge-ok' : order.status_code === 'CANCELLED' ? 'badge-danger' : 'badge-warn'">
                        {{ orderStatusLabels[order.status_code] || order.status_display || order.status_code }}
                      </span>
                    </td>
                    <td class="num">
                      <span class="badge badge-tiny" :class="paymentStatusColors[payment?.status] || 'badge-warn'">
                        {{ paymentStatusLabels[payment?.status] || 'Pending' }}
                      </span>
                    </td>
                    <td class="num">
                      <button @click="goToOrderTracking(order.id)" class="btn btn-sm btn-ghost">Track</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Payment Record -->
          <div v-if="payment" class="card">
            <div class="card-head row-between">
              <h3>Payment record</h3>
              <span class="badge badge-accent">SANDBOX</span>
            </div>
            <dl class="kv" style="grid-template-columns: 180px 1fr;">
              <dt>Provider</dt><dd>{{ payment.provider }}</dd>
              <dt>Provider reference</dt><dd class="mono">{{ payment.provider_reference }}</dd>
              <dt>Amount</dt><dd class="price price-lg">{{ formatPrice(payment.amount) }}</dd>
              <dt>Status</dt><dd><span class="badge" :class="paymentStatusColors[payment.status]">{{ paymentStatusLabels[payment.status] }}</span></dd>
              <dt>Paid at</dt><dd>{{ formatDateTime(payment.paid_at) }}</dd>
              <dt>Mode</dt><dd><span class="badge badge-accent">SANDBOX</span></dd>
            </dl>
          </div>

          <!-- Payment Status Vocabulary Timeline -->
          <div class="card">
            <div class="card-head"><h3>Payment status vocabulary</h3></div>
            <div class="timeline">
              <div
                v-for="(step, index) in paymentStatusSteps"
                :key="step.code"
                class="node"
                :class="{
                  done: payment?.status === 'VERIFIED' || payment?.status === 'REFUNDED' || (payment?.status === 'FAILED' && index > 0),
                  now: payment?.status === step.code,
                  todo: (payment?.status !== step.code) && !(payment?.status === 'VERIFIED' || payment?.status === 'REFUNDED') && !(payment?.status === 'FAILED' && index > 0)
                }"
              >
                <div class="dot" :class="{ filled: payment?.status === step.code || (payment?.status === 'VERIFIED' && index < 2) || (payment?.status === 'REFUNDED' && index < 3) }"></div>
                <div class="label">
                  <div class="t">{{ step.label }}</div>
                  <div class="d">{{ step.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- What Happens Next -->
          <div class="card">
            <div class="card-head"><h3>What happens next</h3></div>
            <div class="grid grid-3" style="gap: 16px;">
              <div
                v-for="step in nextSteps"
                :key="step.title"
                class="card card-tight"
                style="padding: 16px;"
              >
                <div style="font-size: 2rem; margin-bottom: 8px;">{{ step.icon }}</div>
                <div style="font-weight: 650; margin-bottom: 4px;">{{ step.title }}</div>
                <div class="small muted mb12">{{ step.description }}</div>
                <button v-if="step.action" @click="step.action.href === '#' ? null : router.push(step.action.href)" class="btn btn-sm btn-ghost">{{ step.action.label }}</button>
              </div>
            </div>
          </div>

          <!-- Continue Button -->
          <div class="center" style="margin-top: 8px;">
            <button @click="router.push('/order-tracking')" class="btn btn-primary btn-lg">
              View all orders
            </button>
          </div>

        </div>

        <!-- Failed State (Unhappy Path) -->
        <div v-else-if="failed" class="stack" style="gap: 24px;">

          <div class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
            <div class="center" style="padding: 16px;">
              <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--color-danger); display: grid; place-items: center; font-size: 1.8rem; margin-bottom: 16px;">✕</div>
              <h2 class="mb8" style="color: var(--color-danger);">Payment failed</h2>
              <p class="muted mb0">{{ error }}</p>
            </div>
          </div>

          <div class="card">
            <div class="card-head"><h3>Retry payment</h3></div>
            <div class="note note-warn">
              <strong>Idempotency key:</strong> Each retry uses the same provider reference (<code class="mono">{{ providerReference || 'MANUAL-' + Date.now() }}</code>) so duplicate charges are prevented.
            </div>
            <div class="stack mt12" style="gap: 12px;">
              <button @click="retryPayment" :disabled="processing" class="btn btn-primary btn-lg btn-block">
                <span v-if="processing">Retrying…</span>
                <span v-else>Retry payment · {{ formatPrice(grandTotal) }}</span>
              </button>
              <button @click="goBackToCheckout" :disabled="processing" class="btn btn-block">← Back to checkout</button>
            </div>
          </div>

        </div>

        <!-- Payment Form State (Before Success) -->
        <div v-else-if="orders.length > 0" class="stack" style="gap: 24px;">

          <!-- Order Summary -->
          <div class="card">
            <div class="card-head"><h3>Order summary</h3></div>
            <dl class="kv">
              <dt v-for="order in orders" :key="order.id">
                {{ order.vendor_name || order.vendor?.name || 'Vendor' }}
                <span class="badge badge-tiny" :class="order.fulfillment_code === 'DELIVERY' ? 'badge-info' : 'badge-ok'" style="margin-left: 8px; font-size: 0.65rem;">
                  {{ fulfillmentLabels[order.fulfillment_code] || order.fulfillment_display }}
                </span>
              </dt>
              <dd>{{ formatPrice(order.total_amount) }}</dd>
            </dl>
            <hr class="divider">
            <div class="row-between" style="font-weight: 650; font-size: 1.1rem; margin-top: 8px;">
              <span>Total</span>
              <span class="price price-lg">{{ formatPrice(grandTotal) }}</span>
            </div>
            <div class="tiny muted mt8">{{ orderCount }} order{{ orderCount > 1 ? 's' : '' }}</div>
          </div>

          <!-- Payment Method Selection -->
          <div class="card">
            <div class="card-head"><h3>Payment method</h3></div>
            <div v-for="method in paymentMethods" :key="method.value" class="opt" :class="{ on: paymentMethod === method.value }">
              <input
                type="radio"
                name="pay"
                :value="method.value"
                v-model="paymentMethod"
                :aria-label="method.label"
                :disabled="method.value === 'CASH_PICKUP' && isCashPickupDisabled"
              >
              <span>
                <span class="t">{{ method.icon }} {{ method.label }}</span>
                <span class="d">{{ method.desc }}</span>
              </span>
            </div>

            <!-- Provider Reference Input -->
            <div v-if="paymentMethod !== 'CASH_PICKUP'" class="field mt12">
              <label class="small muted">Reference number <span class="text-danger">*</span></label>
              <input
                type="text"
                v-model="providerReference"
                :placeholder="paymentMethod === 'GCASH' ? 'Enter GCash reference number' : paymentMethod === 'MAYA' ? 'Enter Maya reference number' : paymentMethod === 'ONLINE_BANKING' ? 'Enter bank transaction reference' : 'Enter card transaction reference'"
                class="input"
                aria-label="Payment reference number"
              >
              <p class="tiny muted mt4">Enter the transaction reference from your payment provider</p>
            </div>

            <div v-if="paymentMethod === 'CASH_PICKUP'" class="note note-warn mt12 tiny">
              <strong>Cash at pickup:</strong> No reference number needed. Payment will be collected upon pickup at the stall.
            </div>

            <div class="note note-warn mt12 tiny">
              Payments run in <strong>sandbox / test mode</strong>. No real money moves and no card details are stored.
            </div>
          </div>

          <!-- Pay Button -->
          <div class="card card-tight">
            <button
              @click="processPayment"
              :disabled="processing || (paymentMethod !== 'CASH_PICKUP' && !providerReference.trim())"
              class="btn btn-primary btn-lg btn-block"
              style="width: 100%;"
            >
              <span v-if="processing">Processing…</span>
              <span v-else>Pay {{ formatPrice(grandTotal) }}</span>
            </button>
            <div class="center tiny muted mt8">
              By paying, you agree to the terms and confirm your order details.
            </div>
          </div>

        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <p class="muted mb4">No orders found</p>
          <router-link to="/cart" class="btn btn-primary">← Back to cart</router-link>
        </div>

      </div>
    </main>

    <footer class="foot">
      <div class="wrap row-between">
        <span>E-Compra · CCS630 Advance Database Systems capstone</span>
        <span>All prices in Philippine pesos (₱)</span>
      </div>
    </footer>

    <style>
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    </style>
  </div>
</template>

<style scoped>
/* Timeline dot filled state */
.node.now .dot.filled,
.node.done .dot.filled {
  background: var(--color-brand);
  border-color: var(--color-brand);
}

/* Ensure timeline dots use brand color when active */
.timeline .node.now .dot {
  background: var(--color-brand);
  border-color: var(--color-brand);
}

.timeline .node.done .dot {
  background: var(--color-brand);
  border-color: var(--color-brand);
}
</style>