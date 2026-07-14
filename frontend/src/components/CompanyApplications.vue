<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>Student Applications</span>
      <div class="d-flex align-items-center">
        <input v-model="searchQuery" class="form-control form-control-sm me-2" placeholder="Search..." style="width: 200px;" />
        <div class="btn-group btn-group-sm">
          <button class="btn" :class="filter === 'All' ? 'btn-primary' : 'btn-outline-secondary'" @click="filter = 'All'">All</button>
          <button class="btn" :class="filter === 'Shortlisted' ? 'btn-primary' : 'btn-outline-secondary'" @click="filter = 'Shortlisted'">Shortlisted</button>
          <button class="btn" :class="filter === 'Selected' ? 'btn-primary' : 'btn-outline-secondary'" @click="filter = 'Selected'">Selected</button>
          <button class="btn" :class="filter === 'Rejected' ? 'btn-primary' : 'btn-outline-secondary'" @click="filter = 'Rejected'">Rejected</button>
        </div>
      </div>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-muted">Loading applications...</div>
      <div v-else>
        <div class="table-responsive">
          <table class="table table-sm mb-0">
            <thead>
              <tr>
                <th>Student</th>
                <th>Email</th>
                <th>Applied On</th>
                <th>Drive</th>
                <th>Status</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplications" :key="app.application_id">
                <td>{{ app.student_name || app.student_id }}</td>
                <td>{{ app.email || '—' }}</td>
                <td>{{ formatDate(app.applied_on) }}</td>
                <td>{{ app.drive_title || app.drive_id }}</td>
                <td>
                  <select v-model="statusMap[app.application_id]" class="form-select form-select-sm">
                    <option value="Applied">Applied</option>
                    <option value="Shortlisted">Shortlisted</option>
                    <option value="Selected">Selected</option>
                    <option value="Rejected">Rejected</option>
                  </select>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-info me-2" @click="openStudentProfile(app.student_id)">Open Profile</button>
                  <button class="btn btn-sm btn-primary" @click="updateStatus(app)">Update</button>
                </td>
              </tr>
              <tr v-if="filteredApplications.length === 0">
                <td colspan="6" class="text-center py-3 text-muted">No applications found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Student Profile Modal -->
  <div v-if="showStudentModal" class="modal d-block bg-dark bg-opacity-50" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Student Profile</h5>
          <button class="btn-close" @click="closeStudentModal"></button>
        </div>
        <div class="modal-body">
          <div v-if="studentLoading" class="alert alert-info">Loading profile...</div>
          <div v-if="studentError" class="alert alert-danger">{{ studentError }}</div>
          <div v-if="selectedStudent">
            <p><strong>Name:</strong> {{ selectedStudent.name }}</p>
            <p><strong>Email:</strong> {{ selectedStudent.email }}</p>
            <div v-if="selectedStudent.profile">
              <p v-for="(value, key) in selectedStudent.profile" :key="key">
                <strong>{{ key.charAt(0).toUpperCase() + key.slice(1) }}:</strong> {{ value }}
              </p>
            </div>
            <a v-if="selectedStudent.resume_file" :href="getStudentResumeUrl(selectedStudent.id)" target="_blank" class="btn btn-success">Download Resume</a>
            <p v-else class="text-muted">No resume uploaded.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeStudentModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api, { getStudentProfile, getStudentResumeUrl } from '../services/api'

const applications = ref([])
const statusMap = ref({})
const loading = ref(false)
const searchQuery = ref('')
const filter = ref('All')

const selectedStudent = ref(null)
const studentLoading = ref(false)
const studentError = ref(null)
const showStudentModal = ref(false)

const filteredApplications = computed(() => {
  let filtered = applications.value

  if (filter.value !== 'All') {
    filtered = filtered.filter(app => app.status === filter.value)
  }

  if (searchQuery.value) {
    const lowerQuery = searchQuery.value.toLowerCase()
    filtered = filtered.filter(app =>
      (app.student_name || '').toLowerCase().includes(lowerQuery) ||
      (app.email || '').toLowerCase().includes(lowerQuery) ||
      (app.drive_title || '').toLowerCase().includes(lowerQuery)
    )
  }

  return filtered
})

function formatDate(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

async function loadApplications() {
  loading.value = true
  try {
    const res = await api.get('/company/applications')
    applications.value = res.data
    const map = {}
    res.data.forEach((app) => {
      map[app.application_id] = app.status
    })
    statusMap.value = map
  } catch (e) {
    applications.value = []
  } finally {
    loading.value = false
  }
}

async function updateStatus(app) {
  try {
    await api.patch(`/applications/${app.application_id}/status`, {
      status: statusMap.value[app.application_id],
    })
    await loadApplications()
  } catch (e) {
    alert(e.response?.data?.message || 'Could not update status')
  }
}

async function openStudentProfile(studentId) {
  studentLoading.value = true
  studentError.value = null
  selectedStudent.value = null
  showStudentModal.value = true
  try {
    const response = await getStudentProfile(studentId)
    selectedStudent.value = response.data
  } catch (e) {
    studentError.value = 'Failed to load student profile. ' + (e.response?.data?.message || e.message)
  } finally {
    studentLoading.value = false
  }
}

function closeStudentModal() {
  showStudentModal.value = false
  selectedStudent.value = null
  studentError.value = null
}

onMounted(loadApplications)
</script>
