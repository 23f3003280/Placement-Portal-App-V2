<template>
  <div class="company-dashboard">
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h4>Company Dashboard</h4>
        <p class="text-muted mb-0">Manage your company profile, placement drives, and student applications.</p>
      </div>
      <button class="btn btn-outline-secondary btn-sm" @click="loadData">Refresh</button>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-header">Company Details</div>
          <div class="card-body">
            <p class="mb-2"><strong>Name:</strong> {{ profile?.company?.name || profile?.name || '—' }}</p>
            <p class="mb-2"><strong>Email:</strong> {{ profile?.email || '—' }}</p>
            <p class="mb-2"><strong>Status:</strong> {{ profile?.company?.approved ? 'Approved' : 'Pending Approval' }}</p>
            <p class="mb-0"><strong>Active:</strong> {{ profile?.is_active ? 'Yes' : 'No' }}</p>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Created Placement Drives</span>
            <input v-model="searchQuery" class="form-control form-control-sm w-auto" style="max-width: 220px;" placeholder="Search all fields" @input="loadDrives" />
          </div>
          <div class="card-body p-0">
            <table class="table table-sm mb-0">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Drive Date</th>
                  <th>Applicants</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.drive_id">
                  <td>{{ drive.title }}</td>
                  <td>{{ drive.status }}</td>
                  <td>{{ drive.drive_date || '—' }}</td>
                  <td>{{ drive.applicant_count }}</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="openEdit(drive)">Edit</button>
                      <button class="btn btn-outline-danger" @click="confirmDelete(drive)">Delete</button>
                      <button class="btn btn-outline-secondary" @click="openDetails(drive)">View</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="5" class="text-center py-3 text-muted">No drives created yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedDrive" class="modal d-block bg-dark bg-opacity-50" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit Drive' : 'Drive Details' }}</h5>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="isEditing">
              <div class="mb-3">
                <label class="form-label">Title</label>
                <input v-model="selectedDrive.title" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="selectedDrive.description" class="form-control" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Eligibility</label>
                <input v-model="selectedDrive.eligibilityText" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Drive Date</label>
                <input v-model="selectedDrive.drive_date" class="form-control" type="date" />
              </div>
              <div class="mb-3">
                <label class="form-label">Application Deadline</label>
                <input v-model="selectedDrive.application_deadline" class="form-control" type="datetime-local" />
              </div>
            </div>
            <div v-else>
              <p><strong>Title:</strong> {{ selectedDrive.title }}</p>
              <p><strong>Status:</strong> {{ selectedDrive.status }}</p>
              <p><strong>Description:</strong> {{ selectedDrive.description || '—' }}</p>
              <p><strong>Eligibility:</strong> {{ selectedDrive.eligibility || '—' }}</p>
              <p><strong>Drive Date:</strong> {{ selectedDrive.drive_date || '—' }}</p>
              <p><strong>Application Deadline:</strong> {{ selectedDrive.application_deadline || '—' }}</p>
              <p><strong>Applicants:</strong> {{ selectedDrive.applicant_count }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">Close</button>
            <button v-if="isEditing" class="btn btn-primary" @click="saveDrive">Save</button>
          </div>
        </div>
      </div>
    </div>

    <CreateDrive @created="loadData" />
    <CompanyApplications />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import CreateDrive from './CreateDrive.vue'
import CompanyApplications from './CompanyApplications.vue'

const profile = ref({})
const drives = ref([])
const searchQuery = ref('')
const selectedDrive = ref(null)
const isEditing = ref(false)

async function loadProfile() {
  try {
    const res = await api.get('/me')
    profile.value = res.data
  } catch (e) {
    profile.value = {}
  }
}

async function loadDrives() {
  try {
    const res = await api.get('/company/drives', { params: { q: searchQuery.value } })
    drives.value = res.data
  } catch (e) {
    drives.value = []
  }
}

async function loadData() {
  await Promise.all([loadProfile(), loadDrives()])
}

function openEdit(drive) {
  isEditing.value = true
  selectedDrive.value = {
    ...drive,
    eligibilityText: typeof drive.eligibility === 'string' ? drive.eligibility : (drive.eligibility ? JSON.stringify(drive.eligibility) : ''),
  }
}

function openDetails(drive) {
  isEditing.value = false
  selectedDrive.value = { ...drive }
}

function closeModal() {
  selectedDrive.value = null
  isEditing.value = false
}

async function saveDrive() {
  if (!selectedDrive.value) return
  try {
    await api.patch(`/company/drives/${selectedDrive.value.drive_id}`, {
      title: selectedDrive.value.title,
      description: selectedDrive.value.description,
      eligibility: selectedDrive.value.eligibilityText,
      drive_date: selectedDrive.value.drive_date,
      application_deadline: selectedDrive.value.application_deadline,
    })
    closeModal()
    await loadDrives()
  } catch (e) {
    alert(e.response?.data?.message || 'Could not update drive')
  }
}

function confirmDelete(drive) {
  if (window.confirm(`Delete drive "${drive.title}"?`)) {
    deleteDrive(drive.drive_id)
  }
}

async function deleteDrive(id) {
  try {
    await api.delete(`/company/drives/${id}`)
    await loadDrives()
  } catch (e) {
    alert(e.response?.data?.message || 'Could not delete drive')
  }
}

onMounted(loadData)
</script>

<style scoped>
.company-dashboard .card {
  min-height: 120px;
}
</style>
