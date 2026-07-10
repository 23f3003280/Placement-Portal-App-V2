<template>
  <div class="card">
    <div class="card-header">Student Applications</div>
    <div class="card-body">
      <div v-if="loading" class="text-muted">Loading applications...</div>
      <div v-else>
        <div class="table-responsive">
          <table class="table table-sm mb-0">
            <thead>
              <tr>
                <th>Student</th>
                <th>Email</th>
                <th>Drive</th>
                <th>Status</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.application_id">
                <td>{{ app.student_name || app.student_id }}</td>
                <td>{{ app.email || '—' }}</td>
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
                  <button class="btn btn-sm btn-primary" @click="updateStatus(app)">Update</button>
                </td>
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="5" class="text-center py-3 text-muted">No applications found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const applications = ref([])
const statusMap = ref({})
const loading = ref(false)

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

onMounted(loadApplications)
</script>
