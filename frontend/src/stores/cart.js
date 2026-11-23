import { defineStore } from 'pinia'
import api from '@/services/api'

export const useCartStore = defineStore('cart', {
  state: () => ({
    cart: null,
    _initialized: false,
    fulfillmentMethods: {},
  }),
  actions: {
    async fetchCart() {
      try {
        const response = await api.get('/cart/')
        this.cart = response.data
      } catch (err) {
        console.error('Failed to load cart:', err)
        this.cart = { items: [], total_amount: 0 }
      }
    },
    async init() {
      if (this._initialized) return
      await this.fetchCart()
      this._initialized = true
    },
    clear() {
      this.cart = null
      this._initialized = false
    },
    setFulfillmentMethods(methods) {
      this.fulfillmentMethods = { ...methods }
    },
  },
})
