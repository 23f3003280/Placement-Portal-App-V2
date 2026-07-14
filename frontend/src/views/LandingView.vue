<template>
  <div class="landing-container container py-5">
    <div v-if="!showAbout">
      <h1 class="mb-4">Placement Portal</h1>
      <p>Choose your role to continue</p>
      <div class="d-flex gap-3">
        <router-link to="/admin" class="btn btn-primary">Admin</router-link>
        <router-link to="/user" class="btn btn-secondary">Student / Company</router-link>
        <button @click="showAbout = true" class="btn btn-info">About</button>
      </div>
    </div>

    <div v-else class="about-section">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>About This Web App</h2>
        <button @click="showAbout = false" class="btn btn-close"></button>
      </div>

      <h4>Purpose</h4>
      <p>
        This web application serves as a comprehensive Student Placement Portal, designed to streamline and manage the campus placement process. It connects students, companies, and the college administration on a single platform, simplifying communication and coordination for recruitment activities.
      </p>

      <h4>Features</h4>
      <ul>
        <li><strong>Role-Based Access:</strong> Separate and secure portals for Students, Company Representatives, and Administrators.</li>
        <li><strong>Admin Dashboard:</strong> Administrators can manage company registrations, approve placement drives, and oversee student applications.</li>
        <li><strong>Company Portal:</strong> Companies can register, post job openings, and view applications from interested students.</li>
        <li><strong>Student Portal:</strong> Students can create profiles, browse available job opportunities, and apply for placements.</li>
      </ul>

      <h4>Advantages</h4>
      <ul>
        <li><strong>Efficiency:</strong> Centralizes all placement-related activities, reducing manual effort and paperwork.</li>
        <li><strong>Transparency:</strong> Provides clear and immediate access to information for all stakeholders.</li>
        <li><strong>Accessibility:</strong> A web-based platform accessible from anywhere, at any time.</li>
      </ul>

      <div class="creator-info mt-5 text-center">
        <p>Created with ❤️ by <strong>Ritik Soni</strong>, a web dev enthusiast.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const showAbout = ref(false);
</script>

<style scoped>
.landing-container {
  max-width: 900px;
}

.about-section {
  text-align: left;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.about-section h2, .about-section h4 {
  color: #333;
}

.about-section h4 {
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.creator-info {
  font-style: italic;
  color: #555;
}
</style>
