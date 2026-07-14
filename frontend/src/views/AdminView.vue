<template>
  <div class="container py-4">
    <div v-if="!isLogged" class="text-center py-5">
      <div class="mb-4">
        <h2 class="mb-2">Admin Portal</h2>
        <p class="text-muted">Sign in with an institute admin account.</p>
      </div>
      <div class="mx-auto" style="max-width: 420px; text-align: left;">
        <AdminLogin @logged="onAdminLogged" />
      </div>
      <div v-if="error" class="text-danger mt-3">{{ error }}</div>
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
          <button class="btn btn-outline-danger" @click="isLogged = false; profile = null; error = ''">Logout</button>
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
import AdminLogin from '../components/AdminLogin.vue'

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
      // ignore and fall back to admin login form
    }
  }

  isLogged.value = false
  profile.value = null
  error.value = ''
}

function onAdminLogged(role = 'admin') {
  error.value = ''
  if (role === 'admin') {
    isLogged.value = true
    loadProfile()
    activeTab.value = 'home'
  } else {
    error.value = 'Admin accounts must use the admin login page.'
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
