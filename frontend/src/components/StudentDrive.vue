<template>
  <div class="card mb-4">
    <div class="card-header">Approved Placement Drives</div>
    <div class="card-body">
      <div class="input-group mb-3">
        <input v-model="query" @keyup.enter="loadDrives" class="form-control" placeholder="Search drives or eligibility" />
        <button class="btn btn-primary" @click="loadDrives" type="button">Search</button>
      </div>

      <div class="list-group">
        <div v-for="drive in drives" :key="drive.id" class="list-group-item d-flex justify-content-between align-items-start">
          <div>
            <h6>{{ drive.title }}</h6>
            <p class="mb-1 text-muted">{{ drive.description }}</p>
            <div class="small">Company: {{ drive.company_name || 'Unknown' }}</div>
            <div v-if="drive.eligibility" class="small text-secondary">Eligibility: {{ eligibilityText(drive.eligibility) }}</div>
          </div>
          <button class="btn btn-outline-success btn-sm" @click="apply(drive.id)">Apply</button>
        </div>
        <div v-if="drives.length === 0" class="list-group-item text-center text-muted">
          No approved drives found.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const drives = ref([])
const query = ref('')

function eligibilityText(eligibility) {
  if (!eligibility || typeof eligibility !== 'object') return 'None'
  return Object.entries(eligibility)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ')
}

async function loadDrives() {
  try {
    const res = await api.get('/drives', { params: { q: query.value } })
    drives.value = res.data
  } catch (e) {
    drives.value = []
  }
}

async function apply(id) {
  try {
    await api.post(`/drives/${id}/apply`)
    alert('Applied successfully')
    await loadDrives()
  } catch (e) {
    alert(e.response?.data?.message || 'Application failed')
  }
}

onMounted(loadDrives)
</script>

<style scoped>
</style>
