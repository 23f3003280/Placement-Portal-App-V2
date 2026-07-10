<template>
  <div class="student-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4>Student Dashboard</h4>
        <p class="text-muted mb-0">Browse approved placement drives and track your applications.</p>
      </div>
      <div class="btn-group">
        <button class="btn btn-outline-primary" @click="go('drives')">Drives</button>
        <button class="btn btn-outline-primary" @click="go('history')">History</button>
        <button class="btn btn-outline-primary" @click="go('profile')">Profile</button>
      </div>
    </div>

    <div class="row mb-4">
      <div class="col-md-3" v-for="card in cards" :key="card.label">
        <div class="card text-center h-100">
          <div class="card-body">
            <h6 class="text-secondary">{{ card.label }}</h6>
            <p class="display-6 mb-0">{{ card.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <StudentDrive />

    <div class="mt-4 card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="mb-0">Application Status</h5>
          <button class="btn btn-sm btn-outline-primary" @click="exportApplications" :disabled="exporting">
            {{ exporting ? 'Preparing...' : 'Export Applications (CSV)' }}
          </button>
        </div>
        <div v-if="exportMessage" class="alert alert-info py-2">{{ exportMessage }}</div>
        <div class="list-group">
          <div v-for="app in recentApplications" :key="app.id" class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <strong>{{ app.drive_title || 'Drive #' + app.drive_id }}</strong>
              <div class="small text-muted">{{ app.company_name || 'Company unknown' }}</div>
            </div>
            <span :class="['badge', statusBadge(app.status)]">{{ app.status }}</span>
          </div>
          <div v-if="recentApplications.length === 0" class="list-group-item text-center text-muted">
            No applications yet.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import StudentDrive from './StudentDrive.vue'

const router = useRouter()
const drives = ref([])
const applications = ref([])
const exporting = ref(false)
const exportMessage = ref('')

const cards = computed(() => [
  { label: 'Approved Drives', value: drives.value.length },
  { label: 'Applications', value: applications.value.length },
  { label: 'Selected', value: applications.value.filter((a) => a.status === 'Selected').length },
  { label: 'Shortlisted', value: applications.value.filter((a) => a.status === 'Shortlisted').length },
])

const recentApplications = computed(() => applications.value.slice(0, 5))

function statusBadge(status) {
  if (status === 'Selected') return 'bg-success'
  if (status === 'Shortlisted') return 'bg-info'
  if (status === 'Rejected') return 'bg-danger'
  return 'bg-secondary'
}

function go(page) {
  router.push(`/user/${page}`)
}

async function loadDrives() {
  try {
    const res = await api.get('/drives')
    drives.value = res.data
  } catch (e) {
    drives.value = []
  }
}

async function loadApplications() {
  try {
    const res = await api.get('/applications')
    applications.value = res.data
  } catch (e) {
    applications.value = []
  }
}

async function exportApplications() {
  exporting.value = true
  exportMessage.value = ''
  try {
    const res = await api.post('/student/export-applications')
    exportMessage.value = `Export created at ${res.data.path}`
  } catch (e) {
    exportMessage.value = e.response?.data?.message || 'Export failed'
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadDrives(), loadApplications()])
})
</script>

<style scoped>
.student-dashboard .card {
  min-height: 120px;
}
</style>
