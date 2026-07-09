<template>
  <div class="container py-4">
    <h2>User</h2>
    <div class="row">
      <div class="col-12">
        <UserLogin v-if="!isLogged" @logged="onLogged" />
        <div v-else>
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UserLogin from '../components/UserLogin.vue'

const isLogged = ref(false)
const router = useRouter()

function onLogged(role = 'student') {
  isLogged.value = true
  if (role === 'company') {
    router.push('/user/company')
  } else {
    router.push('/user')
  }
}
</script>

<style scoped>
</style>
