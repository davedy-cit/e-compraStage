<script setup>
import { computed } from 'vue'

defineProps(['order'])
defineEmits(['click'])

const formatPrice = (price) => `₱${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2 })}`

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}

const fulfillmentIcon = (code) => code === 'DELIVERY' ? '🛵' : '🏪'

const getStatusClass = (code) => {
  if (code === 'COMPLETED') return 'badge-ok'
  if (code === 'CANCELLED') return 'badge-danger'
  if (code === 'PENDING_PAYMENT') return 'badge-warn'
  return 'badge-info'
}

const vendorName = computed(() => props.order.vendor_name || props.order.vendor?.name || 'Unknown Vendor')
const stallLocation = computed(() => props.order.stall_location || props.order.vendor?.stall_location || '—')
const statusDisplay = computed(() => props.order.status_display || props.order.status_code)
const itemCount = computed(() => props.order.items?.length || 0)
</script>

<template>
  <div class="card" style="cursor: pointer; transition: box-shadow 0.2s;" @click="$emit('click')" @keydown.enter.space="$emit('click')" tabindex="0" role="button">
    <div class="card-head row-between">
      <div>
        <h4 class="mb0">{{ vendorName }}</h4>
        <p class="tiny muted mb0">📍 {{ stallLocation }}</p>
      </div>
      <span class="badge" :class="getStatusClass(props.order.status_code)">
        {{ statusDisplay }}
      </span>
    </div>
    <dl class="kv" style="margin-top: 8px; grid-template-columns: auto 1fr;">
      <dt>{{ formatDate(props.order.created_at) }}</dt>
      <dd class="text-right">{{ formatPrice(props.order.total_amount) }}</dd>
      <dt>{{ fulfillmentIcon(props.order.fulfillment_code) }} {{ props.order.fulfillment_code === 'DELIVERY' ? 'Delivery' : 'Pickup' }}</dt>
      <dd class="text-right">{{ itemCount }} item{{ itemCount > 1 ? 's' : '' }}</dd>
    </dl>
    <div class="card-foot row-between" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--color-line);">
      <span class="tiny muted">View details →</span>
      <span class="badge badge-tiny badge-info">{{ props.order.fulfillment_code === 'DELIVERY' ? '🛵 Delivery' : '🏪 Pickup' }}</span>
    </div>
  </div>
</template>