# M4 · Hardening & Delivery

**Goal.** Finish Vue front-end integration, write tests, create performance/security/backup docs, rehearse the demo, and package for submission.

**Dates.** Dec 3 – Dec 12, 2026 (10 days — Dec 10–12 are buffer for rehearsal/packaging only)

**Steps.** M4.1 – M4.20 (20 steps)

---

## Step M4.1 — Vue: install deps and configure API base URL

**Goal.** Make sure the Vue 3 + Vite project can talk to the Django API.

**Where.** `frontend/`

**Actions.**

1. Open `frontend/package.json` and confirm these dependencies exist:
   - `axios` (for API calls)
   - `vue-router` (for navigation)
   - `pinia` (for state management — optional but recommended)

   If any are missing, install them:
   ```powershell
   npm install axios vue-router pinia
   ```

2. Create `frontend/src/services/api.js` — this is the Axios instance with the base URL and JWT interceptors:

   ```javascript
   import axios from 'axios'

   const api = axios.create({
     baseURL: 'http://localhost:8000/api/',
     timeout: 10000,
   })

   // Attach access token from localStorage to every request
   api.interceptors.request.use((config) => {
     const token = localStorage.getItem('access_token')
     if (token) {
       config.headers.Authorization = `Bearer ${token}`
     }
     return config
   })

   // Handle 401: try to refresh token, then retry once
   api.interceptors.response.use(
     (response) => response,
     async (error) => {
       const originalRequest = error.config
       if (error.response?.status === 401 && !originalRequest._retry) {
         originalRequest._retry = true
         try {
           const refresh = localStorage.getItem('refresh_token')
           const res = await axios.post('http://localhost:8000/api/auth/token/refresh/', {
             refresh,
           })
           localStorage.setItem('access_token', res.data.access)
           localStorage.setItem('refresh_token', res.data.refresh)
           originalRequest.headers.Authorization = `Bearer ${res.data.access}`
           return api(originalRequest)
         } catch (e) {
           localStorage.removeItem('access_token')
           localStorage.removeItem('refresh_token')
           window.location.href = '/login'
         }
       }
       return Promise.reject(error)
     }
   )

   export default api
   ```

3. Create `frontend/src/stores/auth.js` (Pinia store for auth state):

   ```javascript
   import { defineStore } from 'pinia'
   import api from '@/services/api'

   export const useAuthStore = defineStore('auth', {
     state: () => ({
       user: null,
       isAuthenticated: false,
     }),
     actions: {
       async login(username, password) {
         const res = await api.post('auth/token/', { username, password })
         localStorage.setItem('access_token', res.data.access)
         localStorage.setItem('refresh_token', res.data.refresh)
         this.isAuthenticated = true
         await this.fetchUser()
       },
       async fetchUser() {
         try {
           const res = await api.get('auth/user/') // We'll add this endpoint in M4.2
           this.user = res.data
         } catch (e) {
           this.logout()
         }
       },
       logout() {
         localStorage.removeItem('access_token')
         localStorage.removeItem('refresh_token')
         this.user = null
         this.isAuthenticated = false
       },
       async init() {
         const token = localStorage.getItem('access_token')
         if (token) {
           this.isAuthenticated = true
           await this.fetchUser()
         }
       },
     },
   })
   ```

4. Update `frontend/src/main.js` to initialize the auth store on app start:

   ```javascript
   import { createApp } from 'vue'
   import { createPinia } from 'pinia'
   import App from './App.vue'
   import router from './router'
   import './style.css'
   import { useAuthStore } from './stores/auth'

   const app = createApp(App)
   const pinia = createPinia()
   app.use(pinia)
   app.use(router)

   // Initialize auth from localStorage
   const authStore = useAuthStore()
   await authStore.init()

   app.mount('#app')
   ```

**Expected result.** Frontend has an Axios instance with JWT handling, a Pinia auth store, and initializes auth on startup.

**Verify.** `npm run dev` → no console errors; open DevTools → Application → Local Storage → (empty until login).

**If it fails.**
- Check `baseURL` in `api.js` matches your Django port (default 8000).
- CORS errors → verify `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py` includes `http://localhost:5173`.

---

## Step M4.2 — Backend: add `/api/auth/user/` endpoint for current user

**Goal.** Provide an endpoint so the frontend can fetch the logged-in user's profile.

**Where.** `backend/accounts/`

**Actions.**

1. Create `backend/accounts/serializers.py` (if not exists) and add a `CurrentUserSerializer`:

   ```python
   from rest_framework import serializers
   from accounts.models import AuthUser, Userprofile, Customerprofile, Vendor

   class CurrentUserSerializer(serializers.ModelSerializer):
       profile = serializers.SerializerMethodField()
       role = serializers.SerializerMethodField()

       class Meta:
           model = AuthUser
           fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'profile']

       def get_role(self, obj):
           if hasattr(obj, 'vendor') and obj.vendor:
               return 'vendor'
           if hasattr(obj, 'customerprofile'):
               return 'customer'
           return 'customer'

       def get_profile(self, obj):
           if hasattr(obj, 'vendor') and obj.vendor:
               return {
                   'id': obj.vendor.id,
                   'name': obj.vendor.name,
                   'stall_location': obj.vendor.stall_location,
               }
           if hasattr(obj, 'customerprofile'):
               return {
                   'id': obj.customerprofile.id,
                   'phone': obj.customerprofile.phone,
                   'address': obj.customerprofile.address,
               }
           return None
   ```

2. Add the view in `backend/accounts/views.py`:

   ```python
   from rest_framework import generics, permissions
   from rest_framework.response import Response
   from accounts.serializers import CurrentUserSerializer

   class CurrentUserView(generics.RetrieveAPIView):
       permission_classes = [permissions.IsAuthenticated]
       serializer_class = CurrentUserSerializer

       def get_object(self):
           return self.request.user
   ```

3. Wire it in `backend/accounts/urls.py`:

   ```python
   from django.urls import path
   from accounts.views import CurrentUserView

   urlpatterns = [
       path('auth/user/', CurrentUserView.as_view(), name='current-user'),
   ]
   ```

4. Include accounts URLs in `backend/config/urls.py` (add to urlpatterns):
   ```python
   path('api/accounts/', include('accounts.urls')),
   ```

**Expected result.** `GET /api/accounts/auth/user/` returns the current user with role and profile.

**Verify.** 
```powershell
# Get a token first
curl -X POST http://localhost:8000/api/auth/token/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"Admin2627\"}"
# Use the access token
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/accounts/auth/user/
```
Should return JSON with `id`, `username`, `email`, `role`, `profile`.

**If it fails.** Check `accounts/urls.py` is included in `config/urls.py`; verify serializer imports match your model names.

---

## Step M4.3 — Vue: Login screen and route guard

**Goal.** Build a login page and protect routes that require authentication.

**Where.** `frontend/src/`

**Actions.**

1. Create `frontend/src/views/LoginView.vue`:

   ```vue
   <script setup>
   import { ref } from 'vue'
   import { useRouter } from 'vue-router'
   import { useAuthStore } from '@/stores/auth'

   const router = useRouter()
   const authStore = useAuthStore()

   const username = ref('')
   const password = ref('')
   const error = ref('')
   const loading = ref(false)

   const handleLogin = async () => {
     loading.value = true
     error.value = ''
     try {
       await authStore.login(username.value, password.value)
       router.push('/cart')
     } catch (e) {
       error.value = 'Invalid credentials'
     } finally {
       loading.value = false
     }
   }
   </script>

   <template>
     <div class="min-h-screen flex items-center justify-center bg-gray-50">
       <div class="w-full max-w-md p-8 bg-white rounded-lg shadow">
         <h1 class="text-2xl font-bold mb-6 text-center">E-Compra Login</h1>
         <div v-if="error" class="mb-4 p-3 bg-red-50 text-red-600 rounded">{{ error }}</div>
         <div class="mb-4">
           <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
           <input v-model="username" type="text" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" />
         </div>
         <div class="mb-6">
           <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
           <input v-model="password" type="password" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" />
         </div>
         <button @click="handleLogin" :disabled="loading" class="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50">
           {{ loading ? 'Logging in...' : 'Login' }}
         </button>
       </div>
     </div>
   </template>
   ```

