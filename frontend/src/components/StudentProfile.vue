<template>
  <div class="card mb-4">
    <div class="card-header">Student Profile</div>
    <div class="card-body">
      <form @submit.prevent="saveProfile">
        <div class="mb-3">
          <label class="form-label">Name</label>
          <input v-model="profile.name" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="profile.email" class="form-control" disabled />
        </div>
        <div class="mb-3">
          <label class="form-label">Phone</label>
          <input v-model="profile.phone" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Bio</label>
          <textarea v-model="profile.bio" class="form-control" rows="3"></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Education</label>
          <input v-model="profile.education" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Skills</label>
          <input v-model="profile.skills" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Resume</label>
          <input type="file" @change="uploadResume" class="form-control" />
          <div v-if="profile.resume_file" class="mt-2">
            Uploaded: <strong>{{ profile.resume_file }}</strong>
          </div>
        </div>
        <button class="btn btn-primary" type="submit">Save Profile</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const profile = ref({
  name: '',
  email: '',
  phone: '',
  bio: '',
  education: '',
  skills: '',
  resume_file: '',
})

async function loadProfile() {
  try {
    const res = await api.get('/me')
    profile.value = {
      name: res.data.name,
      email: res.data.email,
      phone: res.data.profile?.phone || '',
      bio: res.data.profile?.bio || '',
      education: res.data.profile?.education || '',
      skills: res.data.profile?.skills || '',
      resume_file: res.data.profile?.resume_file || '',
    }
  } catch (e) {
    profile.value = {
      name: '',
      email: '',
      phone: '',
      bio: '',
      education: '',
      skills: '',
      resume_file: '',
    }
  }
}

async function saveProfile() {
  try {
    await api.post('/me', {
      name: profile.value.name,
      phone: profile.value.phone,
      bio: profile.value.bio,
      education: profile.value.education,
      skills: profile.value.skills,
    })
    alert('Profile saved')
  } catch (e) {
    alert(e.response?.data?.message || 'Save failed')
  }
}

async function uploadResume(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const form = new FormData()
  form.append('resume', file)
  try {
    const res = await api.post('/me/resume', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    profile.value.resume_file = res.data.resume_file
    alert('Resume uploaded')
  } catch (e) {
    alert(e.response?.data?.message || 'Upload failed')
  }
}

onMounted(loadProfile)
</script>

<style scoped>
</style>
