<template>
  <div class="student-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4>Hi {{ studentName }} !!</h4>
        <p class="text-muted mb-0">Browse current placement drives and track your applications.</p>
      </div>
      <div class="btn-group">
        
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
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Company Name</th>
                <th>Drive Name</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>{{ app.company_name || 'Unknown' }}</td>
                <td>{{ app.drive_title || 'Drive #' + app.drive_id }}</td>
                <td>{{ formatDate(app.applied_on) }}</td>
                <td>
                  <span :class="['badge', statusBadge(app.status)]">{{ app.status }}</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-info" @click="openDriveDetails(app.drive_id)">Show Details</button>
                </td>
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="5" class="text-center text-muted py-3">
                  No applications yet.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <NotificationCenter />
    </div>

    <div v-if="selectedDrive" class="modal d-block bg-dark bg-opacity-50" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Drive Details</h5>
            <button class="btn-close" @click="selectedDrive = null"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedDrive.loading" class="text-muted">Loading...</div>
            <div v-else>
              <p><strong>Title:</strong> {{ selectedDrive.drive?.title }}</p>
              <p><strong>Company:</strong> {{ selectedDrive.company?.name }}</p>
              <p><strong>Description:</strong> {{ selectedDrive.drive?.description }}</p>
              <p><strong>Eligibility:</strong> {{ selectedDrive.drive?.eligibility }}</p>
              <p><strong>Drive Date:</strong> {{ formatDate(selectedDrive.drive?.drive_date) }}</p>
              <p><strong>Application Deadline:</strong> {{ formatDate(selectedDrive.drive?.application_deadline) }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="selectedDrive = null">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import StudentDrive from './StudentDrive.vue'
import NotificationCenter from './NotificationCenter.vue'


const router = useRouter()
const drives = ref([])
const applications = ref([])
const exporting = ref(false)
const exportMessage = ref('')
const isLogged = ref(true)
const selectedDrive = ref(null)
const studentName = ref('Student') // Default name

async function loadStudentProfile() {
  try {
    const res = await api.get('/me')
    if (res.data && res.data.name) {
      studentName.value = res.data.name
    }
  } catch (e) {
    console.error('Error loading student profile:', e)
  }
}

const cards = computed(() => [
  { label: 'Current Drives', value: drives.value.length },
  { label: 'Applications', value: applications.value.length },
  { label: 'Selected', value: applications.value.filter((a) => a.status === 'Selected').length },
  { label: 'Shortlisted', value: applications.value.filter((a) => a.status === 'Shortlisted').length },
  { label: 'Rejected', value: applications.value.filter((a) => a.status === 'Rejected').length },

])

function statusBadge(status) {
  if (status === 'Selected') return 'bg-success'
  if (status === 'Shortlisted') return 'bg-info'
  if (status === 'Rejected') return 'bg-danger'
  return 'bg-secondary'
}

function go(page) {
  router.push(`/user/${page}`)
}

function formatDate(value) {
  if (!value) return '—'
  const dateValue = new Date(value)
  if (Number.isNaN(dateValue.getTime())) return value
  return dateValue.toLocaleString()
}

async function openDriveDetails(id) {
  selectedDrive.value = { loading: true };
  try {
    const res = await api.get(`/drives/${id}/details`);
    selectedDrive.value = res.data;
  } catch (e) {
    alert(e.response?.data?.message || 'Could not load drive details');
    selectedDrive.value = null;
  }
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
  await Promise.all([loadDrives(), loadApplications(), loadStudentProfile()])
})
</script>

<style scoped>
.student-dashboard .card {
  min-height: 120px;
}
.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}
</style>
