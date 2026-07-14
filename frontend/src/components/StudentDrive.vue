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
          <div class="d-flex gap-2">
            <button class="btn btn-outline-info btn-sm" @click="openDriveDetails(drive.id)">Show Details</button>
          </div>
        </div>
        <div v-if="drives.length === 0" class="list-group-item text-center text-muted">
          No approved drives found.
        </div>
      </div>
    </div>
  </div>

  <div v-if="selectedDrive" class="card border-primary mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>Company Profile + Drive Details</span>
      <button class="btn btn-sm btn-outline-secondary" @click="selectedDrive = null">Close</button>
    </div>
    <div class="card-body">
      <div class="row g-4">
        <div class="col-md-5">
          <h6 class="text-uppercase text-secondary">Company Profile</h6>
          <p class="mb-2"><strong>Name:</strong> {{ selectedDrive.company?.name || '—' }}</p>
          <p class="mb-2"><strong>Status:</strong> {{ selectedDrive.company?.approved ? 'Approved' : 'Pending Approval' }}</p>
          <p class="mb-2"><strong>HR Contact:</strong> {{ selectedDrive.company?.hr_contact || '—' }}</p>
          <p class="mb-0"><strong>Website:</strong> {{ selectedDrive.company?.website || '—' }}</p>
        </div>
        <div class="col-md-7">
          <h6 class="text-uppercase text-secondary">Drive Details</h6>
          <p class="mb-2"><strong>Title:</strong> {{ selectedDrive.drive?.title || '—' }}</p>
          <p class="mb-2"><strong>Description:</strong> {{ selectedDrive.drive?.description || '—' }}</p>
          <p class="mb-2"><strong>Eligibility:</strong> {{ eligibilityText(selectedDrive.drive?.eligibility) }}</p>
          <p class="mb-2"><strong>Drive Date:</strong> {{ formatDate(selectedDrive.drive?.drive_date) }}</p>
          <p class="mb-2"><strong>Application Deadline:</strong> {{ formatDate(selectedDrive.drive?.application_deadline) }}</p>
          <p class="mb-3"><strong>Status:</strong> {{ selectedDrive.drive?.status || '—' }}</p>
          <button class="btn btn-outline-success btn-sm" @click="apply(selectedDrive.drive?.id)">Apply to This Drive</button>
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
const selectedDrive = ref(null)

function eligibilityText(eligibility) {
  if (!eligibility || typeof eligibility !== 'object') return 'None'
  return Object.entries(eligibility)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ')
}

function formatDate(value) {
  if (!value) return '—'
  const dateValue = new Date(value)
  if (Number.isNaN(dateValue.getTime())) return value
  return dateValue.toLocaleDateString()
}

async function loadDrives() {
  try {
    const res = await api.get('/drives', { params: { q: query.value } })
    drives.value = res.data
  } catch (e) {
    drives.value = []
  }
}

async function openDriveDetails(id) {
  try {
    const res = await api.get(`/drives/${id}/details`)
    selectedDrive.value = res.data
  } catch (e) {
    selectedDrive.value = null
    alert(e.response?.data?.message || 'Could not load drive details')
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