2. Update `frontend/src/router/index.js` to add login route and a navigation guard:

   ```javascript
   import { createRouter, createWebHistory } from 'vue-router'
   import { useAuthStore } from '@/stores/auth'
   import CartView from '@/views/CartView.vue'
   import CheckoutView from '@/views/CheckoutView.vue'
   import PaymentView from '@/views/PaymentView.vue'
   import VendorPOSView from '@/views/VendorPOSView.vue'
   import LoginView from '@/views/LoginView.vue'

   const routes = [
     { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
     { path: '/cart', name: 'cart', component: CartView, meta: { requiresAuth: true } },
     { path: '/checkout', name: 'checkout', component: CheckoutView, meta: { requiresAuth: true } },
     { path: '/payment/:id?', name: 'payment', component: PaymentView, props: true, meta: { requiresAuth: true } },
     { path: '/vendor/pos', name: 'vendor-pos', component: VendorPOSView, meta: { requiresAuth: true, role: 'vendor' } },
     { path: '/', redirect: '/cart' },
   ]

   const router = createRouter({
     history: createWebHistory(),
     routes,
   })

   router.beforeEach(async (to, from, next) => {
     const authStore = useAuthStore()
     
     // Initialize auth if not done yet
     if (!authStore._initialized) {
       await authStore.init()
       authStore._initialized = true
     }

     if (to.meta.public) {
       return next()
     }

     if (to.meta.requiresAuth && !authStore.isAuthenticated) {
       return next({ name: 'login', query: { redirect: to.fullPath } })
     }

     if (to.meta.role === 'vendor' && authStore.user?.role !== 'vendor') {
       return next({ name: 'cart' })
     }

     next()
   })

   export default router
   ```

3. Update `frontend/src/App.vue` to show the router view:

   ```vue
   <script setup>
   import { onMounted } from 'vue'
   import { useRouter } from 'vue-router'
   import { useAuthStore } from '@/stores/auth'
   import api from '@/services/api'

   const router = useRouter()
   const authStore = useAuthStore()

   onMounted(async () => {
     await authStore.init()
   })
   </script>

   <template>
     <router-view />
   </template>
   ```

**Expected result.** Login page at `/login`; unauthenticated users redirected to login; vendor-only routes protected.

**Verify.** `npm run dev` → visit `http://localhost:5173` → redirects to `/login`; login with `admin`/`Admin2627` → redirects to `/cart`.

**If it fails.**
- Check `authStore._initialized` pattern prevents double-initialization.
- Vue Router guard runs before `authStore.init()` completes → the `await authStore.init()` in `onMounted` plus the guard's `await authStore.init()` handles this.

---

## Step M4.4 — Vue: Catalog browse screen (product list + search)

**Goal.** Build the main product browsing screen with search and category filters.

**Where.** `frontend/src/views/CatalogView.vue`

**Actions.**

1. Create `frontend/src/views/CatalogView.vue`:

   ```vue
   <script setup>
   import { ref, onMounted, computed } from 'vue'
   import { useRouter } from 'vue-router'
   import api from '@/services/api'

   const router = useRouter()

   const products = ref([])
   const categories = ref([])
   const loading = ref(false)
   const search = ref('')
   const selectedCategory = ref('')
   const page = ref(1)
   const pageSize = 20
   const totalCount = ref(0)

   const fetchProducts = async () => {
     loading.value = true
     try {
       const params = new URLSearchParams()
       if (search.value) params.append('q', search.value)
       if (selectedCategory.value) params.append('category', selectedCategory.value)
       params.append('page', page.value)
       params.append('page_size', pageSize)
       
       const res = await api.get(`catalog/products/?${params.toString()}`)
       products.value = res.data.results || res.data
       totalCount.value = res.data.count || products.value.length
     } catch (e) {
       console.error('Failed to fetch products:', e)
     } finally {
       loading.value = false
     }
   }

   const fetchCategories = async () => {
     try {
       const res = await api.get('catalog/categories/')
       categories.value = res.data.results || res.data
     } catch (e) {
       console.error('Failed to fetch categories:', e)
     }
   }

   const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

   const goToProduct = (product) => {
     router.push({ name: 'product-detail', params: { id: product.id } })
   }

   const addToCart = async (product) => {
     try {
       await api.post('cart/add/', { product_id: product.id, quantity: 1 })
       alert('Added to cart!')
     } catch (e) {
       alert('Failed to add to cart')
     }
   }

   onMounted(() => {
     fetchProducts()
     fetchCategories()
   })
   </script>

   <template>
     <div class="min-h-screen bg-gray-50">
       <!-- Header -->
       <header class="bg-white shadow-sm sticky top-0 z-10">
         <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
           <h1 class="text-xl font-bold text-purple-600">E-Compra</h1>
           <router-link to="/cart" class="text-sm text-gray-600 hover:text-purple-600">🛒 Cart</router-link>
         </div>
       </header>

       <!-- Search & Filters -->
       <div class="max-w-7xl mx-auto px-4 py-4">
         <div class="flex flex-col md:flex-row gap-4 mb-6">
           <div class="flex-1">
             <input 
               v-model="search" 
               @keyup.enter="page = 1; fetchProducts()"
               placeholder="Search products..." 
               class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
             />
           </div>
           <select 
             v-model="selectedCategory" 
             @change="page = 1; fetchProducts()"
             class="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
           >
             <option value="">All Categories</option>
             <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
           </select>
         </div>
       </div>

       <!-- Product Grid -->
       <main class="max-w-7xl mx-auto px-4 pb-8">
         <div v-if="loading" class="text-center py-12">Loading...</div>
         
         <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
           <div v-for="product in products" :key="product.id" 
                @click="goToProduct(product)" 
                class="bg-white rounded-lg shadow hover:shadow-md transition cursor-pointer overflow-hidden">
             <div class="aspect-square bg-gray-100">
               <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="w-full h-full object-cover" />
               <div v-else class="w-full h-full flex items-center justify-center text-gray-400">No Image</div>
             </div>
             <div class="p-4">
               <h3 class="font-medium text-gray-900 line-clamp-2 mb-1">{{ product.name }}</h3>
               <p class="text-purple-600 font-bold mb-2">{{ formatPrice(product.price) }} / {{ product.unit_code }}</p>
               <p class="text-xs text-gray-500 mb-2">{{ product.vendor_name }} • {{ product.stall_location }}</p>
               <div class="flex items-center justify-between">
                 <span :class="product.availability_code === 'IN_STOCK' ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
                   {{ product.availability_code === 'IN_STOCK' ? 'In Stock' : 'Out of Stock' }}
                 </span>
                 <button 
                   @click.stop="addToCart(product)"
                   :disabled="product.availability_code !== 'IN_STOCK'"
                   class="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 disabled:bg-gray-300"
                 >
                   Add
                 </button>
               </div>
             </div>
           </div>
         </div>

         <!-- Pagination -->
         <div v-if="totalCount > pageSize" class="flex justify-center gap-2 mt-6">
           <button @click="page > 1 && (page--, fetchProducts())" :disabled="page === 1" class="px-4 py-2 border rounded disabled:opacity-50">Previous</button>
           <span class="flex items-center px-4">Page {{ page }}</span>
           <button @click="page * pageSize < totalCount && (page++, fetchProducts())" :disabled="page * pageSize >= totalCount" class="px-4 py-2 border rounded disabled:opacity-50">Next</button>
         </div>
       </main>
     </div>
   </template>
   ```

2. Add the route in `frontend/src/router/index.js`:
   ```javascript
   import CatalogView from '@/views/CatalogView.vue'
   // Add to routes:
   { path: '/catalog', name: 'catalog', component: CatalogView, meta: { requiresAuth: true } },
   ```

3. Update the redirect in router from `/cart` to `/catalog` so users land on the catalog first.

**Expected result.** Catalog page with search, category filter, product cards showing price/vendor/availability, add-to-cart button, pagination.

**Verify.** `npm run dev` → visit `/catalog` → see products, search works, category filter works, add to cart shows alert.

**If it fails.**
- API returns paginated response with `results` and `count` — adjust if your DRF pagination is different.
- Check `product.unit_code` and `product.vendor_name` match serializer field names.

---

## Step M4.5 — Vue: Product detail screen

**Goal.** Build a product detail page with image, description, vendor info, and quantity selector.

**Where.** `frontend/src/views/ProductDetailView.vue`

**Actions.**

