<script setup lang="ts">
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, logout } = useAuth()

const goToCards = () => {
  router.push('/cards')
}

const goToQuiz = () => {
  router.push('/quiz')
}

const goToQuizHistory = () => {
  router.push('/quiz/history')
}

const handleLogout = async () => {
  await logout()
  router.push('/login')
}
</script>

<template>
  <div class="start-page">
    <div class="header">
      <h1>Welcome to Slimste Student</h1>
      <div class="user-info">
        <span v-if="user" class="username">{{ user.username }}</span>
        <Button label="Logout" icon="pi pi-sign-out" @click="handleLogout" text />
      </div>
    </div>
    
    <div class="cards-grid">
      <Card class="welcome-card">
        <template #title>Card Collection</template>
        <template #content>
          <p>Browse, create, and manage your study cards with custom labels.</p>
        </template>
        <template #footer>
          <Button label="View Cards" icon="pi pi-arrow-right" @click="goToCards" />
        </template>
      </Card>

      <Card class="welcome-card">
        <template #title>Quiz Mode</template>
        <template #content>
          <p>Test your knowledge! Select labels and answer questions to beat the clock.</p>
        </template>
        <template #footer>
          <div class="card-footer-actions">
            <Button label="Start Quiz" icon="pi pi-play" @click="goToQuiz" />
            <Button label="View History" icon="pi pi-history" outlined @click="goToQuizHistory" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.start-page {
  width: 100%;
  padding: 1rem;
  text-align: center;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 0 1rem;
}

.header h1 {
  color: var(--theme-primary);
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-weight: 600;
  color: #4b5563;
}

h1 {
  color: var(--theme-primary);
  margin-bottom: 2rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  max-width: 800px;
  margin: 0 auto;
}

.card-footer-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.welcome-card {
  max-width: 600px;
  margin: 0 auto;
}
</style>
