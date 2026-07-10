<template>
  <div class="card mb-4">
    <div class="card-header">Placement History</div>
    <div class="card-body">
      <div class="list-group">
        <div v-for="item in history" :key="item.id" class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>{{ item.drive_title || 'Drive #' + item.drive_id }}</strong>
              <div class="small text-muted">Company: {{ item.company_name || 'Unknown' }}</div>
              <div class="small">Status: {{ item.status }}</div>
            </div>
            <span class="text-muted small">{{ formatDate(item.applied_on) }}</span>
          </div>
        </div>
        <div v-if="history.length === 0" class="list-group-item text-center text-muted">
          No placement history found.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const history = ref([])

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleDateString()
}

async function loadHistory() {
  try {
    const res = await api.get('/applications')
    history.value = res.data.filter((item) => item.status === 'Selected' || item.status === 'Rejected')
  } catch (e) {
    history.value = []
  }
}

onMounted(loadHistory)
</script>

<style scoped>
</style>
