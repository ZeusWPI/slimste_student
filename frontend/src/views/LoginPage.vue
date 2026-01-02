<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, register, isLoading } = useAuth()

const isRegisterMode = ref(false)
const username = ref('')
const password = ref('')
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  
  if (!username.value || !password.value) {
    error.value = 'Username and password are required'
    return
  }

  let success = false
  
  if (isRegisterMode.value) {
    success = await register(username.value, password.value, '')
    if (!success) {
      error.value = 'Registration failed. Username may already exist.'
    }
  } else {
    success = await login(username.value, password.value)
    if (!success) {
      error.value = 'Invalid username or password'
    }
  }

  if (success) {
    router.push('/')
  }
}

const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  error.value = ''
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <Card class="login-card">
        <template #title>
          <div class="title-section">
            <i class="pi pi-graduation-cap" style="font-size: 2rem; color: #6366f1;"></i>
            <h1>{{ isRegisterMode ? 'Register' : 'Login' }}</h1>
          </div>
        </template>
        <template #content>
          <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
          
          <form @submit.prevent="handleSubmit" class="login-form">
            <div class="field">
              <label for="username">Username</label>
              <InputText
                id="username"
                v-model="username"
                placeholder="Enter username"
                :disabled="isLoading"
                autocomplete="username"
              />
            </div>

            <div class="field">
              <label for="password">Password</label>
              <Password
                id="password"
                v-model="password"
                placeholder="Enter password"
                :disabled="isLoading"
                :feedback="isRegisterMode"
                toggleMask
                autocomplete="current-password"
              />
            </div>

            <Button
              type="submit"
              :label="isRegisterMode ? 'Register' : 'Login'"
              :loading="isLoading"
              icon="pi pi-sign-in"
              class="submit-button"
            />

            <div class="toggle-mode">
              <span>{{ isRegisterMode ? 'Already have an account?' : "Don't have an account?" }}</span>
              <Button
                :label="isRegisterMode ? 'Login' : 'Register'"
                @click="toggleMode"
                text
                :disabled="isLoading"
              />
            </div>
          </form>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-card {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
}

.title-section h1 {
  margin: 0;
  color: #1f2937;
  font-size: 1.8rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-weight: 600;
  color: #4b5563;
  font-size: 0.95rem;
}

.field input {
  width: 100%;
}

.field :deep(.p-password),
.field :deep(.p-password input) {
  width: 100%;
}

.submit-button {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
}

.toggle-mode {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
}
</style>
