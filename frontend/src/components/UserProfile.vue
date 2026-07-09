<template>
  <div>
    <h5>Profile</h5>
    <div v-if="profile">
      <p><strong>Email:</strong> {{ profile.email }}</p>
      <p><strong>Name:</strong> {{ profile.name }}</p>
    </div>
    <div v-else>
      <p>No profile data.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const profile = ref(null)

onMounted(async () => {
  try {
    // no profile endpoint implemented yet; attempt to read token and show basic info
    const token = localStorage.getItem('ppa_token')
    if (!token) return
    // simple decode attempt removed for simplicity; call /applications to confirm
    const res = await api.get('/applications')
    profile.value = { email: 'you@domain', name: 'User' }
  } catch (e) {
    profile.value = null
  }
})
</script>

<style scoped></style>
