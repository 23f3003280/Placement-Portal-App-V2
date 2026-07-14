<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>Notifications</span>
      <button class="btn btn-sm btn-outline-secondary" @click="loadNotifications">Refresh</button>
    </div>
    <div class="card-body p-0">
      <div v-if="loading" class="p-3 text-muted">Loading notifications...</div>
      <div v-else-if="notifications.length === 0" class="p-3 text-muted">No notifications yet.</div>
      <div v-else class="list-group list-group-flush">
        <div v-for="item in notifications" :key="item.id" class="list-group-item">
          <div class="d-flex justify-content-between align-items-start gap-2">
            <div>
              <strong>{{ item.title }}</strong>
              <div class="small text-muted">{{ item.message }}</div>
              <div class="small text-secondary">{{ formatDate(item.created_at) }}</div>
            </div>
            <span class="badge bg-secondary">{{ item.type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const notifications = ref([])
const loading = ref(false)

function formatDate(value) {
  if (!value) return '—'
  const dateValue = new Date(value)
  if (Number.isNaN(dateValue.getTime())) return value
  return dateValue.toLocaleString()
}

async function loadNotifications() {
  loading.value = true
  try {
    const res = await api.get('/notifications')
    notifications.value = res.data || []
  } catch (e) {
    notifications.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadNotifications)
</script>

<style scoped>
.notification-list .list-group-item {
  word-break: break-word;
}
</style>