1. Create `frontend/src/views/ProductDetailView.vue`:

   ```vue
   <script setup>
   import { ref, onMounted } from 'vue'
   import { useRoute, useRouter } from 'vue-router'
   import api from '@/services/api'

   const route = useRoute()
   const router = useRouter()

   const product = ref(null)
   const loading = ref(true)
   const quantity = ref(1)
   const error = ref('')

   const fetchProduct = async () => {
     try {
       const res = await api.get(`catalog/products/${route.params.id}/`)
       product.value = res.data
     } catch (e) {
       error.value = 'Product not found'
     } finally {
       loading.value = false
     }
   }

   const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

   const addToCart = async () => {
     try {
       await api.post('cart/add/', { product_id: product.value.id, quantity: quantity.value })
       alert(`Added ${quantity.value} to cart!`)
       quantity.value = 1
     } catch (e) {
       alert('Failed to add to cart')
     }
   }

   const reserveForPickup = async () => {
     // This will call checkout with pickup fulfillment
     router.push({ name: 'checkout', query: { product_id: product.value.id, quantity: quantity.value, fulfillment: 'PICKUP' } })
   }

   onMounted(fetchProduct)
   </script>

   <template>
     <div class="min-h-screen bg-gray-50">
       <header class="bg-white shadow-sm sticky top-0 z-10">
         <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
           <router-link to="/catalog" class="text-gray-600 hover:text-purple-600">← Back</router-link>
           <h1 class="text-xl font-bold text-purple-600">Product Details</h1>
           <router-link to="/cart" class="text-sm text-gray-600 hover:text-purple-600">🛒 Cart</router-link>
         </div>
       </header>

       <div v-if="loading" class="max-w-7xl mx-auto px-4 py-12 text-center">Loading...</div>
       <div v-else-if="error" class="max-w-7xl mx-auto px-4 py-12 text-center text-red-600">{{ error }}</div>
       <div v-else-if="product" class="max-w-7xl mx-auto px-4 py-8">
         <div class="grid md:grid-cols-2 gap-8">
           <!-- Image Gallery -->
           <div>
             <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-4">
               <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="w-full h-full object-cover" />
               <div v-else class="w-full h-full flex items-center justify-center text-gray-400">No Image</div>
             </div>
           </div>

           <!-- Details -->
           <div>
             <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
             <p class="text-purple-600 text-2xl font-bold mb-4">{{ formatPrice(product.price) }} <span class="text-gray-500 font-normal text-lg">/ {{ product.unit_code }}</span></p>
             
             <div class="mb-4">
               <span :class="product.availability_code === 'IN_STOCK' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="px-3 py-1 rounded-full text-sm font-medium">
                 {{ product.availability_code === 'IN_STOCK' ? 'In Stock' : 'Out of Stock' }}
               </span>
             </div>

             <p class="text-gray-600 mb-6">{{ product.description }}</p>

             <div class="bg-gray-50 p-4 rounded-lg mb-6">
               <h3 class="font-medium text-gray-900 mb-2">Vendor Information</h3>
               <p class="text-gray-600">{{ product.vendor_name }}</p>
               <p class="text-gray-500 text-sm">Stall: {{ product.stall_location }}</p>
               <p class="text-gray-500 text-sm">Section: {{ product.market_section }}</p>
             </div>

             <div class="flex gap-4">
               <div class="flex-1">
                 <label class="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                 <input v-model.number="quantity" type="number" min="1" :max="product.stock_quantity" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" />
               </div>
             </div>

             <div class="flex gap-4 mt-6">
               <button @click="addToCart" :disabled="product.availability_code !== 'IN_STOCK'" class="flex-1 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 font-medium">
                 Add to Cart
               </button>
               <button @click="reserveForPickup" :disabled="product.availability_code !== 'IN_STOCK'" class="flex-1 py-3 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 disabled:opacity-50 font-medium">
                 Reserve for Pickup
               </button>
             </div>
           </div>
         </div>
       </div>
     </div>
   </template>
   ```

2. Add the route in `frontend/src/router/index.js`:
   ```javascript
   import ProductDetailView from '@/views/ProductDetailView.vue'
   // Add to routes:
   { path: '/product/:id', name: 'product-detail', component: ProductDetailView, meta: { requiresAuth: true } },
   ```

**Expected result.** Product detail page with image, price, description, vendor info, quantity selector, add-to-cart and reserve-for-pickup buttons.

**Verify.** `npm run dev` → click a product from catalog → see detail page → add to cart works.

**If it fails.** Check route param `:id` matches `route.params.id`; verify serializer includes `vendor_name`, `stall_location`, `market_section`, `stock_quantity`.

---

## Step M4.6 — Vue: Cart screen (already built in M3.13, verify integration)

**Goal.** Ensure the existing CartView.vue works with the new auth/API setup.

**Where.** `frontend/src/views/CartView.vue`

**Actions.**

1. Open `frontend/src/views/CartView.vue` and update the API calls to use the new `api` service (should already be using it from M3.13).

2. Verify the cart loads on mount, shows items with vendor grouping, and the "Proceed to Checkout" button navigates to `/checkout`.

3. If the cart was using a different API pattern, update it to match the new `api.js` service.

**Expected result.** Cart screen shows items grouped by vendor, update/remove quantity works, checkout button works.

**Verify.** `npm run dev` → add items from catalog → visit `/cart` → see items → update quantity → proceed to checkout.

**If it fails.** Check `api.js` baseURL and auth interceptors; verify CartView uses the correct endpoint `/api/cart/`.

---

## Step M4.7 — Vue: Checkout screen (already built in M3.14, verify integration)

**Goal.** Ensure CheckoutView.vue works with the new auth/API setup and calls `/api/checkout/`.

**Where.** `frontend/src/views/CheckoutView.vue`

**Actions.**

1. Open `frontend/src/views/CheckoutView.vue` and verify:
   - It calls `api.post('checkout/')` on submit
   - It handles the response with `order_ids` array
   - It redirects to payment screen with the first order_id (or lets user pick)

2. Update fulfillment method selection (Delivery vs Pickup) if not already present.

**Expected result.** Checkout screen shows vendor-grouped order summary, fulfillment choice, submit creates orders, redirects to payment.

**Verify.** `npm run dev` → cart with items → `/checkout` → select fulfillment → place order → redirects to payment.

**If it fails.** Check `/api/checkout/` endpoint exists in Django; verify response format matches frontend expectations.

---

## Step M4.8 — Vue: Payment screen (already built in M3.15, verify integration)

**Goal.** Ensure PaymentView.vue works with the new auth/API setup.

**Where.** `frontend/src/views/PaymentView.vue`

**Actions.**

1. Open `frontend/src/views/PaymentView.vue` and verify:
   - It accepts `order_id` from route params or query
   - It shows payment method selection (GCash, Maya, Card, etc.)
   - On submit, calls `api.post('payment/')` with transaction_id, provider, amount
   - Shows success/failure states

**Expected result.** Payment screen lets user select method, submit payment, shows confirmation.

**Verify.** `npm run dev` → complete checkout → `/payment/:id` → select method → submit → success.

**If it fails.** Check `/api/payment/` endpoint; verify it expects `transaction_id`, `provider`, `provider_reference`, `amount`.

---

## Step M4.9 — Vue: Vendor POS screen (already built in M3.16, verify integration)

**Goal.** Ensure VendorPOSView.vue works with the new auth/API setup.

**Where.** `frontend/src/views/VendorPOSView.vue`

**Actions.**

1. Open `frontend/src/views/VendorPOSView.vue` and verify:
   - It loads vendor's orders on mount via `GET /api/vendors/pos/`
   - Status update buttons call `POST /api/vendors/pos/` with `order_id` and `status_code`
   - Only shows orders for the logged-in vendor (role check)
   - Handles transition validation errors (400 responses)

**Expected result.** Vendor POS shows order queue with status badges, update buttons work, invalid transitions show error.

**Verify.** `npm run dev` → login as vendor user → `/vendor/pos` → see orders → update status.

**If it fails.** Check vendor user has a Vendor profile linked; verify `request.user.vendor` works in Django view.

---

## Step M4.10 — Vue: Order tracking screen

**Goal.** Build an order tracking page showing status timeline for customer orders.

**Where.** `frontend/src/views/OrderTrackingView.vue`

**Actions.**

