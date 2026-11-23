<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useCartStore } from '@/stores/cart'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()
const cartStore = useCartStore()

const cart = ref({ items: [] })
const loading = ref(true)
const error = ref(null)
const processing = ref(false)

// Form state
const paymentMethod = ref('GCASH')
const deliveryPartner = ref('LALAMOVE')
const deliveryAddress = ref('')

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const categoryIcons = {
  'Fish': '🐟',
  'Meat': '🥩',
  'Poultry': '🍗',
  'Fruits': '🍎',
  'Vegetables': '🥬',
  'Rice': '🍚',
  'Dry goods': '🫙',
  'Spices': '🧂',
  'Others': '🧺',
}

const getCategoryIcon = (name) => categoryIcons[name] || '📦'

// Group items by vendor
const itemsByVendor = computed(() => {
  const grouped = {}
  if (cart.value.items) {
    cart.value.items.forEach(item => {
      const vendorId = item.vendor_id || 'unknown'
      if (!grouped[vendorId]) {
        grouped[vendorId] = {
          vendor_id: vendorId,
          vendor_name: item.vendor_name || 'Unknown Vendor',
          stall_location: item.stall_location || '—',
          section_name: item.section_name || '—',
          items: [],
          subtotal: 0,
          fulfillment: cartStore.fulfillmentMethods[vendorId] || 'DELIVERY'
        }
      }
      grouped[vendorId].items.push(item)
      grouped[vendorId].subtotal += Number(item.product_price) * Number(item.quantity)
    })
  }
  return grouped
})

const vendorCount = computed(() => Object.keys(itemsByVendor.value).length)

const deliveryVendorCount = computed(() => {
  return Object.values(itemsByVendor.value).filter(v => v.fulfillment === 'DELIVERY').length
})

const pickupVendorCount = computed(() => {
  return Object.values(itemsByVendor.value).filter(v => v.fulfillment === 'PICKUP').length
})

const deliveryFee = computed(() => deliveryVendorCount.value * 95)

const grandTotal = computed(() => {
  let total = 0
  Object.values(itemsByVendor.value).forEach(vendor => {
    total += vendor.subtotal
  })
  total += deliveryFee.value
  return total
})

const paymentMethods = [
  { value: 'GCASH', icon: '📱', label: 'GCash', desc: 'Pay online now · sandbox' },
  { value: 'MAYA', icon: '📱', label: 'Maya', desc: 'Pay online now · sandbox' },
  { value: 'ONLINE_BANKING', icon: '🏦', label: 'Online banking', desc: 'Sandbox' },
  { value: 'CARD', icon: '💳', label: 'Card', desc: 'Sandbox · no card data is stored' },
  { value: 'CASH_PICKUP', icon: '💵', label: 'Cash at pickup', desc: 'Pickup orders only' },
]

const deliveryPartners = [
  { value: 'LALAMOVE', label: 'Lalamove', fee: 95 },
  { value: 'GRABEXPRESS', label: 'GrabExpress', fee: 110 },
  { value: 'MAXIM', label: 'Maxim', fee: 85 },
  { value: 'LOCAL_RIDER', label: 'Local market rider', fee: 60 },
]

const fetchCart = async () => {
  try {
    loading.value = true
    const response = await api.get('/cart/')
    cart.value = response.data
    // Initialize fulfillment methods from cart store if not already set
    if (response.data.items) {
      const vendors = [...new Set(response.data.items.map(i => i.vendor_id).filter(Boolean))]
      vendors.forEach(vid => {
        if (!cartStore.fulfillmentMethods[vid]) {
          cartStore.fulfillmentMethods[vid] = 'DELIVERY'
        }
      })
    }
  } catch (err) {
    error.value = 'Failed to load checkout'
  } finally {
    loading.value = false
  }
}

