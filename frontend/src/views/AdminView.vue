<template>
  <div class="container py-4">
    <div v-if="!isLogged" class="text-center py-5">
      <div class="spinner-border text-primary mb-3" role="status"></div>
      <p class="text-muted">Preparing admin dashboard...</p>
      <div v-if="error" class="text-danger">{{ error }}</div>
    </div>

    <div v-else class="admin-shell">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
        <div>
          <h2 class="mb-1">Admin Dashboard</h2>
          <p class="text-muted mb-0">Manage placements, approvals, and platform users.</p>
        </div>
        <div class="btn-group" role="group">
          <button class="btn btn-outline-primary" :class="{ active: activeTab === 'home' }" @click="activeTab = 'home'">Home</button>
          <button class="btn btn-outline-primary" :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">Profile</button>
          <button class="btn btn-outline-primary" :class="{ active: activeTab === 'about' }" @click="activeTab = 'about'">About</button>
        </div>
      </div>

      <div v-if="activeTab === 'home'">
        <AdminDashboard />
      </div>

      <div v-else-if="activeTab === 'profile'" class="card">
        <div class="card-body">
          <h5 class="card-title">Admin Profile</h5>
          <p class="mb-2"><strong>Name:</strong> {{ profile?.name || 'Admin' }}</p>
          <p class="mb-2"><strong>Email:</strong> {{ profile?.email || '—' }}</p>
          <p class="mb-0"><strong>Role:</strong> {{ profile?.role || 'admin' }}</p>
        </div>
      </div>

      <div v-else-if="activeTab === 'about'" class="card">
        <div class="card-body">
          <h5 class="card-title">About Admin Portal</h5>
          <p class="mb-2">This portal helps administrators review company registrations, approve placement drives, manage student accounts, and generate reports.</p>
          <p class="mb-0">Use Home to access operations, Profile to view your account details, and About for portal guidance.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { setAuthToken } from '../services/api'
import AdminDashboard from '../components/AdminDashboard.vue'

const isLogged = ref(false)
const activeTab = ref('home')
const profile = ref(null)
const error = ref('')

async function loadProfile() {
  try {
    const res = await api.get('/me')
    profile.value = res.data
  } catch (e) {
    profile.value = null
  }
}

async function autoLogin() {
  const storedToken = localStorage.getItem('ppa_token')
  if (storedToken) {
    setAuthToken(storedToken)
    try {
      const res = await api.get('/me')
      if (res.data?.role === 'admin') {
        profile.value = res.data
        isLogged.value = true
        return
      }
    } catch (e) {
      // ignore and fall back to default admin login
    }
  }

  try {
    const res = await api.post('/login', {
      email: 'admin@institute.edu',
      password: 'adminpass',
    })
    if (res.data?.role === 'admin') {
      setAuthToken(res.data.access_token)
      localStorage.setItem('ppa_token', res.data.access_token)
      await loadProfile()
      isLogged.value = true
    }
  } catch (e) {
    error.value = e.response?.data?.message || 'Unable to access admin panel'
  }
}

onMounted(() => {
  autoLogin()
})
</script>

<style scoped>
.admin-shell .btn-group .btn.active {
  background-color: #0d6efd;
  color: #fff;
}
</style>
