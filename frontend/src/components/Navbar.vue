<template>
  <header class="appbar" :class="{ 'is-vendor': isVendor, 'is-admin': isAdmin }">
    <div class="wrap">
      <div class="flex items-center justify-between" style="height: 58px;">
        <!-- Logo / Brand -->
        <router-link to="/catalog" class="brand">
          <span class="mark">EC</span>
          <span>E-Compra<small>Mandaue Public Market</small></span>
        </router-link>

        <!-- Desktop Navigation -->
        <nav class="nav">
          <router-link
            v-for="item in visibleNavItems"
            :key="item.name"
            :to="item.to"
            :class="{ on: isActive(item.to) }"
          >
            {{ item.label }}
          </router-link>
        </nav>

        <!-- Cart with item count -->
        <router-link to="/cart" class="cart">
          🛒 Cart
          <span v-if="cartItemCount > 0" style="margin-left: 6px;">· {{ cartItemCount }}</span>
        </router-link>

        <!-- User Section (authenticated) -->
        <div v-if="authStore.isAuthenticated" class="who" style="display: flex; align-items: center; gap: 12px; margin-left: 16px;">
          <div style="text-align: right;">
            <div class="font-medium" style="font-size: .85rem;">{{ authStore.user?.username }}</div>
            <div class="text-xs muted" style="color: rgba(255,255,255,.85); text-transform: capitalize;">{{ authStore.user?.role }}</div>
          </div>
          <button
            @click="handleLogout"
            class="btn btn-sm"
            style="background: rgba(255,255,255,.16); border-color: transparent; color: #fff; padding: 5px 10px;"
          >
            Logout
          </button>
        </div>

        <!-- Auth links (not authenticated) -->
        <div v-else style="display: flex; align-items: center; gap: 8px; margin-left: 8px;">
          <router-link
            to="/register"
            class="btn btn-sm"
            style="background: rgba(255,255,255,.16); border-color: transparent; color: #fff; padding: 5px 12px;"
          >
            Register
          </router-link>
          <router-link
            to="/login"
            class="btn btn-sm"
            style="background: var(--color-accent); border-color: transparent; color: #fff; padding: 5px 12px;"
          >
            Login
          </router-link>
        </div>

        <!-- Mobile Menu Button -->
        <button
          @click="toggleMobileMenu"
          class="md:hidden"
          style="background: none; border: none; padding: 4px; color: #fff;"
        >
          <span class="block w-6 h-0.5 bg-current"></span>
          <span class="block w-6 h-0.5 bg-current mt-1"></span>
          <span class="block w-6 h-0.5 bg-current mt-1"></span>
        </button>
      </div>

      <!-- Mobile Navigation (dropdown) -->
      <div
        v-if="mobileMenuOpen"
        class="md:hidden"
        style="padding: 12px 0; border-top: 1px solid rgba(255,255,255,.12); margin-top: 4px;"
      >
        <div class="space-y-2">
          <router-link
            v-for="item in visibleNavItems"
            :key="item.name"
            :to="item.to"
            @click="mobileMenuOpen = false"
            class="block px-4 py-2 text-sm font-medium hover:bg-white/10 rounded-lg"
            style="color: #fff;"
          >
            {{ item.label }}
          </router-link>
          <router-link
            to="/cart"
            @click="mobileMenuOpen = false"
            class="block px-4 py-2 text-sm font-medium hover:bg-white/10 rounded-lg flex items-center gap-2"
            style="color: #fff;"
          >
            <span>🛒 Cart</span>
            <span
              v-if="cartItemCount > 0"
              class="bg-red-500 text-white text-xs font-bold rounded-full h-4 w-4 flex items-center justify-center ml-auto"
            >
              {{ cartItemCount }}
            </span>
          </router-link>
          <div class="pt-4 border-t" style="border-color: rgba(255,255,255,.12);">
            <div v-if="authStore.isAuthenticated">
              <div class="px-4 py-2">
                <div class="text-sm font-medium" style="color: #fff;">{{ authStore.user?.username }}</div>
                <div class="text-xs" style="color: rgba(255,255,255,.7); text-transform: capitalize;">{{ authStore.user?.role }}</div>
              </div>
              <button
                @click="handleLogout"
                class="w-full px-4 py-2 text-sm font-medium rounded-lg text-left"
                style="background: rgba(255,255,255,.16); color: #fff; border: none;"
              >
                Logout
              </button>
            </div>
            <div v-else>
              <router-link
                to="/register"
                class="w-full px-4 py-2 text-sm font-medium text-center rounded-lg block mb-2"
                style="background: rgba(255,255,255,.16); color: #fff; border: none;"
              >
                Register
              </router-link>
              <router-link
                to="/login"
                class="w-full px-4 py-2 text-sm font-medium text-center rounded-lg block"
                style="background: var(--color-accent); color: #fff; border: none;"
              >
                Login
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const mobileMenuOpen = ref(false)

const navItems = [
  { name: 'catalog', label: 'Marketplace', to: '/catalog' },
  { name: 'market-map', label: 'Market Map', to: '/market-map' },
  { name: 'favorites-history', label: 'Favorites', to: '/favorites-history' },
  { name: 'order-tracking', label: 'Orders', to: '/order-tracking' },
]

const vendorNavItems = [
  { name: 'vendor-dashboard', label: 'Dashboard', to: '/vendor/dashboard' },
  { name: 'vendor-products', label: 'Products', to: '/vendor/products' },
  { name: 'vendor-orders', label: 'Orders', to: '/vendor/orders' },
  { name: 'vendor-pos', label: 'POS', to: '/vendor/pos' },
]

const adminNavItems = [
  { name: 'admin-dashboard', label: 'Admin Dashboard', to: '/admin' },
  { name: 'admin-vendors', label: 'Manage Vendors', to: '/admin/vendors' },
]

const visibleNavItems = computed(() => {
  if (isAdmin.value) {
    return [...navItems, ...adminNavItems]
  }
  if (isVendor.value) {
    return vendorNavItems
  }
  return navItems
})

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const isActive = (to) => route.name === router.resolve(to).name

const cartItemCount = computed(() => {
  if (!cartStore.cart || !cartStore.cart.items) return 0
  return cartStore.cart.items.reduce((sum, item) => sum + Number(item.quantity || 1), 0)
})

const isVendor = computed(() => authStore.user?.role === 'vendor')
const isAdmin = computed(() => authStore.user?.role === 'admin')

const handleLogout = () => {
  authStore.logout()
  mobileMenuOpen.value = false
  router.push('/login')
}
</script>