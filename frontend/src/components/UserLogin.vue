<template>
  <div>
    <h5>{{ mode === 'login' ? 'User Login' : 'User Registration' }}</h5>
    <div class="mb-3 d-flex gap-2">
      <button class="btn" :class="mode === 'login' ? 'btn-primary' : 'btn-outline-secondary'" @click="setMode('login')" type="button">Login</button>
      <button class="btn" :class="mode === 'register' ? 'btn-primary' : 'btn-outline-secondary'" @click="setMode('register')" type="button">Register</button>
    </div>

    <form @submit.prevent="submit">
      <div v-if="mode === 'register'" class="mb-2">
        <input v-model="name" class="form-control" placeholder="Name" />
      </div>
      <div class="mb-2">
        <input v-model="email" class="form-control" placeholder="Email" />
      </div>
      <div class="mb-2">
        <input v-model="password" type="password" class="form-control" placeholder="Password" />
      </div>
      <div v-if="mode === 'register'" class="mb-2">
        <select v-model="role" class="form-select">
          <option value="student">Student</option>
          <option value="company">Company</option>
        </select>
      </div>
      <div class="mb-2">
        <button class="btn btn-success" type="submit">{{ mode === 'login' ? 'Submit Login' : 'Submit Registration' }}</button>
      </div>
    </form>

    <div v-if="error" class="text-danger mt-2">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api, { setAuthToken } from '../services/api'

const mode = ref('login')
const name = ref('')
const email = ref('')
const password = ref('')
const role = ref('student')
const error = ref(null)

const emit = defineEmits(['logged'])

function setMode(newMode) {
  mode.value = newMode
  error.value = null
}

async function submit() {
  error.value = null
  try {
    if (mode.value === 'login') {
      const res = await api.post('/login', { email: email.value, password: password.value })
      const currentRole = res.data?.role
      if (currentRole === 'admin') {
        setAuthToken(null)
        error.value = 'Admin accounts must use the admin login page.'
        return
      }
      const token = res.data.access_token
      setAuthToken(token)
      localStorage.setItem('ppa_token', token)
      emit('logged', currentRole)
      return
    }

    await api.post('/register', { name: name.value, email: email.value, password: password.value, role: role.value })
    const res = await api.post('/login', { email: email.value, password: password.value })
    const currentRole = res.data?.role || role.value
    if (currentRole === 'admin') {
      setAuthToken(null)
      error.value = 'Admin accounts must use the admin login page.'
      return
    }
    const token = res.data.access_token
    setAuthToken(token)
    localStorage.setItem('ppa_token', token)
    emit('logged', currentRole)
  } catch (e) {
    error.value = e.response?.data?.message || (mode.value === 'login' ? 'Login failed' : 'Registration failed')
  }
}
</script>
<style scoped></style>
