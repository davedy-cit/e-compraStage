import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import CartView from '@/views/CartView.vue'
import CheckoutView from '@/views/CheckoutView.vue'
import PaymentView from '@/views/PaymentView.vue'
import VendorPOSView from '@/views/VendorPOSView.vue'
import LoginView from '@/views/LoginView.vue'
import CatalogView from '@/views/CatalogView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'
import OrderTrackingView from '@/views/OrderTrackingView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/cart', name: 'cart', component: CartView, meta: { requiresAuth: true } },
  { path: '/checkout', name: 'checkout', component: CheckoutView, meta: { requiresAuth: true } },
  { path: '/payment/:id?', name: 'payment', component: PaymentView, props: true, meta: { requiresAuth: true } },
  { path: '/vendor/pos', name: 'vendor-pos', component: VendorPOSView, meta: { requiresAuth: true, role: 'vendor' } },
  { path: '/', redirect: '/catalog' },
  { path: '/catalog', name: 'catalog', component: CatalogView, meta: { requiresAuth: true } },
  { path: '/product/:id', name: 'product-detail', component: ProductDetailView, meta: { requiresAuth: true } },
  { path: '/order/:id', name: 'order-tracking', component: OrderTrackingView, meta: { requiresAuth: true } },
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