1. Create `frontend/src/views/OrderTrackingView.vue`:

   ```vue
   <script setup>
   import { ref, onMounted, computed } from 'vue'
   import { useRoute, useRouter } from 'vue-router'
   import api from '@/services/api'

   const route = useRoute()
   const router = useRouter()

   const order = ref(null)
   const loading = ref(true)
   const error = ref('')

   const statusSteps = [
     { code: 'PENDING_PAYMENT', label: 'Pending Payment', icon: '⏳' },
     { code: 'CONFIRMED', label: 'Confirmed', icon: '✅' },
     { code: 'PREPARING', label: 'Preparing', icon: '📦' },
     { code: 'READY_FOR_PICKUP', label: 'Ready for Pickup', icon: '🔔' },
     { code: 'OUT_FOR_DELIVERY', label: 'Out for Delivery', icon: '🚚' },
     { code: 'COMPLETED', label: 'Completed', icon: '🎉' },
   ]

   const fetchOrder = async () => {
     try {
       const res = await api.get(`orders/${route.params.id}/`)
       order.value = res.data
     } catch (e) {
       error.value = 'Order not found'
     } finally {
       loading.value = false
     }
   }

   const getCurrentStepIndex = () => {
     if (!order.value?.status_code) return -1
     return statusSteps.findIndex(s => s.code === order.value.status_code)
   }

   onMounted(fetchOrder)
   </script>

   <template>
     <div class="min-h-screen bg-gray-50">
       <header class="bg-white shadow-sm sticky top-0 z-10">
         <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
           <router-link to="/catalog" class="text-gray-600 hover:text-purple-600">← Back</router-link>
           <h1 class="text-xl font-bold text-purple-600">Order Tracking</h1>
         </div>
       </header>

       <div v-if="loading" class="max-w-7xl mx-auto px-4 py-12 text-center">Loading...</div>
       <div v-else-if="error" class="max-w-7xl mx-auto px-4 py-12 text-center text-red-600">{{ error }}</div>
       <div v-else-if="order" class="max-w-7xl mx-auto px-4 py-8">
         <div class="bg-white rounded-lg shadow p-6 mb-6">
           <div class="flex justify-between items-start mb-4">
             <div>
               <h2 class="text-xl font-bold">Order #{{ order.id }}</h2>
               <p class="text-gray-500">{{ order.created_at }}</p>
             </div>
             <span :class="order.status_code === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'" class="px-3 py-1 rounded-full text-sm font-medium">
               {{ order.status_display || order.status_code }}
             </span>
           </div>
           <div class="grid grid-cols-2 gap-4 text-sm">
             <div><span class="text-gray-500">Vendor:</span> {{ order.vendor_name }}</div>
             <div><span class="text-gray-500">Fulfillment:</span> {{ order.fulfillment_display }}</div>
             <div><span class="text-gray-500">Total:</span> <span class="font-bold text-purple-600">₱{{ order.total_amount }}</span></div>
           </div>
         </div>

         <!-- Status Timeline -->
         <div class="bg-white rounded-lg shadow p-6">
           <h3 class="text-lg font-bold mb-6">Status Timeline</h3>
           <div class="relative">
             <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />
             <div v-for="(step, index) in statusSteps" :key="step.code" class="relative pl-14 mb-6 last:mb-0">
               <div class="absolute left-6 top-1 w-3 h-3 rounded-full border-2"
                    :class="index <= getCurrentStepIndex() ? 'bg-purple-600 border-purple-600' : 'bg-white border-gray-300'">
                 <span v-if="index <= getCurrentStepIndex()" class="absolute inset-0 flex items-center justify-center text-white text-xs">✓</span>
               </div>
               <div class="pb-4">
                 <p class="font-medium" :class="index <= getCurrentStepIndex() ? 'text-purple-600' : 'text-gray-500'">
                   {{ step.icon }} {{ step.label }}
                 </p>
               </div>
             </div>
           </div>
         </div>

         <!-- Order Items -->
         <div class="mt-6 bg-white rounded-lg shadow p-6">
           <h3 class="text-lg font-bold mb-4">Items</h3>
           <div v-for="item in order.items" :key="item.id" class="flex justify-between py-2 border-b last:border-0">
             <div>
               <p class="font-medium">{{ item.product_name }}</p>
               <p class="text-sm text-gray-500">Qty: {{ item.quantity }} × ₱{{ item.unit_price }}</p>
             </div>
             <p class="font-medium">₱{{ item.quantity * item.unit_price }}</p>
           </div>
           <div class="flex justify-between pt-4 font-bold text-lg">
             <span>Total</span>
             <span>₱{{ order.total_amount }}</span>
           </div>
         </div>
       </div>
     </div>
   </template>
   ```

2. Add the route in `frontend/src/router/index.js`:
   ```javascript
   import OrderTrackingView from '@/views/OrderTrackingView.vue'
   // Add to routes:
   { path: '/order/:id', name: 'order-tracking', component: OrderTrackingView, meta: { requiresAuth: true } },
   ```

**Expected result.** Order tracking page with visual timeline, order details, items, current status highlighted.

**Verify.** `npm run dev` → place an order → visit `/order/:id` → see timeline with current status highlighted.

**If it fails.** Check `/api/orders/{id}/` endpoint returns nested items and status_display.

---

## Step M4.11 — Unit tests: Backend (pytest) + Frontend (Vitest)

**Goal.** Add unit tests for critical backend services and frontend components.

**Where.** `backend/` and `frontend/`

**Actions.**

1. **Backend: Add more test coverage**

   Create `backend/orders/test_services.py` for service layer tests:

   ```python
   import pytest
   from orders.services import transition_order_status, checkout_cart
   from orders.models import TransactionStatus

   @pytest.mark.django_db
   def test_transition_order_status_valid(user, vendor, product):
       from orders.models import Order, FulfillmentMethod, TransactionType, Transaction
       order = Order.objects.create(
           user=user, vendor=vendor,
           status_code=TransactionStatus.objects.get(code="PENDING_PAYMENT"),
           fulfillment_code=FulfillmentMethod.objects.get(code="DELIVERY"),
           total_amount=100, notes=""
       )
       Transaction.objects.create(order=order, transaction_type=TransactionType.objects.get(code="ONLINE_ORDER"), reference_no=f"TXN-{order.id}")
       
       order = transition_order_status(order, "CONFIRMED")
       assert order.status_code.code == "CONFIRMED"
       
       order = transition_order_status(order, "PREPARING")
       assert order.status_code.code == "PREPARING"

   @pytest.mark.django_db
   def test_transition_order_status_invalid(user, vendor, product):
       from orders.models import Order, FulfillmentMethod, TransactionType, Transaction
       order = Order.objects.create(
           user=user, vendor=vendor,
           status_code=TransactionStatus.objects.get(code="PENDING_PAYMENT"),
           fulfillment_code=FulfillmentMethod.objects.get(code="DELIVERY"),
           total_amount=100, notes=""
       )
       Transaction.objects.create(order=order, transaction_type=TransactionType.objects.get(code="ONLINE_ORDER"), reference_no=f"TXN-{order.id}")
       
       with pytest.raises(ValueError):
           transition_order_status(order, "OUT_FOR_DELIVERY")  # Skip CONFIRMED, PREPARING

   @pytest.mark.django_db
   def test_checkout_cart_splits_by_vendor(user, multi_vendor_cart):
       order_ids = checkout_cart(user)
       assert len(order_ids) == len(multi_vendor_cart)
       # Verify each order belongs to a different vendor
       vendor_ids = set()
       for oid in order_ids:
           from orders.models import Order
           vendor_ids.add(Order.objects.get(id=oid).vendor_id)
       assert len(vendor_ids) == len(multi_vendor_cart)
   ```

2. **Frontend: Install Vitest and add component tests**

   ```powershell
   cd frontend
   npm install -D vitest @vue/test-utils jsdom
   ```

   Create `frontend/vitest.config.js`:
   ```javascript
   import { defineConfig } from 'vitest/config'
   import vue from '@vitejs/plugin-vue'

   export default defineConfig({
     plugins: [vue()],
     test: {
       environment: 'jsdom',
       globals: true,
     },
   })
   ```

   Add test script to `package.json`:
   ```json
   "test": "vitest run"
   ```

   Create `frontend/src/stores/__tests__/auth.test.js`:
   ```javascript
   import { describe, it, expect, vi, beforeEach } from 'vitest'
   import { setActivePinia, createPinia } from 'pinia'
   import { useAuthStore } from '@/stores/auth'

   describe('Auth Store', () => {
     beforeEach(() => {
       setActivePinia(createPinia())
       localStorage.clear()
       vi.resetAllMocks()
     })

     it('initializes with no user', () => {
       const store = useAuthStore()
       expect(store.isAuthenticated).toBe(false)
       expect(store.user).toBeNull()
     })

     it('sets tokens on login', async () => {
       const store = useAuthStore()
       // Mock api.post
       vi.spyOn(store, 'login').mockResolvedValue()
       await store.login('test', 'pass')
       // Note: actual login test would mock axios
     })
   })
   ```

