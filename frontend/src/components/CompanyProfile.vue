<template>
  <div>
    <h3>Company Profile</h3>
    <div v-if="loading" class="alert alert-info">Loading...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    
    <form @submit.prevent="saveProfile" v-if="company">
      <div class="mb-3">
        <label for="companyName" class="form-label">Company Name</label>
        <input type="text" class="form-control" id="companyName" v-model="form.name">
      </div>
      <div class="mb-3">
        <label for="contactName" class="form-label">Contact Person Name</label>
        <input type="text" class="form-control" id="contactName" v-model="form.contact_name">
      </div>
      <div class="mb-3">
        <label for="hrContact" class="form-label">HR Contact (Email/Phone)</label>
        <input type="text" class="form-control" id="hrContact" v-model="form.hr_contact">
      </div>
      <div class="mb-3">
        <label for="website" class="form-label">Website</label>
        <input type="text" class="form-control" id="website" v-model="form.website">
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Login Email</label>
        <input type="email" class="form-control" id="email" v-model="form.email">
      </div>
      
      <button type="submit" class="btn btn-primary">Save Changes</button>
      <router-link to="/user/company" class="btn btn-secondary ms-2">Back to Dashboard</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api, { updateCompanyProfile } from '../services/api';

const company = ref(null);
const form = ref({
  name: '',
  contact_name: '',
  hr_contact: '',
  website: '',
  email: ''
});
const loading = ref(true);
const error = ref(null);
const success = ref(null);

async function fetchCompanyProfile() {
  loading.value = true;
  error.value = null;
  try {
    const response = await api.get('/me');
    const userData = response.data;
    if (userData.role === 'company' && userData.company) {
      company.value = userData.company;
      form.value.name = userData.company.name;
      form.value.hr_contact = userData.company.hr_contact;
      form.value.website = userData.company.website;
      form.value.email = userData.email;
      form.value.contact_name = userData.name;
    } else {
      throw new Error('Not a company account.');
    }
  } catch (e) {
    error.value = 'Failed to fetch company profile. ' + (e.response?.data?.message || e.message);
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  loading.value = true;
  error.value = null;
  success.value = null;
  try {
    const response = await updateCompanyProfile(form.value);
    success.value = response.data.message;
    // Refresh data after save
    fetchCompanyProfile();
  } catch (e) {
    error.value = 'Failed to update profile. ' + (e.response?.data?.message || e.message);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchCompanyProfile);
</script>

<style scoped>
</style>
