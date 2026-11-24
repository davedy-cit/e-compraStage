<template>
  <div class="admin-dashboard page">
    <!-- Header -->
    <header class="page-head row-between">
      <div>
        <h1 class="page-title">Admin Dashboard</h1>
        <p class="muted">Market Administrator Overview</p>
      </div>
      <div class="row" style="gap: 8px;">
        <router-link to="/admin/vendors" class="btn btn-accent">Manage Vendors</router-link>
        <router-link to="/catalog" class="btn">View Marketplace</router-link>
      </div>
    </header>

    <!-- Stats Cards -->
    <section class="card">
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div class="stat card">
          <div class="stat-label">Total Vendors</div>
          <div class="stat-value">{{ stats.totalVendors }}</div>
        </div>
        <div class="stat card">
          <div class="stat-label">Active Vendors</div>
          <div class="stat-value">{{ stats.activeVendors }}</div>
        </div>
        <div class="stat card">
          <div class="stat-label">Inactive Vendors</div>
          <div class="stat-value">{{ stats.inactiveVendors }}</div>
        </div>
        <div class="stat card">
          <div class="stat-label">Total Products</div>
          <div class="stat-value">{{ stats.totalProducts }}</div>
        </div>
        <div class="stat card">
          <div class="stat-label">Pending Orders</div>
          <div class="stat-value">{{ stats.pendingOrders }}</div>
        </div>
        <div class="stat card">
          <div class="stat-label">Revenue (Today)</div>
          <div class="stat-value">{{ formatCurrency(stats.revenueToday) }}</div>
        </div>
      </div>
    </section>

    <!-- Quick Actions -->
    <section class="card">
      <h2 class="section-title">Quick Actions</h2>
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
        <router-link to="/admin/vendors" class="action-card card">
          <div class="action-icon">👥</div>
          <div class="action-label">Add New Vendor</div>
          <div class="action-desc muted">Create vendor account with stall</div>
        </router-link>
        <router-link to="/admin/vendors" class="action-card card">
          <div class="action-icon">📋</div>
          <div class="action-label">View All Vendors</div>
          <div class="action-desc muted">Manage vendor accounts and stalls</div>
        </router-link>
        <a href="#" class="action-card card" @click.prevent>
          <div class="action-icon">📊</div>
          <div class="action-label">Sales Reports</div>
          <div class="action-desc muted">View marketplace analytics</div>
        </a>
        <a href="#" class="action-card card" @click.prevent>
          <div class="action-icon">⚙️</div>
          <div class="action-label">Market Settings</div>
          <div class="action-desc muted">Configure market sections, fees</div>
        </a>
        <a href="#" class="action-card card" @click.prevent>
          <div class="action-icon">📦</div>
          <div class="action-label">Product Moderation</div>
          <div class="action-desc muted">Review pending product listings</div>
        </a>
        <a href="#" class="action-card card" @click.prevent>
          <div class="action-icon">🎫</div>
          <div class="action-label">Support Tickets</div>
          <div class="action-desc muted">Customer & vendor support</div>
        </a>
      </div>
    </section>

    <!-- Recent Activity -->
    <section class="card" v-if="recentActivity.length > 0">
      <div class="row-between" style="margin-bottom: 12px;">
        <h2 class="section-title" style="margin: 0;">Recent Activity</h2>
        <a href="#" class="link-sm">View all</a>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Type</th>
              <th>Description</th>
              <th>User</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="activity in recentActivity" :key="activity.id">
              <td class="tiny muted">{{ activity.time }}</td>
              <td><span class="badge" :class="activity.badge">{{ activity.type }}</span></td>
              <td>{{ activity.description }}</td>
              <td>{{ activity.user }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Empty state for recent activity -->
    <div v-else class="card text-center py-12">
      <p class="muted">No recent activity</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

const stats = ref({
  totalVendors: 0,
  activeVendors: 0,
  inactiveVendors: 0,
  totalProducts: 0,
  pendingOrders: 0,
  revenueToday: 0,
})

const recentActivity = ref([])
const loading = ref(true)
const error = ref(null)

// Role guard - redirect if not admin
const isAdmin = computed(() => authStore.user?.role === 'admin')

onMounted(async () => {
  if (!isAdmin.value) {
    // Navigation guard in router should handle this, but double-check
    return
  }
  await fetchDashboardData()
})

async function fetchDashboardData() {
  loading.value = true
  error.value = null
  try {
    // Fetch stats from admin endpoints
    const [vendorsRes, productsRes, ordersRes] = await Promise.all([
      api.get('/vendors/admin/'),
      api.get('/products/'),
      api.get('/orders/'),
    ])

    const vendors = vendorsRes.data || []
    stats.value.totalVendors = vendors.length
    stats.value.activeVendors = vendors.filter(v => v.is_active === 1).length
    stats.value.inactiveVendors = vendors.filter(v => v.is_active === 0).length

    // Products count
    stats.value.totalProducts = (productsRes.data?.results || productsRes.data || []).length

    // Orders stats
    const orders = ordersRes.data?.results || ordersRes.data || []
    stats.value.pendingOrders = orders.filter(o => o.status_code === 'pending' || o.status_code === 'confirmed').length

    // Calculate today's revenue (mock for now - would need backend endpoint)
    const today = new Date().toISOString().split('T')[0]
    const todayOrders = orders.filter(o => o.created_at?.startsWith(today))
    stats.value.revenueToday = todayOrders.reduce((sum, o) => sum + Number(o.total_amount || 0), 0)

    // Build recent activity
    recentActivity.value = [
      ...vendors.slice(0, 3).map(v => ({
        id: `vendor-${v.id}`,
        time: formatTimeAgo(v.created_at),
        type: v.is_active === 1 ? 'Vendor Added' : 'Vendor Deactivated',
        badge: v.is_active === 1 ? 'badge-ok' : 'badge-warn',
        description: `${v.name} (${v.stall_location})`,
        user: v.user_username,
      })),
      ...orders.slice(0, 3).map(o => ({
        id: `order-${o.id}`,
        time: formatTimeAgo(o.created_at),
        type: 'New Order',
        badge: 'badge-info',
        description: `Order #${o.id} - ${formatCurrency(o.total_amount)}`,
        user: o.customer_name || 'Customer',
      })),
    ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 10)
  } catch (e) {
    error.value = 'Failed to load dashboard data'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    minimumFractionDigits: 2,
  }).format(amount)
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return 'Unknown'
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
.page-head {
  margin-bottom: 24px;
}
.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 4px;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 16px;
}
.muted {
  color: var(--color-muted);
}
.row-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.row {
  display: flex;
  align-items: center;
}
.grid {
  display: grid;
}
.stat {
  text-align: center;
  padding: 20px 16px;
}
.stat-label {
  font-size: 0.75rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
}
.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 24px 16px;
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
.action-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}
.action-label {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 4px;
}
.action-desc {
  font-size: 0.8rem;
}
.link-sm {
  font-size: 0.85rem;
  color: var(--color-accent);
  text-decoration: none;
}
.link-sm:hover {
  text-decoration: underline;
}
.text-center {
  text-align: center;
}
.py-12 {
  padding-top: 48px;
  padding-bottom: 48px;
}
.tiny {
  font-size: 0.75rem;
}
.table-wrap {
  overflow-x: auto;
}
.table {
  width: 100%;
  border-collapse: collapse;
}
.table th,
.table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.table th {
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--color-muted);
  letter-spacing: 0.05em;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
}
.badge-ok { background: var(--color-success-bg); color: var(--color-success); }
.badge-warn { background: var(--color-warning-bg); color: var(--color-warning); }
.badge-info { background: var(--color-info-bg); color: var(--color-info); }

@media (max-width: 640px) {
  .page {
    padding: 16px;
  }
  .stat-value {
    font-size: 2rem;
  }
  .action-card {
    padding: 16px 12px;
  }
}
</style>