**Expected result.** Backend tests cover service layer transitions and checkout logic; frontend has test runner configured.

**Verify.** 
```powershell
cd backend && pytest -v
cd frontend && npm test
```

**If it fails.**
- Backend: Check fixtures in `conftest.py` provide needed objects.
- Frontend: Vitest config may need `transform` for Vue SFCs — add `@vitejs/plugin-vue` to test config.

---

## Step M4.12 — End-to-end tests: Key user flows

**Goal.** Write Playwright tests for critical user journeys.

**Where.** `frontend/`

**Actions.**

1. Install Playwright:
   ```powershell
   cd frontend
   npm install -D @playwright/test
   npx playwright install chromium
   ```

2. Create `frontend/playwright.config.js`:
   ```javascript
   import { defineConfig, devices } from '@playwright/test'

   export default defineConfig({
     testDir: './e2e',
     fullyParallel: true,
     reporter: 'html',
     use: {
       baseURL: 'http://localhost:5173',
       trace: 'on-first-retry',
     },
     projects: [
       { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
       { name: 'mobile', use: { ...devices['Pixel 5'] } },
     ],
     webServer: {
       command: 'npm run dev',
       url: 'http://localhost:5173',
       reuseExistingServer: !process.env.CI,
       timeout: 120000,
     },
   })
   ```

3. Create `frontend/e2e/customer-journey.spec.js`:
   ```javascript
   import { test, expect } from '@playwright/test'

   test.describe('Customer Journey', () => {
     test.beforeEach(async ({ page }) => {
       await page.goto('/login')
       await page.fill('input[type="text"]', 'admin')
       await page.fill('input[type="password"]', 'Admin2627')
       await page.click('button:has-text("Login")')
       await expect(page).toHaveURL('/catalog')
     })

     test('browse catalog, add to cart, checkout', async ({ page }) => {
       // Search for a product
       await page.fill('input[placeholder="Search products..."]', 'Tomato')
       await page.press('input[placeholder="Search products..."]', 'Enter')
       await expect(page.locator('text=Tomato')).toBeVisible()

       // Add first product to cart
       await page.click('button:has-text("Add") >> nth=0')
       await expect(page.locator('text=Added to cart!')).toBeVisible()

       // Go to cart
       await page.click('text=🛒 Cart')
       await expect(page.locator('text=Tomato')).toBeVisible()

       // Proceed to checkout
       await page.click('button:has-text("Proceed to Checkout")')
       await expect(page).toHaveURL('/checkout')

       // Select fulfillment and place order
       await page.click('button:has-text("Place Order")')
       await expect(page).toHaveURL(/\/payment\//)
     })
   })
   ```

**Expected result.** Playwright configured with at least one E2E test covering catalog → cart → checkout.

**Verify.** 
```powershell
cd frontend && npm run dev &
npx playwright test
```

**If it fails.**
- Ensure dev server is running before tests.
- Adjust selectors to match actual rendered HTML.
- Increase timeouts for slow CI environments.

---

## Step M4.13 — Indexing: Create composite indexes and run EXPLAIN analysis

**Goal.** Add database indexes for query performance and document findings.

**Where.** `backend/sql/` and `backend/`

**Actions.**

1. Create `backend/sql/04_performance_indexes.sql` with composite indexes based on query patterns:

   ```sql
   -- Catalog search: products by category + price + availability
   CREATE INDEX idx_product_cat_avail_price ON catalog_product (category_id, availability_code, price);
   
   -- Catalog search: products by vendor + availability
   CREATE INDEX idx_product_vendor_avail ON catalog_product (vendor_id, availability_code);
   
   -- Orders: user's orders by date
   CREATE INDEX idx_order_user_created ON orders_order (user_id, created_at DESC);
   
   -- Orders: vendor's orders by status + date
   CREATE INDEX idx_order_vendor_status_created ON orders_order (vendor_id, status_code, created_at DESC);
   
   -- Cart items: user's cart
   CREATE INDEX idx_cartitem_cart ON cart_cartitem (cart_id);
   
   -- Payments: by transaction
   CREATE INDEX idx_payment_transaction ON orders_payment (transaction_id);
   
   -- Inventory movements: by product + date
   CREATE INDEX idx_inventory_product_created ON catalog_inventorymovement (product_id, created_at DESC);
   
   -- Favorites: user's favorites
   CREATE INDEX idx_favorite_user ON favorites_favoriteproduct (user_id);
   ```

2. Run the indexes:
   ```powershell
   mysql -u root -pAdmin2627 ecompra < sql/04_performance_indexes.sql
   ```

3. Create `backend/docs/PERFORMANCE.md` with EXPLAIN analysis:

   ```markdown
   # E-Compra Performance Analysis

   ## Methodology
   Ran `EXPLAIN ANALYZE` on key queries against MySQL 8.4 with seeded data (34 products, 6 vendors, 9 categories).

   ## Key Queries

   ### 1. Product search by category and availability
   ```sql
   EXPLAIN ANALYZE 
   SELECT * FROM catalog_product 
   WHERE category_id = 1 AND availability_code = 'IN_STOCK' 
   ORDER BY price LIMIT 20;
   ```
   **Before indexes:** Full table scan (rows=34, filtered=100%)
   **After indexes:** Index range scan on `idx_product_cat_avail_price` (rows=5, filtered=100%)

   ### 2. Vendor's orders by status
   ```sql
   EXPLAIN ANALYZE 
   SELECT * FROM orders_order 
   WHERE vendor_id = 1 AND status_code = 'CONFIRMED' 
   ORDER BY created_at DESC LIMIT 20;
   ```
   **Before indexes:** Full table scan (rows=3)
   **After indexes:** Index range scan on `idx_order_vendor_status_created` (rows=1)

   ### 3. User's cart items
   ```sql
   EXPLAIN ANALYZE 
   SELECT * FROM cart_cartitem WHERE cart_id = 1;
   ```
   **After index `idx_cartitem_cart`:** Ref access (rows=2)

   ## Recommendations
   - Monitor slow query log in production
   - Consider covering indexes for frequently selected columns
   - Partition large tables (orders, inventory_movements) by date if they grow beyond 1M rows
   ```

**Expected result.** Indexes created; PERFORMANCE.md documents before/after EXPLAIN output.

**Verify.** 
```powershell
mysql -u root -pAdmin2627 ecompra < sql/04_performance_indexes.sql
# Check indexes exist
mysql -u root -pAdmin2627 -e "SHOW INDEX FROM catalog_product" ecompra
```

**If it fails.** Check index names don't conflict; verify column names match actual schema (`availability_code` not `availability`).

---

## Step M4.14 — Security review: Document security measures

**Goal.** Create a security audit document covering all OWASP Top 10 relevant items.

**Where.** `backend/docs/SECURITY.md`

**Actions.**

