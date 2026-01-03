<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import type { Label } from '../config/types'

const router = useRouter()

const labels = ref<Label[]>([])
const loading = ref(true)

const fetchLabels = async () => {
  try {
    const response = await fetch('/api/labels/')
    if (response.ok) {
      labels.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching labels:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLabels()
})

const goBack = () => {
  router.push('/cards')
}

const goToCreate = () => {
  router.push('/labels/create')
}

const goToShare = () => {
  router.push('/labels/share')
}

const deleteLabel = async (id: number) => {
  if (!confirm('Are you sure you want to delete this label?')) {
    return
  }

  try {
    const response = await fetch(`/api/labels/${id}/`, {
      method: 'DELETE',
    })

    if (response.ok) {
      labels.value = labels.value.filter(label => label.id !== id)
    } else {
      alert('Failed to delete label')
    }
  } catch (error) {
    console.error('Error deleting label:', error)
    alert('Error deleting label')
  }
}
</script>

<template>
  <div class="labels-page">
    <div class="header">
      <Button label="Back to Cards" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Manage Labels</h1>
      <div class="header-actions">
        <Button label="Share Labels" icon="pi pi-share-alt" @click="goToShare" outlined />
        <Button label="Create Label" icon="pi pi-plus" @click="goToCreate" />
      </div>
    </div>

    <div v-if="loading" class="loading">Loading labels...</div>

    <div v-else class="labels-list">
      <Card v-for="label in labels" :key="label.id" class="label-item">
        <template #content>
          <div class="label-content">
            <div class="label-info">
              <Chip 
                :label="label.name" 
                :style="{ 
                  backgroundColor: label.color, 
                  color: '#fff',
                  fontSize: '1rem',
                  padding: '0.5rem 1rem'
                }"
              />
              <span class="card-count">
                <i class="pi pi-bookmark"></i>
                {{ label.card_count || 0 }} card{{ (label.card_count || 0) !== 1 ? 's' : '' }}
              </span>
            </div>
            <Button 
              icon="pi pi-trash" 
              severity="danger" 
              text 
              rounded
              @click="deleteLabel(label.id)"
            />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.labels-page {
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
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: var(--text-color-secondary);
}

.labels-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.label-item {
  width: 100%;
}

.label-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
}

.label-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.card-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.9rem;
}

.card-count i {
  font-size: 0.85rem;
}
</style>
