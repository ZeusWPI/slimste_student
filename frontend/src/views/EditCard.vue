<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from 'primevue/button'
import CardForm from '../components/CardForm.vue'
import { iconOptions, type IconOption } from '../config/icons'
import type { Label } from '../config/types'

const router = useRouter()
const route = useRoute()

const initialTitle = ref('')
const initialIcon = ref<IconOption>(iconOptions[0]!)
const initialLabels = ref<Label[]>([])
const initialQuickFacts = ref<string[]>([])
const initialKeywords = ref<string[]>([])
const saving = ref(false)
const loading = ref(true)
const isOwner = ref(true)

const fetchCard = async () => {
  const cardId = route.params.id
  try {
    const response = await fetch(`/api/cards/${cardId}/`)
    if (response.ok) {
      const card = await response.json()
      
      // Check if user is the owner
      if (card.is_owner === false) {
        alert('You can only edit cards you created')
        router.push('/cards')
        return
      }
      
      isOwner.value = card.is_owner !== false
      initialTitle.value = card.title
      
      const matchedIcon = iconOptions.find(opt => opt.class === card.icon)
      initialIcon.value = matchedIcon ?? iconOptions[0]!
      
      initialLabels.value = card.labels || []
      initialQuickFacts.value = card.quick_facts || []
      initialKeywords.value = card.keywords || []
    } else {
      alert('Failed to load card')
      router.push('/cards')
    }
  } catch (error) {
    console.error('Error fetching card:', error)
    alert('Error loading card')
    router.push('/cards')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCard()
})

const updateCard = async (data: { title: string; icon: string; labelIds: number[]; quickFacts: string[]; keywords: string[] }) => {
  saving.value = true
  const cardId = route.params.id
  try {
    const response = await fetch(`/api/cards/${cardId}/`, {
      method: 'PATCH',
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
      const error = await response.json()
      alert(error.error || 'Failed to update card')
    }
  } catch (error) {
    console.error('Error updating card:', error)
    alert('Error updating card')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/cards')
}
</script>

<template>
  <div class="edit-page">
    <div class="header">
      <Button label="Back to Cards" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Edit Card</h1>
    </div>

    <div v-if="loading" class="loading">Loading card...</div>

    <CardForm 
      v-else
      :initial-title="initialTitle"
      :initial-icon="initialIcon"
      :initial-labels="initialLabels"
      :initial-quick-facts="initialQuickFacts"
      :initial-keywords="initialKeywords"
      submit-label="Update Card"
      :loading="saving"
      @submit="updateCard"
      @cancel="goBack"
    />
  </div>
</template>

<style scoped>
.edit-page {
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

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: var(--text-color-secondary);
}
</style>