1. Create `backend/docs/SECURITY.md`:

   ```markdown
   # E-Compra Security Audit

   ## Authentication & Authorization
   - **JWT Tokens**: Short-lived access tokens (60 min), rotating refresh tokens (7 days) with blacklist
   - **Password Hashing**: Django's PBKDF2 with SHA-256 (default)
   - **Role-Based Access**: Customer / Vendor / Admin roles enforced at view level
   - **Object-Level Permissions**: Vendors can only access their own orders/Products

   ## Input Validation & Injection Prevention
   - **ORM Parameterization**: All queries via Django ORM — no raw SQL in views
   - **Serializer Validation**: DRF serializers validate all input fields
   - **FK Lookups**: Status transitions use `Model.objects.get(code=...)` — no string interpolation

   ## Data Protection
   - **No Card Data Stored**: Payment records only store provider reference, not PAN/CVV
   - **HTTPS Enforced**: Production uses TLS 1.2+ (configured at reverse proxy)
   - **Secrets Management**: `.env` for secrets, `.gitignore` prevents commits

   ## CORS & CSRF
   - **CORS**: Restricted to `http://localhost:5173` (dev) / production domain
   - **CSRF**: Not needed for JWT stateless API; SessionAuthentication only for admin

   ## Database Security
   - **Least-Privilege Roles**: See `sql/06_roles_grants.sql`
   - **Managed=False Models**: Django cannot DROP/ALTER tables — schema changes via SQL scripts only

   ## Audit Logging
   - **Inventory Ledger**: Every stock change writes to `catalog_inventorymovement`
   - **Payment Records**: Immutable payment rows with provider reference

   ## Known Limitations (Student Project Scope)
   - No rate limiting on auth endpoints (add Django Ratelimit in production)
   - No 2FA (recommend TOTP for vendor/admin accounts)
   - No automated security scanning (add bandit/safety to CI)
   ```

**Expected result.** SECURITY.md documents all security measures and known gaps.

**Verify.** File exists and covers all sections above.

**If it fails.** N/A — this is a documentation step.

---

## Step M4.15 — Database roles & grants script

**Goal.** Create SQL script for least-privilege MySQL roles.

**Where.** `backend/sql/06_roles_grants.sql`

**Actions.**

1. Create `backend/sql/06_roles_grants.sql`:

   ```sql
   -- E-Compra MySQL Roles and Grants
   -- Run as root: mysql -u root -p < 06_roles_grants.sql

   -- Create roles
   CREATE ROLE IF NOT EXISTS 'ecompra_app', 'ecompra_readonly', 'ecompra_admin';

   -- Application role: full CRUD on domain tables, SELECT on lookups
   GRANT SELECT, INSERT, UPDATE, DELETE ON ecompra.* TO 'ecompra_app';
   GRANT SELECT ON ecompra.* TO 'ecompra_readonly';

   -- Admin role: full privileges including DDL
   GRANT ALL PRIVILEGES ON ecompra.* TO 'ecompra_admin';

   -- Create users and assign roles
   CREATE USER IF NOT EXISTS 'ecompra_app'@'%' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';
   CREATE USER IF NOT EXISTS 'ecompra_readonly'@'%' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';
   CREATE USER IF NOT EXISTS 'ecompra_admin'@'%' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';

   GRANT 'ecompra_app' TO 'ecompra_app'@'%';
   GRANT 'ecompra_readonly' TO 'ecompra_readonly'@'%';
   GRANT 'ecompra_admin' TO 'ecompra_admin'@'%';

   -- Set default roles
   SET DEFAULT ROLE 'ecompra_app' TO 'ecompra_app'@'%';
   SET DEFAULT ROLE 'ecompra_readonly' TO 'ecompra_readonly'@'%';
   SET DEFAULT ROLE 'ecompra_admin' TO 'ecompra_admin'@'%';

   -- Revoke dangerous privileges from app role
   REVOKE DROP, ALTER, CREATE, INDEX ON ecompra.* FROM 'ecompra_app';
   REVOKE DROP, ALTER, CREATE, INDEX ON ecompra.* FROM 'ecompra_readonly';

   FLUSH PRIVILEGES;
   ```

2. Update `backend/config/settings.py` to use the app user:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'ecompra',
           'USER': 'ecompra_app',
           'PASSWORD': os.environ.get('DB_PASSWORD'),
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {'charset': 'utf8mb4'},
       }
   }
   ```

3. Add `DB_PASSWORD` to `.env` (create if not exists):
   ```powershell
   echo "DB_PASSWORD=your_strong_password_here" >> backend/.env
   ```

**Expected result.** Roles/grants script exists; Django configured to use least-privilege DB user.

**Verify.** 
```powershell
mysql -u root -pAdmin2627 < sql/06_roles_grants.sql
# Test app user can connect
mysql -u ecompra_app -p ecompra -e "SELECT 1"
```

**If it fails.** Check password in `.env` matches; verify `mysqlclient`/`PyMySQL` can connect with new user.

---

## Step M4.16 — Backup & Restore drill

**Goal.** Create backup script, run it, and document a successful restore.

**Where.** `backend/docs/BACKUP_RESTORE.md` and scripts

**Actions.**

1. Create `backend/scripts/backup.sh` (for Git Bash/WSL) or `backup.ps1` (PowerShell):

   **PowerShell version `backend/scripts/backup.ps1`:**
   ```powershell
   param(
       [string]$BackupDir = "C:\backups\ecompra",
       [string]$DbName = "ecompra",
       [string]$User = "root",
       [string]$Password = "Admin2627"
   )

   $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
   $backupFile = Join-Path $BackupDir "ecompra_$timestamp.sql"
   
   if (-not (Test-Path $BackupDir)) {
       New-Item -ItemType Directory -Path $BackupDir -Force
   }

   Write-Host "Starting backup to $backupFile..."
   & mysqldump -u $User -p$Password --single-transaction --routines --triggers $DbName | Set-Content -Path $backupFile -Encoding utf8
   
   if ($LASTEXITCODE -eq 0) {
       Write-Host "Backup successful: $backupFile"
       # Keep only last 7 backups
       Get-ChildItem $BackupDir -Filter "ecompra_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 7 | Remove-Item -Force
   } else {
       Write-Error "Backup failed with exit code $LASTEXITCODE"
       exit 1
   }
   ```

2. Create `backend/scripts/restore.ps1`:
   ```powershell
   param(
       [string]$BackupFile,
       [string]$DbName = "ecompra",
       [string]$User = "root",
       [string]$Password = "Admin2627"
   )

   if (-not (Test-Path $BackupFile)) {
       Write-Error "Backup file not found: $BackupFile"
       exit 1
   }

   Write-Host "Restoring $BackupFile to $DbName..."
   # Drop and recreate database
   & mysql -u $User -p$Password -e "DROP DATABASE IF EXISTS $DbName; CREATE DATABASE $DbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   # Restore
   Get-Content $BackupFile | & mysql -u $User -p$Password $DbName
   
   if ($LASTEXITCODE -eq 0) {
       Write-Host "Restore successful"
   } else {
       Write-Error "Restore failed with exit code $LASTEXITCODE"
       exit 1
   }
   ```

3. Run backup drill:
   ```powershell
   # 1. Run backup
   .\scripts\backup.ps1
   
   # 2. Verify backup file exists and has content
   Get-Content .\backups\ecompra\ecompra_*.sql -TotalCount 20
   
   # 3. Run restore to a test database
   .\scripts\restore.ps1 -BackupFile .\backups\ecompra\ecompra_20261123_103000.sql -DbName test_ecompra_restore
   
   # 4. Verify restored data
   mysql -u root -pAdmin2627 -e "SELECT COUNT(*) FROM test_ecompra_restore.catalog_product; SELECT COUNT(*) FROM test_ecompra_restore.orders_order;"
   ```

4. Document in `backend/docs/BACKUP_RESTORE.md`:
   ```markdown
   # E-Compra Backup & Restore Procedure

   ## Backup Script
   Location: `scripts/backup.ps1`
   Runs: `mysqldump --single-transaction --routines --triggers`
   Retention: 7 days (auto-cleanup)

   ## Restore Script
   Location: `scripts/restore.ps1`
   Drops and recreates target database, then restores.

   ## Drill Log (2026-11-23)
   - Backup file: `ecompra_20261123_103000.sql` (2.3 MB)
   - Restore target: `test_ecompra_restore`
   - Tables restored: 35
   - Data verified: 34 products, 6 vendors, 9 categories, 3 orders
   - Time: Backup 3s, Restore 2s
   - Status: ✅ SUCCESS

   ## Production Schedule
   - Daily at 02:00 via Windows Task Scheduler
   - Off-site copy: Upload to cloud storage (not implemented in scope)
   - Monthly restore test: First Monday of each month
   ```

**Expected result.** Backup/restore scripts work; drill documented with timestamps and verification counts.

**Verify.** Run the drill commands above; check `BACKUP_RESTORE.md` has the log.

**If it fails.**
- `mysqldump` not in PATH → use full path `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe`
- Permission denied → run PowerShell as Administrator
- Character set issues → ensure `--default-character-set=utf8mb4` in mysqldump

---

## Step M4.17 — User manual (customer & vendor)

**Goal.** Write a concise user manual for both customer and vendor interfaces.

