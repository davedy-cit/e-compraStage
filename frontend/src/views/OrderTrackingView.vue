<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import OrderCard from '@/components/OrderCard.vue'

const route = useRoute()
const router = useRouter()

// State for list view
const orders = ref([])
const loading = ref(true)
const error = ref('')
const activeFilter = ref('all') // all, active, completed, history

// State for single order detail view
const singleOrder = ref(null)
const singleOrderLoading = ref(false)
const singleOrderError = ref('')

// Determine which view to show
const isListView = computed(() => !route.params.id)
const isDetailView = computed(() => !!route.params.id)

// Formatters
const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatDateShort = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

// Status step definitions for timeline
const orderStatusSteps = [
  { code: 'PENDING_PAYMENT', label: 'Pending Payment', icon: '⏳' },
  { code: 'CONFIRMED', label: 'Confirmed', icon: '✅' },
  { code: 'PREPARING', label: 'Preparing', icon: '📦' },
  { code: 'READY_FOR_PICKUP', label: 'Ready for Pickup', icon: '🔔' },
  { code: 'OUT_FOR_DELIVERY', label: 'Out for Delivery', icon: '🚚' },
  { code: 'COMPLETED', label: 'Completed', icon: '🎉' },
]

const paymentStatusSteps = [
  { code: 'PENDING', label: 'Pending', desc: 'Payment initiated' },
  { code: 'VERIFIED', label: 'Verified', desc: 'Funds received' },
  { code: 'FAILED', label: 'Failed', desc: 'Payment failed' },
  { code: 'REFUNDED', label: 'Refunded', desc: 'Payment refunded' },
]

const deliveryStatusSteps = [
  { code: 'BOOKED', label: 'Booked', desc: 'Courier assigned' },
  { code: 'PICKED_UP', label: 'Picked Up', desc: 'Rider has order' },
  { code: 'IN_TRANSIT', label: 'In Transit', desc: 'On the way' },
  { code: 'DELIVERED', label: 'Delivered', desc: 'Completed' },
  { code: 'FAILED', label: 'Failed', desc: 'Delivery failed' },
]

// Fulfillment icons
const fulfillmentIcon = (code) => code === 'DELIVERY' ? '🛵' : '🏪'
const fulfillmentLabel = (code) => code === 'DELIVERY' ? 'Delivery' : 'Pickup'

// Status badge classes
const getOrderStatusClass = (code) => {
  if (code === 'COMPLETED') return 'badge-ok'
  if (code === 'CANCELLED') return 'badge-danger'
  if (code === 'PENDING_PAYMENT') return 'badge-warn'
  return 'badge-info'
}

const getPaymentStatusClass = (code) => {
  if (code === 'VERIFIED') return 'badge-ok'
  if (code === 'FAILED') return 'badge-danger'
  if (code === 'REFUNDED') return 'badge-info'
  return 'badge-warn'
}

const getDeliveryStatusClass = (code) => {
  if (code === 'DELIVERED') return 'badge-ok'
  if (code === 'FAILED') return 'badge-danger'
  return 'badge-info'
}

// Fetch all orders for the current user (list view)
const fetchOrders = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await api.get('/orders/')
    orders.value = response.data.results || response.data
  } catch (e) {
    error.value = 'Failed to load orders'
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Fetch single order detail
const fetchSingleOrder = async () => {
  if (!route.params.id) return
  try {
    singleOrderLoading.value = true
    singleOrderError.value = ''
    const response = await api.get(`/orders/${route.params.id}/`)
    singleOrder.value = response.data
  } catch (e) {
    singleOrderError.value = 'Order not found'
    console.error(e)
  } finally {
    singleOrderLoading.value = false
  }
}

// Computed: filtered orders for list view
const filteredOrders = computed(() => {
  let result = orders.value
  if (activeFilter.value === 'active') {
    result = result.filter(o => ['PENDING_PAYMENT', 'CONFIRMED', 'PREPARING', 'OUT_FOR_DELIVERY', 'READY_FOR_PICKUP'].includes(o.status_code))
  } else if (activeFilter.value === 'completed') {
    result = result.filter(o => o.status_code === 'COMPLETED')
  } else if (activeFilter.value === 'history') {
    result = result.filter(o => ['COMPLETED', 'CANCELLED'].includes(o.status_code))
  }
  return result
})

// Computed: split orders by fulfillment type
const deliveryOrders = computed(() => filteredOrders.value.filter(o => o.fulfillment_code === 'DELIVERY'))
const pickupOrders = computed(() => filteredOrders.value.filter(o => o.fulfillment_code === 'PICKUP'))

// Computed: current step index for timeline
const getCurrentStepIndex = (orderStatus) => {
  return orderStatusSteps.findIndex(s => s.code === orderStatus)
}

const getPaymentStepIndex = (paymentStatus) => {
  return paymentStatusSteps.findIndex(s => s.code === paymentStatus)
}

const getDeliveryStepIndex = (deliveryStatus) => {
  return deliveryStatusSteps.findIndex(s => s.code === deliveryStatus)
}

// Navigation
function goToOrderDetail(orderId) {
  router.push({ name: 'order-detail', params: { id: orderId } })
}

function goBackToList() {
  router.push({ name: 'order-tracking' })
}

// Watch route changes to fetch appropriate data
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchSingleOrder()
  } else {
    fetchOrders()
  }
}, { immediate: true })

