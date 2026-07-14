<template>
  <div class="container py-4">
    <h2 v-if="!isLogged">User Login</h2>

    <div class="row">
      <div class="col-12">
        <UserLogin v-if="!isLogged" @logged="onLogged" />
        <div v-else>
          <button @click="logout" class="btn btn-danger mb-3">Logout</button>
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import UserLogin from '../components/UserLogin.vue'
import api, { setAuthToken } from '../services/api'

const isLogged = ref(false)
const router = useRouter()

function logout() {
  localStorage.removeItem('ppa_token')
  setAuthToken(null)
  isLogged.value = false
  router.push('/')
}

function onLogged(role = 'student') {
  const token = localStorage.getItem('ppa_token')
  if (!token) {
    logout()
    return
  }
  setAuthToken(token)
  if (role === 'admin') {
    setAuthToken(null)
    router.push('/admin')
    return
  }

  isLogged.value = true
  if (role === 'company') {
    router.push('/user/company')
  } else {
    router.push('/user')
  }
}

onMounted(async () => {
  const token = localStorage.getItem('ppa_token')
  if (token) {
    setAuthToken(token)
    try {
      const res = await api.get('/me')
      onLogged(res.data.role)
    } catch (e) {
      logout()
    }
  }
})
</script>

<style scoped>
</style>
