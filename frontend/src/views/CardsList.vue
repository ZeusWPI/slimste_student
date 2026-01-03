<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import LabelSelector from '../components/LabelSelector.vue'
import type { Label, Card as CardData } from '../config/types'

const router = useRouter()

const cards = ref<CardData[]>([])
const availableLabels = ref<Label[]>([])
const selectedLabelFilters = ref<Label[]>([])
const loading = ref(true)

const filteredCards = computed(() => {
  if (selectedLabelFilters.value.length === 0) {
    return cards.value
  }
  return cards.value.filter(card => 
    selectedLabelFilters.value.some(filter => 
      card.labels.some(label => label.id === filter.id)
    )
  )
})

const fetchLabels = async () => {
  try {
    const response = await fetch('/api/labels/', {
      credentials: 'include'
    })
    if (response.ok) {
      availableLabels.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching labels:', error)
  }
}

const fetchCards = async () => {
  try {
    const response = await fetch('/api/cards/', {
      credentials: 'include'
    })
    if (response.ok) {
      cards.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching cards:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLabels()
  fetchCards()
})

const goBack = () => {
  router.push('/')
}

const goToCreate = () => {
  router.push('/cards/create')
}

const goToManageLabels = () => {
  router.push('/labels')
}

const deleteCard = async (id: number) => {
  if (!confirm('Are you sure you want to delete this card?')) {
    return
  }

  try {
    const response = await fetch(`/api/cards/${id}/`, {
      method: 'DELETE',
    })

    if (response.ok) {
      // Remove card from local list
      cards.value = cards.value.filter(card => card.id !== id)
    } else {
      alert('Failed to delete card')
    }
  } catch (error) {
    console.error('Error deleting card:', error)
    alert('Error deleting card')
  }
}
</script>

<template>
  <div class="cards-page">
    <div class="header">
      <Button label="Back to Home" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Cards Collection</h1>
      <div class="header-actions">
        <Button label="Manage Labels" icon="pi pi-tag" @click="goToManageLabels" severity="secondary" />
        <Button label="Create Card" icon="pi pi-plus" @click="goToCreate" />
      </div>
    </div>
    
    <div class="filter-section">
      <LabelSelector 
        v-model="selectedLabelFilters" 
        :options="availableLabels"
        placeholder="Filter by labels"
      />
    </div>

    <div v-if="loading" class="loading">Loading cards...</div>
    
    <div v-else class="cards-grid">
      <Card v-for="card in filteredCards" :key="card.id" class="card-item">
        <template #title>
          <div class="card-header">
            <div class="card-title">
              <i :class="card.icon"></i>
              {{ card.title }}
            </div>
            <div v-if="card.labels.length > 0" class="card-labels">
              <Chip 
                v-for="label in card.labels" 
                :key="label.id" 
                :label="label.name" 
                :style="{ backgroundColor: label.color, color: '#fff' }"
                class="label-chip"
              />
            </div>
          </div>
        </template>
        <template #content>
          <div v-if="card.quick_facts && card.quick_facts.length > 0" class="card-section">
            <ul class="facts-list">
              <li v-for="(fact, index) in card.quick_facts" :key="index">{{ fact }}</li>
            </ul>
          </div>
          
          <div v-if="card.keywords && card.keywords.length > 0" class="card-section keywords-section">
            <div class="keywords-list">
              <Chip 
                v-for="(keyword, index) in card.keywords" 
                :key="index" 
                :label="keyword"
                :style="{ backgroundColor: '#4444ff', color: '#fff' }"
                class="keyword-chip"
              />
            </div>
          </div>
        </template>
        <template #footer>
          <div class="card-actions">
            <Button 
              v-if="card.is_owner !== false" 
              label="Edit" 
              icon="pi pi-pencil" 
              outlined 
              @click="router.push(`/cards/${card.id}/edit`)"
            />
            <Button 
              v-if="card.is_owner !== false" 
              label="Delete" 
              icon="pi pi-trash" 
              severity="danger" 
              outlined 
              @click="deleteCard(card.id)"
            />
            <span v-if="card.is_owner === false" class="shared-badge">
              <i class="pi pi-eye"></i> View Only (Shared by {{ card.owner_username }})
            </span>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.cards-page {
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
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.filter-section {
  margin-bottom: 1.5rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: var(--text-color-secondary);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.card-item {
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.card-title i {
  font-size: 1.5rem;
}

.card-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  align-items: flex-start;
}

.label-chip {
  font-size: 0.7rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  align-items: center;
}

.shared-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.85rem;
  font-style: italic;
}

.card-section {
  margin-top: 1rem;
}

.card-section h4 {
  margin: 0 0 0.5rem 0;
  color: var(--theme-primary);
  font-size: 0.9rem;
}

.keywords-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keywords-section h4 {
  margin: 0;
}

.facts-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.facts-list li {
  margin-bottom: 0.25rem;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-chip {
  font-size: 0.7rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
}
</style>