onMounted(() => {
  if (isListView.value) {
    fetchOrders()
  } else {
    fetchSingleOrder()
  }
})
</script>

<template>
  <div class="min-h-screen bg-bg">
    <main class="page">
      <div class="wrap stack">

        <!-- LIST VIEW: Order Tracking Dashboard -->
        <div v-if="isListView" class="stack" style="gap: 24px;">

          <!-- Page Header -->
          <div class="pagehead">
            <h1>Order Tracking</h1>
            <p>Track your delivery and pickup orders in real time.</p>
          </div>

          <!-- Filter Chips -->
          <div class="chips" role="tablist" aria-label="Order filters">
            <button
              v-for="filter in [
                { value: 'all', label: 'All' },
                { value: 'active', label: 'Active' },
                { value: 'completed', label: 'Completed' },
                { value: 'history', label: 'History' }
              ]"
              :key="filter.value"
              @click="activeFilter = filter.value"
              :class="{ on: activeFilter === filter.value }"
              class="chip"
              role="tab"
              :aria-selected="activeFilter === filter.value"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="text-center py-12">
            <div class="spinner" style="width: 40px; height: 40px; border: 3px solid var(--color-line); border-top-color: var(--color-brand); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px;"></div>
            <p class="muted">Loading orders…</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
            <p>{{ error }}</p>
            <button @click="fetchOrders" class="btn btn-primary mt12">Retry</button>
          </div>

          <!-- Orders Content -->
          <div v-else class="stack" style="gap: 24px;">

            <!-- Split View: Delivery + Pickup -->
            <div class="grid grid-2" style="gap: 24px;">

              <!-- Delivery Orders -->
              <section>
                <div class="row-between mb12" style="align-items: center;">
                  <h2 class="mb0">🛵 Delivery Orders</h2>
                  <span class="badge badge-info">{{ deliveryOrders.length }}</span>
                </div>
                <div v-if="deliveryOrders.length === 0" class="card card-tight" style="padding: 24px; text-align: center;">
                  <p class="muted mb0">No delivery orders</p>
                </div>
                <div v-else class="stack" style="gap: 12px;">
                  <OrderCard
                    v-for="order in deliveryOrders"
                    :key="order.id"
                    :order="order"
                    @click="goToOrderDetail(order.id)"
                  />
                </div>
              </section>

              <!-- Pickup Orders -->
              <section>
                <div class="row-between mb12" style="align-items: center;">
                  <h2 class="mb0">🏪 Pickup Orders</h2>
                  <span class="badge badge-ok">{{ pickupOrders.length }}</span>
                </div>
                <div v-if="pickupOrders.length === 0" class="card card-tight" style="padding: 24px; text-align: center;">
                  <p class="muted mb0">No pickup orders</p>
                </div>
                <div v-else class="stack" style="gap: 12px;">
                  <OrderCard
                    v-for="order in pickupOrders"
                    :key="order.id"
                    :order="order"
                    @click="goToOrderDetail(order.id)"
                  />
                </div>
              </section>

            </div>

            <!-- Vocabulary Cards -->
            <div class="grid grid-3" style="gap: 16px;">
              <div class="card card-tight" style="padding: 16px;">
                <h4 class="mb8">Order Status</h4>
                <div class="stack" style="gap: 6px;">
                  <div v-for="step in orderStatusSteps" :key="step.code" class="row-between tiny">
                    <span>{{ step.icon }} {{ step.label }}</span>
                    <span class="badge badge-tiny" :class="getOrderStatusClass(step.code)">{{ step.code }}</span>
                  </div>
                </div>
              </div>

              <div class="card card-tight" style="padding: 16px;">
                <h4 class="mb8">Payment Status</h4>
                <div class="stack" style="gap: 6px;">
                  <div v-for="step in paymentStatusSteps" :key="step.code" class="row-between tiny">
                    <span>{{ step.label }}</span>
                    <span class="badge badge-tiny" :class="getPaymentStatusClass(step.code)">{{ step.code }}</span>
                  </div>
                </div>
              </div>

              <div class="card card-tight" style="padding: 16px;">
                <h4 class="mb8">Delivery Status</h4>
                <div class="stack" style="gap: 6px;">
                  <div v-for="step in deliveryStatusSteps" :key="step.code" class="row-between tiny">
                    <span>{{ step.label }}</span>
                    <span class="badge badge-tiny badge-info">{{ step.code }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>

        <!-- DETAIL VIEW: Single Order Detail -->
        <div v-else-if="isDetailView" class="stack" style="gap: 24px;">

          <!-- Back Button + Header -->
          <div v-if="singleOrderLoading" class="text-center py-12">
            <div class="spinner" style="width: 40px; height: 40px; border: 3px solid var(--color-line); border-top-color: var(--color-brand); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px;"></div>
            <p class="muted">Loading order…</p>
          </div>

          <div v-else-if="singleOrderError" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
            <p>{{ singleOrderError }}</p>
            <button @click="goBackToList" class="btn btn-primary mt12">← Back to orders</button>
          </div>

          <div v-else-if="singleOrder" class="stack" style="gap: 24px;">

            <!-- Order Header -->
            <div class="card">
              <div class="card-head row-between">
                <div>
                  <h2 class="mb0">Order #{{ singleOrder.id }}</h2>
                  <p class="muted tiny">{{ formatDate(singleOrder.created_at) }}</p>
                </div>
                <div class="row" style="gap: 8px; align-items: center;">
                  <span class="badge" :class="getOrderStatusClass(singleOrder.status_code)">
                    {{ singleOrder.status_display || singleOrder.status_code }}
                  </span>
                  <button @click="goBackToList" class="btn btn-ghost btn-sm">← Back</button>
                </div>
              </div>

              <div class="grid grid-3" style="margin-top: 16px; gap: 16px;">
                <div>
                  <p class="tiny muted">Vendor</p>
                  <p class="font-medium">{{ singleOrder.vendor_name || singleOrder.vendor?.name || '—' }}</p>
                  <p class="tiny muted">📍 {{ singleOrder.stall_location || singleOrder.vendor?.stall_location || '—' }}</p>
                </div>
                <div>
                  <p class="tiny muted">Fulfillment</p>
                  <p class="font-medium">
                    <span class="badge" :class="singleOrder.fulfillment_code === 'DELIVERY' ? 'badge-info' : 'badge-ok'">
                      {{ fulfillmentIcon(singleOrder.fulfillment_code) }} {{ fulfillmentLabel(singleOrder.fulfillment_code) }}
                    </span>
                  </p>
                </div>
                <div class="text-right">
                  <p class="tiny muted">Total</p>
                  <p class="price price-lg">{{ formatPrice(singleOrder.total_amount) }}</p>
                </div>
              </div>

              <!-- Pickup-specific info -->
              <div v-if="singleOrder.fulfillment_code === 'PICKUP'" class="note note-warn mt12" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                <div>
                  <p class="tiny muted">Down payment paid</p>
                  <p class="font-medium">{{ formatPrice(singleOrder.total_amount * 0.2) }}</p>
                </div>
                <div>
                  <p class="tiny muted">Balance due at stall</p>
                  <p class="font-medium text-danger">{{ formatPrice(singleOrder.total_amount * 0.8) }}</p>
                </div>
                <div>
                  <p class="tiny muted">Hold expires</p>
                  <p class="font-medium">{{ formatDateShort(new Date(Date.now() + 24*60*60*1000).toISOString()) }}</p>
                </div>
              </div>
            </div>

            <!-- Status Timelines -->
            <div class="grid grid-2" style="gap: 24px;">
              <!-- Order Status Timeline -->
              <div class="card">
                <div class="card-head"><h3>Order Status</h3></div>
                <div class="timeline">
                  <div
                    v-for="(step, index) in orderStatusSteps"
                    :key="step.code"
                    class="node"
                    :class="{
                      done: index < getCurrentStepIndex(singleOrder.status_code),
                      now: index === getCurrentStepIndex(singleOrder.status_code),
                      todo: index > getCurrentStepIndex(singleOrder.status_code)
                    }"
                  >
                    <div class="dot" :class="{ filled: index <= getCurrentStepIndex(singleOrder.status_code) }"></div>
                    <div class="label">
                      <div class="t">{{ step.icon }} {{ step.label }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Payment Status Timeline -->
              <div class="card">
                <div class="card-head"><h3>Payment Status</h3></div>
                <div class="timeline">
                  <div
                    v-for="(step, index) in paymentStatusSteps"
                    :key="step.code"
                    class="node"
                    :class="{
                      done: singleOrder.transaction?.payments?.length && index < getPaymentStepIndex(singleOrder.transaction?.payments?.[0]?.status_code || 'PENDING'),
                      now: singleOrder.transaction?.payments?.length && index === getPaymentStepIndex(singleOrder.transaction?.payments?.[0]?.status_code || 'PENDING'),
                      todo: !singleOrder.transaction?.payments?.length || index > getPaymentStepIndex(singleOrder.transaction?.payments?.[0]?.status_code || 'PENDING')
                    }"
                  >
                    <div class="dot" :class="{ filled: singleOrder.transaction?.payments?.length && index <= getPaymentStepIndex(singleOrder.transaction?.payments?.[0]?.status_code || 'PENDING') }"></div>
                    <div class="label">
                      <div class="t">{{ step.label }}</div>
                      <div class="d">{{ step.desc }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Order Items -->
            <div class="card">
              <div class="card-head"><h3>Items</h3></div>
              <div class="table-wrap">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th class="num">Qty</th>
                      <th class="num">Unit Price</th>
                      <th class="num">Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in singleOrder.items" :key="item.id">
                      <td>
                        <div class="row" style="align-items: center; gap: 12px;">
                          <span style="font-size: 1.4rem;">📦</span>
                          <span>
                            <strong>{{ item.product_name }}</strong><br>
                            <span class="tiny muted">Sold per {{ item.product?.unit || 'kg' }}</span>
                          </span>
                        </div>
                      </td>
                      <td class="num">{{ item.quantity }}</td>
                      <td class="num">{{ formatPrice(item.unit_price) }}</td>
                      <td class="num"><strong>{{ formatPrice(item.quantity * item.unit_price) }}</strong></td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="card-foot row-between">
                <span class="font-medium">Total</span>
                <span class="price price-lg">{{ formatPrice(singleOrder.total_amount) }}</span>
              </div>
            </div>

            <!-- Delivery Info (if delivery) -->
            <div v-if="singleOrder.fulfillment_code === 'DELIVERY' && singleOrder.transaction?.delivery_booking" class="card">
              <div class="card-head"><h3>Delivery Tracking</h3></div>
              <dl class="kv">
                <dt>Partner</dt><dd>{{ singleOrder.transaction.delivery_booking.provider }}</dd>
                <dt>Booking Reference</dt><dd class="mono">{{ singleOrder.transaction.delivery_booking.booking_reference }}</dd>
                <dt>Status</dt><dd><span class="badge badge-info">{{ singleOrder.transaction.delivery_booking.status?.description || singleOrder.transaction.delivery_booking.status }}</span></dd>
                <dt>Booked At</dt><dd>{{ formatDate(singleOrder.transaction.delivery_booking.booked_at) }}</dd>
                <dt v-if="singleOrder.transaction.delivery_booking.tracking_url">Tracking</dt>
                <dd v-if="singleOrder.transaction.delivery_booking.tracking_url">
                  <a :href="singleOrder.transaction.delivery_booking.tracking_url" target="_blank" class="btn btn-sm btn-ghost">Track on partner site →</a>
                </dd>
              </dl>
            </div>

          </div>

        </div>

      </div>
    </main>

    <footer class="foot">
      <div class="wrap row-between">
        <span>E-Compra · CCS630 Advance Database Systems capstone</span>
        <span>All prices in Philippine pesos (₱)</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>