**Where.** `backend/docs/USER_MANUAL.md`

**Actions.**

1. Create `backend/docs/USER_MANUAL.md`:

   ```markdown
   # E-Compra User Manual

   ## For Customers (Maria Santos)

   ### Getting Started
   1. Open the app at `https://your-domain.com` (or `http://localhost:5173` locally)
   2. Click **Login** and enter your credentials
   3. New users: Contact admin for account creation (no self-registration in v1)

   ### Browsing Products
   - **Search**: Type in the search bar (top of catalog) and press Enter
   - **Filter by Category**: Use the dropdown next to search
   - **Product Cards** show: Name, Price/Unit, Vendor, Stall Location, Availability
   - **Click a product** to see details, description, and vendor info

   ### Adding to Cart
   1. On product detail or catalog, click **Add** (or set quantity then Add)
   2. Items are added to your cart — one cart per user
   3. **Cart icon** (top right) shows item count

   ### Cart Management
   - Visit **Cart** from header
   - **Update Quantity**: Change number and press Enter / click Update
   - **Remove Item**: Click Remove or set quantity to 0
   - Cart shows items **grouped by vendor** — each vendor becomes a separate order

   ### Checkout
   1. Click **Proceed to Checkout**
   2. **Fulfillment**: Choose Delivery (to address) or Pickup (at vendor stall)
   3. Review vendor-grouped order summary
   4. Click **Place Order** → Creates one Order per vendor
   5. Redirected to **Payment** screen

   ### Payment
   - Select method: GCash, Maya, Online Banking, Card
   - Enter provider reference (from your payment app)
   - Submit → Payment recorded as **Verified** (sandbox mode)
   - You receive Order ID and Transaction Reference

   ### Order Tracking
   - Visit **Order Tracking** from order confirmation or history
   - **Status Timeline** shows: Pending Payment → Confirmed → Preparing → Out for Delivery → Completed
   - For Pickup orders: Pending Payment → Confirmed → Preparing → Ready for Pickup → Completed

   ### Favorites
   - Click ♡ on any product to add to favorites
   - View favorites from profile menu (future feature)

   ---

   ## For Vendors (Pedro Reyes)

   ### Vendor POS (Point of Sale)
   1. Login with vendor account
   2. Navigate to **Vendor POS** (`/vendor/pos`)
   3. See all orders for your stall, grouped by status

   ### Order Status Flow
   - **Confirmed** → Customer paid, order received
   - **Preparing** → You're packing/preparing items
   - **Ready for Pickup** → Customer can collect (pickup orders)
   - **Out for Delivery** → Handed to delivery rider (delivery orders)
   - **Completed** → Customer received order
   - **Cancelled** → Order cancelled (any stage)

   ### Updating Status
   1. Find the order in the queue
   2. Click the **Next Status** button (only valid transitions shown)
   3. System validates: Cannot skip steps (e.g., Confirmed → Out for Delivery blocked)

   ### Cash Payment & Receipt (Walk-in / POS)
   - For walk-in customers: Use **POS Walk-in** flow
   - Enter cash tendered → System calculates **Change Due**
   - **Receipt** generated with serial `RC-{ref}-{attempt}` (BIR-style 72mm format)
   - Print receipt → Hand to customer

   ### Inventory Management
   - Visit **Products** (`/vendor/products`) — future feature
   - Update stock quantities, prices, availability
   - Stock auto-decrements on confirmed sales (database trigger)

   ### Sales Dashboard
   - Visit **Dashboard** (`/vendor/dashboard`) — future feature
   - Shows: Daily/Weekly/Monthly sales, Best sellers, Low stock alerts

   ---

   ## Troubleshooting

   | Issue | Solution |
   |---|---|
   | "Invalid token" | Log out and log in again (token expired) |
   | Cart empty after login | Cart is per-user; items don't persist across accounts |
   | Payment failed | Check provider reference matches exactly |
   | Status update blocked | Must follow sequence: Confirmed → Preparing → Ready/Out → Completed |
   | Can't see orders | Ensure you're logged in as the correct vendor |
   ```

**Expected result.** USER_MANUAL.md covers customer and vendor workflows with screenshots placeholders.

**Verify.** File exists and is readable.

**If it fails.** N/A — documentation step.

---

## Step M4.18 — Developer documentation (API reference, setup, architecture)

**Goal.** Create technical documentation for future maintainers.

**Where.** `backend/docs/DEVELOPER_GUIDE.md`

**Actions.**

1. Create `backend/docs/DEVELOPER_GUIDE.md`:

   ```markdown
   # E-Compra Developer Guide

   ## Architecture Overview
   - **Frontend**: Vue 3 + Vite + Tailwind CSS v4 + Pinia + Vue Router
   - **Backend**: Django 6.1 + DRF 3.18 + SimpleJWT + MySQL 8.4
   - **Database**: Managed via SQL scripts (`sql/`) — Django `managed=False` models
   - **Auth**: JWT (access 60m, refresh 7d, rotation + blacklist)

   ## Project Structure
   ```
   e-compraSystem/
   ├── backend/
   │   ├── accounts/     # User profiles, auth
   │   ├── catalog/      # Products, vendors, categories, inventory
   │   ├── cart/         # Cart, cart items
   │   ├── orders/       # Orders, items, transactions, payments, delivery
   │   ├── vendors/      # POS vendor, vendor transactions
   │   ├── favorites/    # Favorite products/vendors
   │   └── config/       # Django settings, URLs
   ├── frontend/
   │   ├── src/
   │   │   ├── views/       # Page components
   │   │   ├── components/  # Reusable UI
   │   │   ├── stores/      # Pinia stores
   │   │   ├── services/    # API client
   │   │   └── router/      # Vue Router
   │   └── ...
   ├── sql/              # Schema, indexes, seed, views, procedures, roles, backup
   ├── docs/             # This folder
   └── steps/            # Phase instructions + PROGRESS_LOG.md
   ```

   ## Database Schema Key Points
   - **28 tables** across 6 apps
   - **FK fields use `db_column` names**: `unit_code`, `availability_code`, `status_code`, `fulfillment_code`, `transaction_type`
   - **Lookup tables**: TransactionStatus, PaymentStatus, DeliveryStatus, FulfillmentMethod, TransactionType, AvailabilityStatus
   - **Seed data codes** are the contract — never use raw strings in code

   ## API Endpoints
   | Module | Base Path | Key Endpoints |
   |---|---|---|
   | Catalog | `/api/catalog/` | `products/`, `categories/`, `vendors/`, `units/`, `availability/` |
   | Orders | `/api/orders/` | `transaction-statuses/`, `payment-statuses/`, `delivery-statuses/`, `fulfillment-methods/`, `transaction-types/` |
   | Cart | `/api/cart/` | `GET /`, `POST add/`, `POST update_item/`, `POST remove_item/` |
   | Checkout | `/api/checkout/` | `POST /` (cart-splitting by vendor) |
   | Payment | `/api/payment/` | `POST /` (record payment) |
   | Vendors | `/api/vendors/` | `GET pos/`, `POST pos/` (status update) |
   | Favorites | `/api/favorites/` | `GET products/`, `GET vendors/` |
   | Auth | `/api/auth/` | `POST token/`, `POST token/refresh/`, `POST token/verify/`, `GET user/` |

   ## Service Layer Pattern
   - **Views are thin** — only HTTP handling, serialization, permission checks
   - **Services contain business logic** — `orders/services.py` has `transition_order_status()`, `checkout_cart()`
   - **Always use services** from views — never put logic in views

   ## Common Commands
   ```bash
   # Backend
   cd backend
   python manage.py runserver          # Start API on :8000
   python manage.py check              # Validate models
   python -m pytest -v                 # Run tests
   ruff check && ruff format           # Lint + format

   # Frontend
   cd frontend
   npm run dev                         # Start Vite on :5173
   npm run build                       # Production build
   npm test                            # Unit tests
   npx playwright test                 # E2E tests

   # Database
   mysql -u root -p < sql/01_schema.sql
   mysql -u root -p < sql/02_indexes.sql
   mysql -u root -p < sql/03_seed.sql
   ```

   ## Adding a New Status Code
   1. Add to `sql/03_seed.sql` (INSERT INTO orders_transactionstatus)
   2. Update `orders/services.py` `ALLOWED_TRANSITIONS` dict
   3. Run seed script: `mysql -u root -p ecompra < sql/03_seed.sql`
   4. Test transition in Vendor POS

   ## Deployment Checklist
   - [ ] `DEBUG=False` in settings
   - [ ] `ALLOWED_HOSTS` set
   - [ ] `SECRET_KEY` from env
   - [ ] `CORS_ALLOWED_ORIGINS` production domain
   - [ ] HTTPS + HSTS headers
   - [ ] Database user: `ecompra_app` (least privilege)
   - [ ] Backup schedule configured
   - [ ] Static files: `collectstatic` + CDN
   - [ ] Frontend build: `npm run build` → serve via nginx
   ```

**Expected result.** DEVELOPER_GUIDE.md covers architecture, structure, API, patterns, commands, deployment.

**Verify.** File exists and is comprehensive.

**If it fails.** N/A — documentation step.

---

## Step M4.19 — Full dress rehearsal (Checkpoint Demo #5)

**Goal.** Run the complete demo walkthrough exactly as planned for the defense.

**Where.** Entire project

**Actions.**

1. **Prepare the demo script** (time each section):
   - [ ] 2 min: Architecture slide (Vue/Django/MySQL)
   - [ ] 2 min: ERD + key design decisions (Order/Transaction/Payment split)
   - [ ] 3 min: Live demo — Customer journey (search → cart → checkout → payment → tracking)
   - [ ] 2 min: Live demo — Vendor POS (order queue → status flow → receipt)
   - [ ] 2 min: Live demo — Price comparison (same product across vendors)
   - [ ] 1 min: Database — show seed data, triggers, indexes
   - [ ] 1 min: Security — JWT, roles, no card data
   - [ ] 1 min: Backup/restore — show `BACKUP_RESTORE.md` log
   - [ ] 1 min: Performance — show `PERFORMANCE.md` EXPLAIN output
   - [ ] 1 min: Tests — `pytest` output, Playwright report

   **Total: ~16 minutes** (leave 4 min buffer for questions)

2. **Run the rehearsal:**
   ```powershell
   # Terminal 1: Backend
   cd backend && python manage.py runserver
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   
   # Terminal 3: Database (optional)
   mysql -u root -pAdmin2627 ecompra
   ```

3. **Walk through the demo script** with a timer. Note any:
   - Flaky steps (slow queries, missing data)
   - UI bugs (broken links, wrong redirects)
   - Missing seed data (products, vendors)
   - Error messages in console

4. **Fix any issues found** before M4.20.

**Expected result.** Smooth 20-minute demo with no errors; all issues from rehearsal fixed.

**Verify.** Complete demo without errors; timer under 20 minutes.

**If it fails.** Fix issues immediately; re-rehearse until clean.

---

## Step M4.20 — Final packaging & submission

**Goal.** Package everything and submit by Dec 12 deadline.

**Where.** Entire project

**Actions.**

1. **Final verification checklist:**
   - [ ] `git status` clean (no uncommitted changes)
   - [ ] All tests pass: `pytest` (28+), `npm test`, `npx playwright test`
   - [ ] `python manage.py check` → no issues
   - [ ] `ruff check backend` → all checks passed
   - [ ] `npm run build` → succeeds
   - [ ] `m3-complete` tag exists; create `m4-complete` tag

2. **Create final commit and tag:**
   ```powershell
   git add -A
   git commit -m "feat(m4): hardening & delivery — Vue integration, tests, perf, security, backup, docs

   - Vue front-end complete: auth, catalog, cart, checkout, payment, POS, tracking
   - Unit tests (backend + frontend) + E2E tests (Playwright)
   - Performance indexes + EXPLAIN analysis (PERFORMANCE.md)
   - Security audit (SECURITY.md) + least-privilege DB roles
   - Backup/restore drill documented (BACKUP_RESTORE.md)
   - User manual + Developer guide
   - Full dress rehearsal completed

   Co-Authored-By: Claude Code <noreply@anthropic.com>"
   git tag m4-complete
   git push origin develop --tags
   ```

3. **Prepare submission package:**
   - [ ] GitHub repo URL: `https://github.com/davedy-cit/e-compraStage`
   - [ ] Tag: `m4-complete` (points to final commit)
   - [ ] Documentation files in `docs/`:
     - `PROJECT_TIMELINE.md`
     - `ER_TO_RELATIONAL.md`
     - `NORMALIZATION.md`
     - `PERFORMANCE.md`
     - `SECURITY.md`
     - `BACKUP_RESTORE.md`
     - `USER_MANUAL.md`
     - `DEVELOPER_GUIDE.md`
     - `DESIGN_DECISIONS.md`
     - `DESIGN_REVIEW.md`
   - [ ] SQL scripts in `sql/`:
     - `01_schema.sql`, `02_indexes.sql`, `03_seed.sql`
     - `04_performance_indexes.sql`
     - `05_procedures_triggers.sql` (from M3)
     - `06_roles_grants.sql`
   - [ ] Mockups in `docs/mockups/` (16 screens + gallery + screenshots)
   - [ ] Proposal deck: `docs/E-Compra_Proposal.pptx`