async function placeOrders() {
  try {
    processing.value = true
    error.value = null

    // Build fulfillment methods from itemsByVendor (already synced from cart store)
    const fulfillmentMethods = {}
    Object.values(itemsByVendor.value).forEach(vendor => {
      fulfillmentMethods[vendor.vendor_id] = vendor.fulfillment
    })

    const response = await api.post('/checkout/', {
      fulfillment_methods: fulfillmentMethods,
      payment_method: paymentMethod.value,
      delivery_partner: deliveryPartner.value,
      delivery_address: deliveryAddress.value
    })

    const orderIds = response.data.order_ids
    const transactionIds = response.data.transaction_ids

    // Clear cart store
    cartStore.clear()

    // Redirect to payment screen with all transaction IDs
    if (transactionIds.length > 0) {
      router.push({
        name: 'payment',
        params: { id: transactionIds[0] }, // Keep first for backward compatibility
        query: { transactions: transactionIds.join(',') } // Pass all for enhanced view
      })
    } else {
      router.push('/catalog')
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Checkout failed'
  } finally {
    processing.value = false
  }
}

function goBackToCart() {
  router.push('/cart')
}

onMounted(fetchCart)
</script>

<template>
  <div class="min-h-screen bg-bg">
    <Navbar />

    <main class="page">
      <div class="wrap stack">

        <!-- Page Header -->
        <div class="pagehead">
          <div class="eyebrow">Step 2 of 3</div>
          <h1>Checkout</h1>
          <p>Review your orders and choose how you'd like to pay. You're placing <strong>{{ vendorCount }} order{{ vendorCount > 1 ? 's' : '' }}</strong>.</p>
        </div>

        <div v-if="loading" class="text-center py-12">Loading…</div>

        <div v-else-if="error" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
          <p>{{ error }}</p>
          <button @click="fetchCart" class="btn btn-primary mt12">Retry</button>
        </div>

        <div v-else-if="cart.items && cart.items.length > 0">
          <div class="grid-side checkout-grid" style="gap: 24px;">

            <!-- Order Review (Left Side) -->
            <div class="stack" style="gap: 16px;">
              <section
                v-for="(vendor, vendorId) in itemsByVendor"
                :key="vendorId"
                class="card"
              >
                <div class="card-head row-between">
                  <div>
                    <h3 class="mb0">🏪 {{ vendor.vendor_name }}</h3>
                    <span class="small muted">📍 {{ vendor.stall_location }} · {{ vendor.section_name }}</span>
                  </div>
                  <span class="badge badge-info">Order {{ Object.keys(itemsByVendor).indexOf(vendorId) + 1 }} of {{ vendorCount }}</span>
                </div>

                <div class="table-wrap">
                  <table class="table">
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th class="num">Unit price</th>
                        <th class="num">Qty</th>
                        <th class="num">Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="item in vendor.items" :key="item.id">
                        <td>
                          <div class="row" style="align-items: center; gap: 12px;">
                            <span style="font-size: 1.4rem;">{{ getCategoryIcon(item.category_name || item.category) }}</span>
                            <span>
                              <strong>{{ item.product_name }}</strong><br>
                              <span class="tiny muted">Sold per {{ item.unit || 'kg' }}</span>
                            </span>
                          </div>
                        </td>
                        <td class="num">{{ formatPrice(item.product_price) }} / {{ item.unit || 'kg' }}</td>
                        <td class="num">{{ item.quantity }}</td>
                        <td class="num"><strong>{{ formatPrice(Number(item.product_price) * Number(item.quantity)) }}</strong></td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div class="card-foot stack" style="gap: 12px;">
                  <div class="field mb8"><span>Fulfillment for this vendor</span></div>

                  <label
                    class="opt"
                    :class="{ on: vendor.fulfillment === 'DELIVERY' }"
                  >
                    <input
                      type="radio"
                      :name="'ff-' + vendorId"
                      value="DELIVERY"
                      v-model="vendor.fulfillment"
                      aria-label="Delivery"
                    >
                    <span>
                      <span class="t">🛵 Delivery</span>
                      <span class="d">To your address · quoted ₱95.00</span>
                    </span>
                  </label>

                  <label
                    class="opt"
                    :class="{ on: vendor.fulfillment === 'PICKUP' }"
                  >
                    <input
                      type="radio"
                      :name="'ff-' + vendorId"
                      value="PICKUP"
                      v-model="vendor.fulfillment"
                      aria-label="Pickup"
                    >
                    <span>
                      <span class="t">🏪 Pickup at the stall</span>
                      <span class="d">Collect at {{ vendor.stall_location }} · free</span>
                    </span>
                  </label>

                  <div class="row-between mt12">
                    <span class="muted small">Vendor subtotal</span>
                    <span class="price">{{ formatPrice(vendor.subtotal) }}</span>
                  </div>
                </div>
              </section>

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
                    :disabled="method.value === 'CASH_PICKUP' && pickupVendorCount === 0"
                  >
                  <span>
                    <span class="t">{{ method.icon }} {{ method.label }}</span>
                    <span class="d">{{ method.desc }}</span>
                  </span>
                </div>
                <div class="note note-warn mt12 tiny">
                  Payments run in <strong>sandbox / test mode</strong>. No real money moves and no card details are stored.
                </div>
              </div>

              <!-- Delivery Address (for delivery orders) -->
              <div v-if="deliveryVendorCount > 0" class="card">
                <div class="card-head"><h3>Delivery address</h3></div>
                <div class="field">
                  <label class="small muted">Drop-off location</label>
                  <textarea
                    v-model="deliveryAddress"
                    class="input"
                    rows="3"
                    placeholder="Enter delivery address (e.g., Unit 4B, A.C. Cortes Ave., Mandaue City)"
                    aria-label="Delivery address"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Summary Sidebar (Right Side) -->
            <aside class="stack" style="gap: 16px; position: sticky; top: 80px;">
              <!-- Order Summary -->
              <div class="card">
                <div class="card-head"><h3>Order summary</h3></div>
                <dl class="kv">
                  <template v-for="(vendor, vendorId) in itemsByVendor" :key="vendorId">
                    <dt>
                      {{ vendor.vendor_name }}
                      <span class="badge badge-tiny" :class="vendor.fulfillment === 'DELIVERY' ? 'badge-info' : 'badge-ok'" style="margin-left: 8px; font-size: 0.65rem;">
                        {{ vendor.fulfillment === 'DELIVERY' ? 'Delivery' : 'Pickup' }}
                      </span>
                    </dt>
                    <dd>{{ formatPrice(vendor.subtotal) }}</dd>
                  </template>
                </dl>
                <hr class="divider">
                <div v-if="deliveryFee > 0" class="kv" style="margin-top: 8px;">
                  <dt>Delivery fee ({{ deliveryVendorCount }} vendor{{ deliveryVendorCount > 1 ? 's' : '' }} · {{ deliveryPartners.find(p => p.value === deliveryPartner)?.label || 'Lalamove' }})</dt>
                  <dd>₱{{ deliveryFee.toFixed(2) }}</dd>
                </div>
                <div class="row-between" style="font-weight: 650; font-size: 1.1rem; margin-top: 8px;">
                  <span>Total</span>
                  <span class="price price-lg">{{ formatPrice(grandTotal) }}</span>
                </div>
                <div class="tiny muted mt8">
                  {{ vendorCount }} order{{ vendorCount > 1 ? 's' : '' }} · {{ pickupVendorCount }} for pickup, {{ deliveryVendorCount }} for delivery
                </div>
              </div>

              <!-- Delivery Partner Selection -->
              <div v-if="deliveryVendorCount > 0" class="card">
                <div class="card-head"><h3>Delivery quote</h3></div>
                <label class="field">
                  <span>Partner</span>
                  <select
                    v-model="deliveryPartner"
                    class="input"
                    aria-label="Delivery partner"
                  >
                    <option v-for="partner in deliveryPartners" :key="partner.value" :value="partner.value">
                      {{ partner.label }} — ₱{{ partner.fee }}.00
                    </option>
                  </select>
                </label>
                <dl class="kv">
                  <dt>Estimated time</dt><dd>45–60 min</dd>
                  <dt>Drop-off</dt><dd>{{ deliveryAddress || 'Your saved address' }}</dd>
                </dl>
                <div class="note mt12 tiny">Delivery is <strong>mocked</strong> in this project — the partner is simulated.</div>
              </div>

              <!-- Action Buttons -->
              <button
                @click="placeOrders"
                :disabled="processing"
                class="btn btn-accent btn-lg btn-block"
              >
                <span v-if="processing">Placing {{ vendorCount }} order{{ vendorCount > 1 ? 's' : '' }}…</span>
                <span v-else>Place {{ vendorCount }} order{{ vendorCount > 1 ? 's' : '' }} · {{ formatPrice(grandTotal) }}</span>
              </button>
              <button
                @click="goBackToCart"
                class="btn btn-block"
                :disabled="processing"
              >
                ← Back to cart
              </button>
            </aside>

          </div>
        </div>

        <div v-else class="text-center py-12">
          <p class="muted mb4">Your cart is empty</p>
          <router-link to="/catalog" class="btn btn-primary">Start shopping</router-link>
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