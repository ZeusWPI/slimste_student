<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import CardForm from '../components/CardForm.vue'

const router = useRouter()
const saving = ref(false)

const createCard = async (data: { title: string; icon: string; labelIds: number[]; quickFacts: string[]; keywords: string[] }) => {
  saving.value = true
  try {
    const response = await fetch('/api/cards/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: data.title,
        icon: data.icon,
        label_ids: data.labelIds,
        quick_facts: data.quickFacts,
        keywords: data.keywords,
      }),
    })

    if (response.ok) {
      router.push('/cards')
    } else {
      alert('Failed to create card')
    }
  } catch (error) {
    console.error('Error creating card:', error)
    alert('Error creating card')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/cards')
}
</script>

<template>
  <div class="create-page">
    <div class="header">
      <Button label="Back to Cards" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Create New Card</h1>
    </div>

    <CardForm 
      submit-label="Create Card"
      :loading="saving"
      @submit="createCard"
      @cancel="goBack"
    />
  </div>
</template>

<style scoped>
.create-page {
  width: 100%;
  padding: 1rem;
}

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

h1 {
  color: var(--theme-primary);
  margin: 0;
}
</style>
