<template>
  <div class="card mb-4">
    <div class="card-header">Create Placement Drive</div>
    <div class="card-body">
      <form @submit.prevent="submitDrive">
        <div class="mb-3">
          <label class="form-label">Drive Title</label>
          <input v-model="title" class="form-control" placeholder="e.g. Software Engineer Internship" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea v-model="description" class="form-control" rows="3" placeholder="Describe the role and requirements" required></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Eligibility</label>
          <input v-model="eligibility" class="form-control" placeholder="e.g. CGPA >= 7.0, B.Tech final year" />
        </div>
        <div class="mb-3">
          <label class="form-label">Drive Date</label>
          <input v-model="driveDate" class="form-control" type="date" />
        </div>
        <div class="mb-3">
          <label class="form-label">Application Deadline</label>
          <input v-model="applicationDeadline" class="form-control" type="datetime-local" />
        </div>
        <button class="btn btn-primary" :disabled="loading">{{ loading ? 'Creating...' : 'Create Drive' }}</button>
      </form>
      <div v-if="message" class="alert alert-info mt-3 mb-0">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const emit = defineEmits(['created'])

const title = ref('')
const description = ref('')
const eligibility = ref('')
const driveDate = ref('')
const applicationDeadline = ref('')
const message = ref('')
const loading = ref(false)

async function submitDrive() {
  loading.value = true
  message.value = ''

  try {
    await api.post('/company/create_drive', {
      title: title.value,
      description: description.value,
      eligibility: eligibility.value,
      drive_date: driveDate.value,
      application_deadline: applicationDeadline.value,
    })
    message.value = 'Drive created successfully and is pending admin approval.'
    title.value = ''
    description.value = ''
    eligibility.value = ''
    driveDate.value = ''
    applicationDeadline.value = ''
    emit('created')
  } catch (e) {
    message.value = e.response?.data?.message || 'Could not create drive'
  } finally {
    loading.value = false
  }
}

</script>
