<template>
  <div>
    <h5>User Dashboard</h5>
    <button class="btn btn-sm btn-outline-primary mb-2" @click="loadDrives">Refresh Drives</button>
    <ul class="list-group">
      <li v-for="d in drives" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ d.title }}</strong>
          <div class="small text-muted">{{ d.description }}</div>
        </div>
        <div>
          <button class="btn btn-primary btn-sm" @click="apply(d.id)">Apply</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const drives = ref([])

async function loadDrives() {
  try {
    const res = await api.get('/drives')
    drives.value = Array.isArray(res.data) ? res.data.filter((drive) => drive.status === 'Approved' || !drive.status) : []
  } catch (e) {
    drives.value = []
  }
}

async function apply(id) {
  try {
    await api.post(`/drives/${id}/apply`)
    alert('Applied')
  } catch (e) {
    alert(e.response?.data?.message || 'Error')
  }
}

loadDrives()
</script>

<style scoped></style>
