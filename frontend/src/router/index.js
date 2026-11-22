import { createRouter, createWebHistory } from 'vue-router'
import CartView from '@/views/CartView.vue'
import CheckoutView from '@/views/CheckoutView.vue'

const routes = [
  { path: '/cart', name: 'cart', component: CartView },
  { path: '/checkout', name: 'checkout', component: CheckoutView },
  { path: '/', redirect: '/cart' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router