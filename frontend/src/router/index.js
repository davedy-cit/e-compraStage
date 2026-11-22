import { createRouter, createWebHistory } from 'vue-router'
import CartView from '@/views/CartView.vue'
import CheckoutView from '@/views/CheckoutView.vue'
import PaymentView from '@/views/PaymentView.vue'
import VendorPOSView from '@/views/VendorPOSView.vue'

const routes = [
  { path: '/cart', name: 'cart', component: CartView },
  { path: '/checkout', name: 'checkout', component: CheckoutView },
  { path: '/payment/:id?', name: 'payment', component: PaymentView, props: true },
  { path: '/vendor/pos', name: 'vendor-pos', component: VendorPOSView },
  { path: '/', redirect: '/cart' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router