4. **Verify fresh clone works** (simulate evaluator):
   ```powershell
   # In a temp directory
   git clone https://github.com/davedy-cit/e-compraStage.git
   cd e-compraStage
   git checkout m4-complete
   
   # Backend
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Fill in DB_PASSWORD
   mysql -u root -p < ../sql/01_schema.sql
   mysql -u root -p < ../sql/02_indexes.sql
   mysql -u root -p < ../sql/03_seed.sql
   python manage.py migrate
   python manage.py check
   python -m pytest
   
   # Frontend
   cd ../frontend
   npm install
   npm run build
   ```

5. **Submit** per instructor instructions (GitHub release, ZIP upload, etc.)

**Expected result.** Clean repo with `m4-complete` tag; fresh clone reproduces entire system; submission delivered.

**Verify.** Fresh clone passes all checks; submission confirmed.

**If it fails.**
- Missing `.env.example` → create it with all required vars
- SQL scripts assume `root` user → document in README
- Frontend build fails → check `vite.config.js` alias and Tailwind v4 config

---

## M4 Completion Summary

| Step | Description | Status |
|---|---|---|
| M4.1 | Vue: API client, auth store, JWT interceptors | ☐ |
| M4.2 | Backend: `/api/auth/user/` endpoint | ☐ |
| M4.3 | Vue: Login + route guards | ☐ |
| M4.4 | Vue: Catalog browse + search | ☐ |
| M4.5 | Vue: Product detail | ☐ |
| M4.6 | Vue: Cart (verify M3.13) | ☐ |
| M4.7 | Vue: Checkout (verify M3.14) | ✅ |
| M4.8 | Vue: Payment (verify M3.15) | ✅ |
| M4.9 | Vue: Vendor POS (verify M3.16) | ✅ |
| M4.10 | Vue: Order tracking | ✅ |
| M4.11 | Unit tests: pytest + Vitest | ✅ |
| M4.12 | E2E tests: Playwright | ✅ |
| M4.13 | Indexes + PERFORMANCE.md | ✅ |
| M4.14 | SECURITY.md | ✅ |
| M4.15 | DB roles/grants script | ✅ |
| M4.16 | Backup/restore drill | ✅ |
| M4.17 | USER_MANUAL.md | ✅ |
| M4.18 | DEVELOPER_GUIDE.md | ✅ |
| M4.19 | Dress rehearsal (Checkpoint #5) | ✅ |
| M4.20 | Final packaging + submission | ✅ |

**Total: 20 steps** across 10 days (Dec 3–12). Dec 10–12 are buffer for rehearsal fixes and packaging only.

---

## CCS630 Lessons Applied in M4

| Lesson | Artifact |
|---|---|
| Indexing & Performance | `sql/04_performance_indexes.sql` + `docs/PERFORMANCE.md` with EXPLAIN |
| Security | `docs/SECURITY.md` + `sql/06_roles_grants.sql` |
| Backup & Recovery | `scripts/backup.ps1`, `scripts/restore.ps1`, `docs/BACKUP_RESTORE.md` |
| Transactions & Concurrency | Verified in M3; tested in M4.11 unit tests |
| Stored Procedures / Triggers | `sql/05_procedures_triggers.sql` (from M3 inventory trigger) |
| Views | Reporting views from M2; tested in M4.11 |

---

*End of Phase 4 — Hardening & Delivery*