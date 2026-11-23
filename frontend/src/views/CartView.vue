<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()

const cart = ref({ items: [] })
const loading = ref(true)
const error = ref(null)
const fulfillmentMethods = ref({}) // vendor_id -> 'DELIVERY' | 'PICKUP'

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
          subtotal: 0
        }
      }
      grouped[vendorId].items.push(item)
      grouped[vendorId].subtotal += Number(item.product_price) * Number(item.quantity)
    })
  }
  return grouped
})

const vendorCount = computed(() => Object.keys(itemsByVendor.value).length)

const fetchCart = async () => {
  try {
    loading.value = true
    const response = await api.get('/cart/')
    cart.value = response.data
    // Initialize fulfillment methods for each vendor (default to DELIVERY)
    if (response.data.items) {
      const vendors = [...new Set(response.data.items.map(i => i.vendor_id).filter(Boolean))]
      vendors.forEach(vid => {
        if (!fulfillmentMethods.value[vid]) {
          fulfillmentMethods.value[vid] = 'DELIVERY'
        }
      })
    }
  } catch (err) {
    error.value = 'Failed to load cart'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function updateQuantity(itemId, quantity) {
  if (quantity < 1) return
  try {
    await api.post('/cart/update_item/', { item_id: itemId, quantity })
    await fetchCart()
  } catch (err) {
    error.value = 'Failed to update quantity'
    console.error(err)
  }
}

async function removeItem(itemId) {
  try {
    await api.post('/cart/remove_item/', { item_id: itemId })
    await fetchCart()
  } catch (err) {
    error.value = 'Failed to remove item'
    console.error(err)
  }
}

function proceedToCheckout() {
  // Store fulfillment methods in cart store for checkout
  cartStore.setFulfillmentMethods(fulfillmentMethods.value)
  router.push('/checkout')
}

function continueShopping() {
  router.push('/catalog')
}

// Sync fulfillment methods with cart store
watch(() => cartStore.fulfillmentMethods, (newMethods) => {
  if (newMethods) {
    fulfillmentMethods.value = { ...newMethods }
  }
}, { immediate: true, deep: true })

// Computed for summary
const deliveryVendorCount = computed(() => {
  return Object.values(fulfillmentMethods.value).filter(m => m === 'DELIVERY').length
})

const pickupVendorCount = computed(() => {
  return Object.values(fulfillmentMethods.value).filter(m => m === 'PICKUP').length
})

const hasDeliveryFee = computed(() => deliveryVendorCount.value > 0)

const grandTotal = computed(() => {
  let total = 0
  Object.values(itemsByVendor.value).forEach(vendor => {
    total += vendor.subtotal
  })
  // Add delivery fee (₱95 per delivery vendor)
  total += deliveryVendorCount.value * 95
  return total
})

onMounted(fetchCart)
</script>

<template>
  <div class="min-h-screen bg-bg">
    <Navbar />

    <main class="page">
      <div class="wrap stack">

        <!-- Page Header -->
        <div class="pagehead">
          <div class="eyebrow">Step 1 of 3</div>
          <h1>Your cart</h1>
          <p v-if="vendorCount > 1">
            Your items come from <strong>{{ vendorCount }} different vendor{{ vendorCount > 1 ? 's' : '' }}</strong>, so checkout creates
            <strong>{{ vendorCount }} separate order{{ vendorCount > 1 ? 's' : '' }}</strong> —
            one per vendor. Each has its own status, its own payment, and its own pickup or delivery arrangement.
          </p>
          <p v-else-if="vendorCount === 1">
            Your items are from <strong>1 vendor</strong>. Checkout will create <strong>1 order</strong>.
          </p>
        </div>

        <div class="note">
          <strong>Why one order per vendor?</strong> A vendor can only prepare, price and hand over their own goods.
          Splitting the cart keeps every order trackable on its own — Rosa can have your vegetables ready at 4 PM
          while Nena is still dressing your chicken.
        </div>

        <div v-if="loading" class="text-center py-12">Loading…</div>

        <div v-else-if="error" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
          <p>{{ error }}</p>
          <button @click="fetchCart" class="btn btn-primary mt12">Retry</button>
        </div>

        <div v-else-if="cart.items && cart.items.length > 0">
          <div class="grid-side" style="grid-template-columns: 1fr 330px; gap: 24px;">

            <!-- Vendor Groups (Left Side) -->
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
                        <td class="num">
                          <div class="row" style="align-items: center; gap: 8px;">
                            <button
                              @click="updateQuantity(item.id, item.quantity - 1)"
                              :disabled="item.quantity <= 1"
                              class="btn btn-sm"
                              style="width: 32px; height: 32px; padding: 0; display: flex; align-items: center; justify-content: center;"
                            >−</button>
                            <span class="w-8 text-center" style="font-weight: 500;">{{ item.quantity }}</span>
                            <button
                              @click="updateQuantity(item.id, item.quantity + 1)"
                              class="btn btn-sm"
                              style="width: 32px; height: 32px; padding: 0; display: flex; align-items: center; justify-content: center;"
                            >+</button>
                          </div>
                        </td>
                        <td class="num"><strong>{{ formatPrice(Number(item.product_price) * Number(item.quantity)) }}</strong></td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div class="card-foot stack" style="gap: 12px;">
                  <div class="field mb8"><span>Fulfillment for this vendor</span></div>

                  <label
                    class="opt"
                    :class="{ on: fulfillmentMethods[vendorId] === 'DELIVERY' }"
                  >
                    <input
                      type="radio"
                      :name="'ff-' + vendorId"
                      value="DELIVERY"
                      v-model="fulfillmentMethods[vendorId]"
                      aria-label="Delivery"
                    >
                    <span>
                      <span class="t">🛵 Delivery</span>
                      <span class="d">To your address · quoted ₱95.00</span>
                    </span>
                  </label>

                  <label
                    class="opt"
                    :class="{ on: fulfillmentMethods[vendorId] === 'PICKUP' }"
                  >
                    <input
                      type="radio"
                      :name="'ff-' + vendorId"
                      value="PICKUP"
                      v-model="fulfillmentMethods[vendorId]"
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
            </div>

            <!-- Summary Sidebar (Right Side) -->
            <aside class="stack" style="gap: 16px; position: sticky; top: 80px;">
              <!-- Order Summary -->
              <div class="card">
                <div class="card-head"><h3>Order summary</h3></div>
                <dl class="kv">
                  <dt v-for="(vendor, vendorId) in itemsByVendor" :key="vendorId">
                    {{ vendor.vendor_name }}
                    <span class="badge badge-tiny" :class="fulfillmentMethods[vendorId] === 'DELIVERY' ? 'badge-info' : 'badge-ok'" style="margin-left: 8px; font-size: 0.65rem;">
                      {{ fulfillmentMethods[vendorId] === 'DELIVERY' ? 'Delivery' : 'Pickup' }}
                    </span>
                  </dt>
                  <dd>{{ formatPrice(vendor.subtotal) }}</dd>
                </dl>
                <hr class="divider">
                <div v-if="hasDeliveryFee" class="kv" style="margin-top: 8px;">
                  <dt>Delivery fee ({{ deliveryVendorCount }} vendor{{ deliveryVendorCount > 1 ? 's' : '' }})</dt>
                  <dd>₱95.00</dd>
                </div>
                <div class="row-between" style="font-weight: 650; font-size: 1.1rem; margin-top: 8px;">
                  <span>Total</span>
                  <span class="price price-lg">{{ formatPrice(grandTotal) }}</span>
                </div>
                <div class="tiny muted mt8">
                  {{ vendorCount }} order{{ vendorCount > 1 ? 's' : '' }} · {{ pickupVendorCount }} for pickup, {{ deliveryVendorCount }} for delivery
                </div>
              </div>

              <!-- Payment Method Preview (read-only here, editable in checkout) -->
              <div class="card">
                <div class="card-head"><h3>Payment method</h3></div>
                <div class="opt on">
                  <input type="radio" name="pay-preview" checked disabled aria-label="GCash">
                  <span><span class="t">📱 GCash</span><span class="d">Pay online now · sandbox</span></span>
                </div>
                <div class="opt">
                  <input type="radio" name="pay-preview" disabled aria-label="Maya">
                  <span><span class="t">📱 Maya</span><span class="d">Pay online now · sandbox</span></span>
                </div>
                <div class="opt">
                  <input type="radio" name="pay-preview" disabled aria-label="Online banking">
                  <span><span class="t">🏦 Online banking</span><span class="d">Sandbox</span></span>
                </div>
                <div class="opt">
                  <input type="radio" name="pay-preview" disabled aria-label="Card">
                  <span><span class="t">💳 Card</span><span class="d">Sandbox · no card data is stored</span></span>
                </div>
                <div class="opt">
                  <input type="radio" name="pay-preview" disabled aria-label="Cash at pickup">
                  <span><span class="t">💵 Cash at pickup</span><span class="d">Pickup orders only</span></span>
                </div>
                <div class="note note-warn mt12 tiny">
                  Payments run in <strong>sandbox / test mode</strong>. No real money moves and no card details are stored.
                </div>
              </div>

              <!-- Delivery Partner Preview -->
              <div class="card">
                <div class="card-head"><h3>Delivery quote</h3></div>
                <label class="field">
                  <span>Partner</span>
                  <select class="input" aria-label="Delivery partner" disabled>
                    <option>Lalamove — ₱95.00</option>
                    <option>GrabExpress — ₱110.00</option>
                    <option>Maxim — ₱85.00</option>
                    <option>Local market rider — ₱60.00</option>
                  </select>
                </label>
                <dl class="kv">
                  <dt>Estimated time</dt><dd>45–60 min</dd>
                  <dt>Drop-off</dt><dd>Your saved address</dd>
                </dl>
                <div class="note mt12 tiny">Delivery is <strong>mocked</strong> in this project — the partner is simulated.</div>
              </div>

              <!-- Action Buttons -->
              <button
                @click="proceedToCheckout"
                class="btn btn-accent btn-lg btn-block"
                :disabled="cart.items.length === 0"
              >
                Proceed to checkout · {{ formatPrice(grandTotal) }}
              </button>
              <button
                @click="continueShopping"
                class="btn btn-block"
              >
                Continue shopping
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