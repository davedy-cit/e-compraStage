<template>
  <div class="admin-vendors page">
    <!-- Header -->
    <header class="page-head row-between">
      <div>
        <h1 class="page-title">Manage Vendors</h1>
        <p class="muted">Create and manage vendor accounts and stalls</p>
      </div>
      <button @click="openCreateModal" class="btn btn-accent">+ Create Vendor</button>
    </header>

    <!-- Vendor Table -->
    <section class="card">
      <div v-if="loading" class="text-center py-12">
        <div class="spinner"></div>
        <p class="muted mt8">Loading vendors...</p>
      </div>
      <div v-else-if="error" class="alert alert-error">
        {{ error }}
        <button @click="fetchVendors" class="btn btn-sm" style="margin-left: 12px;">Retry</button>
      </div>
      <div v-else class="table-wrap admin-table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Vendor Name</th>
              <th>Stall</th>
              <th>Section</th>
              <th>Contact</th>
              <th>Account</th>
              <th>Status</th>
              <th class="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in vendors" :key="v.id">
              <td>
                <strong>{{ v.name }}</strong>
                <br><span class="tiny muted">{{ v.user_username }}</span>
              </td>
              <td>{{ v.stall_location }}</td>
              <td>{{ v.market_section }}</td>
              <td>
                {{ v.contact_phone }}<br>
                <span class="tiny muted">{{ v.contact_email }}</span>
              </td>
              <td>
                {{ v.user_email }}<br>
                <span class="tiny muted">{{ v.user_is_active === 1 ? 'Active' : 'Inactive' }}</span>
              </td>
              <td>
                <span class="badge" :class="v.is_active === 1 ? 'badge-ok' : 'badge-warn'">
                  {{ v.is_active === 1 ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="actions">
                <button @click="editVendor(v)" class="btn btn-sm" style="margin-right: 4px;">Edit</button>
                <button v-if="v.is_active === 1" @click="handleDeactivate(v.id, v.name)" class="btn btn-sm" style="background: var(--color-danger-bg); border-color: var(--color-danger); color: var(--color-danger);">Deactivate</button>
                <button v-else class="btn btn-sm" disabled style="opacity: 0.5;">Deactivated</button>
              </td>
            </tr>
            <tr v-if="vendors.length === 0">
              <td colspan="7" class="text-center py-8 muted">No vendors registered yet</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Create Vendor Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal card" style="max-width: 560px; width: 90%; max-height: 90vh; overflow-y: auto;">
        <div class="card-head row-between">
          <h3>Create New Vendor Account</h3>
          <button @click="showCreateModal = false" class="btn btn-ghost btn-sm">✕</button>
        </div>
        <form @submit.prevent="handleCreateVendor" class="stack" style="gap: 12px; padding: 16px;">
          <!-- Account Details -->
          <div class="card" style="padding: 16px;">
            <h4 class="mb12" style="border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">Account Credentials</h4>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">Username *</label>
                <input v-model="form.username" type="text" class="input" :class="{ 'input-error': formErrors.username }" />
                <span v-if="formErrors.username" class="field-error">{{ formErrors.username }}</span>
              </div>
              <div class="field">
                <label class="small">Email *</label>
                <input v-model="form.email" type="email" class="input" :class="{ 'input-error': formErrors.email }" />
                <span v-if="formErrors.email" class="field-error">{{ formErrors.email }}</span>
              </div>
            </div>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">First Name *</label>
                <input v-model="form.first_name" type="text" class="input" :class="{ 'input-error': formErrors.first_name }" />
              </div>
              <div class="field">
                <label class="small">Last Name *</label>
                <input v-model="form.last_name" type="text" class="input" :class="{ 'input-error': formErrors.last_name }" />
              </div>
            </div>
            <div class="field">
              <label class="small">Password *</label>
              <input v-model="form.password" type="password" class="input" :class="{ 'input-error': formErrors.password }" />
              <span v-if="formErrors.password" class="field-error">{{ formErrors.password }}</span>
            </div>
          </div>

          <!-- Vendor Details -->
          <div class="card" style="padding: 16px;">
            <h4 class="mb12" style="border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">Stall Information</h4>
            <div class="field">
              <label class="small">Business Name *</label>
              <input v-model="form.name" type="text" class="input" :class="{ 'input-error': formErrors.name }" placeholder="Rosa's Fresh Vegetables" />
              <span v-if="formErrors.name" class="field-error">{{ formErrors.name }}</span>
            </div>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">Stall Location *</label>
                <input v-model="form.stall_location" type="text" class="input" :class="{ 'input-error': formErrors.stall_location }" placeholder="Stall A-12" />
                <span v-if="formErrors.stall_location" class="field-error">{{ formErrors.stall_location }}</span>
              </div>
              <div class="field">
                <label class="small">Market Section *</label>
                <input v-model="form.market_section" type="text" class="input" :class="{ 'input-error': formErrors.market_section }" placeholder="Vegetables Section" />
                <span v-if="formErrors.market_section" class="field-error">{{ formErrors.market_section }}</span>
              </div>
            </div>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">Contact Phone *</label>
                <input v-model="form.contact_phone" type="tel" class="input" :class="{ 'input-error': formErrors.contact_phone }" placeholder="09171112233" />
                <span v-if="formErrors.contact_phone" class="field-error">{{ formErrors.contact_phone }}</span>
              </div>
              <div class="field">
                <label class="small">Contact Email *</label>
                <input v-model="form.contact_email" type="email" class="input" :class="{ 'input-error': formErrors.contact_email }" placeholder="rosa@stall.com" />
                <span v-if="formErrors.contact_email" class="field-error">{{ formErrors.contact_email }}</span>
              </div>
            </div>
          </div>

          <div class="row" style="justify-content: flex-end; gap: 8px; margin-top: 8px;">
            <button type="button" @click="showCreateModal = false" class="btn">Cancel</button>
            <button type="submit" :disabled="creating" class="btn btn-accent">
              <span v-if="creating">Creating…</span>
              <span v-else>Create Vendor</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const vendors = ref([])
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)
const creating = ref(false)
const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  name: '',
  stall_location: '',
  market_section: '',
  contact_phone: '',
  contact_email: '',
})
const formErrors = ref({})

