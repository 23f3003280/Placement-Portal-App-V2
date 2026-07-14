<template>
  <div class="card shadow-sm border-0">
    <div class="card-body p-4">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div>
          <h5 class="mb-1">Admin Login</h5>
          <p class="text-muted mb-0">Use only institute admin credentials.</p>
        </div>
        
      </div>

      <form @submit.prevent="submit">
        <div class="mb-3">
          <input v-model="email" class="form-control" placeholder="Admin Email" required />
        </div>
        <div class="mb-3">
          <input v-model="password" type="password" class="form-control" placeholder="Password" required />
        </div>
        <div class="d-grid">
          <button class="btn btn-primary" type="submit" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            Login as Admin
          </button>
        </div>
      </form>

      <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api, { setAuthToken } from '../services/api'

const emit = defineEmits(['logged', 'cancel'])

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

async function submit() {
  error.value = ''
  isLoading.value = true
  try {
    const res = await api.post('/login', { email: email.value, password: password.value })
    if (res.data?.role !== 'admin') {
      setAuthToken(null)
      error.value = 'Admin accounts must use the admin login page.'
      return
    }

    const token = res.data.access_token
    setAuthToken(token)
    localStorage.setItem('ppa_token', token)
    emit('logged', res.data.role)
  } catch (e) {
    error.value = e.response?.data?.message || 'Admin login failed'
  } finally {
    isLoading.value = false
  }
}
</script>