// Role guard
const isAdmin = computed(() => authStore.user?.role === 'admin')

onMounted(async () => {
  if (!isAdmin.value) {
    return
  }
  await fetchVendors()
})

async function fetchVendors() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get('/vendors/admin/')
    vendors.value = res.data || []
  } catch (e) {
    error.value = 'Failed to load vendors'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  resetForm()
  showCreateModal.value = true
}

function resetForm() {
  form.value = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    name: '',
    stall_location: '',
    market_section: '',
    contact_phone: '',
    contact_email: '',
  }
  formErrors.value = {}
}

function validateForm() {
  const errors = {}
  if (!form.value.username.trim()) errors.username = 'Username is required'
  if (!form.value.email.trim()) errors.email = 'Email is required'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) errors.email = 'Invalid email format'
  if (!form.value.first_name.trim()) errors.first_name = 'First name is required'
  if (!form.value.last_name.trim()) errors.last_name = 'Last name is required'
  if (!form.value.password) errors.password = 'Password is required'
  else if (form.value.password.length < 8) errors.password = 'Password must be at least 8 characters'
  if (!form.value.name.trim()) errors.name = 'Business name is required'
  if (!form.value.stall_location.trim()) errors.stall_location = 'Stall location is required'
  if (!form.value.market_section.trim()) errors.market_section = 'Market section is required'
  if (!form.value.contact_phone.trim()) errors.contact_phone = 'Contact phone is required'
  if (!form.value.contact_email.trim()) errors.contact_email = 'Contact email is required'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.contact_email)) errors.contact_email = 'Invalid email format'
  formErrors.value = errors
  return Object.keys(errors).length === 0
}

async function handleCreateVendor() {
  if (!validateForm()) return
  creating.value = true
  try {
    await api.post('/vendors/admin/create/', form.value)
    showCreateModal.value = false
    await fetchVendors()
  } catch (e) {
    if (e.response?.data) {
      const data = e.response.data
      // Map backend validation errors to form fields
      if (data.username) formErrors.value.username = Array.isArray(data.username) ? data.username[0] : data.username
      if (data.email) formErrors.value.email = Array.isArray(data.email) ? data.email[0] : data.email
      if (data.name) formErrors.value.name = Array.isArray(data.name) ? data.name[0] : data.name
      if (data.stall_location) formErrors.value.stall_location = Array.isArray(data.stall_location) ? data.stall_location[0] : data.stall_location
      if (data.market_section) formErrors.value.market_section = Array.isArray(data.market_section) ? data.market_section[0] : data.market_section
      if (data.contact_phone) formErrors.value.contact_phone = Array.isArray(data.contact_phone) ? data.contact_phone[0] : data.contact_phone
      if (data.contact_email) formErrors.value.contact_email = Array.isArray(data.contact_email) ? data.contact_email[0] : data.contact_email
      if (data.password) formErrors.value.password = Array.isArray(data.password) ? data.password[0] : data.password
      if (data.non_field_errors) {
        alert(data.non_field_errors.join(', '))
      }
    } else {
      alert('Failed to create vendor. Please try again.')
    }
  } finally {
    creating.value = false
  }
}

async function handleDeactivate(vendorId, vendorName) {
  if (!confirm(`Deactivate vendor "${vendorName}"? This will disable their account and stall.`)) return
  try {
    await api.post(`/vendors/admin/${vendorId}/deactivate/`)
    await fetchVendors()
  } catch (e) {
    alert('Failed to deactivate vendor')
    console.error(e)
  }
}

function editVendor(vendor) {
  // TODO: Implement edit functionality
  alert(`Edit vendor: ${vendor.name} (not yet implemented)`)
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
.stack {
  display: flex;
  flex-direction: column;
}
.grid {
  display: grid;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.card-head h3 {
  margin: 0;
  font-size: 1.1rem;
}
.mb12 {
  margin-bottom: 12px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field label.small {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text);
}
.input {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.9rem;
  background: var(--color-bg);
  color: var(--color-text);
}
.input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-bg);
}
.input-error {
  border-color: var(--color-danger) !important;
}
.field-error {
  color: var(--color-danger);
  font-size: 0.75rem;
  margin-top: 4px;
  display: block;
}
.actions {
  white-space: nowrap;
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
.text-center { text-align: center; }
.py-8 { padding-top: 32px; padding-bottom: 32px; }
.py-12 { padding-top: 48px; padding-bottom: 48px; }
.mt8 { margin-top: 8px; }
.tiny { font-size: 0.75rem; }
.table-wrap { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--color-border); }
.table th { font-weight: 600; font-size: 0.75rem; text-transform: uppercase; color: var(--color-muted); letter-spacing: 0.05em; }
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }
.alert { padding: 12px 16px; border-radius: 6px; display: flex; align-items: center; gap: 12px; }
.alert-error { background: var(--color-danger-bg); border: 1px solid var(--color-danger); color: var(--color-danger); }
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.modal {
  animation: slideUp 0.2s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .admin-table-responsive {
    display: block;
    overflow-x: auto;
  }
  .page { padding: 16px; }
  .modal { width: 95%; margin: 10px; }
  .grid { grid-template-columns: 1fr !important; }
}
</style>