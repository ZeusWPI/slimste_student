<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import AutoComplete from 'primevue/autocomplete'
import Chip from 'primevue/chip'
import Message from 'primevue/message'
import type { Label } from '../config/types'
import { fetchWithCsrf } from '../utils/csrf'

const router = useRouter()
const labels = ref<Label[]>([])
const shareUsername = ref<{ [key: number]: string }>({})
const suggestedUsers = ref<{ [key: number]: { username: string }[] }>({})
const successMessage = ref('')
const errorMessage = ref('')

const fetchLabels = async () => {
  try {
    const response = await fetch('/api/labels/', {
      credentials: 'include'
    })
    if (response.ok) {
      labels.value = await response.json()
      // Initialize suggested users for each label
      labels.value.forEach(async (label) => {
        if (label.is_owner) {
          await searchUsers(label.id, '')
        }
      })
    }
  } catch (error) {
    console.error('Error fetching labels:', error)
  }
}

const searchUsers = async (labelId: number, query: string) => {
  try {
    const response = await fetch(`/api/users/search/?q=${encodeURIComponent(query)}`, {
      credentials: 'include'
    })
    if (response.ok) {
      suggestedUsers.value[labelId] = await response.json()
    }
  } catch (error) {
    console.error('Error searching users:', error)
  }
}

const onUserSearch = (labelId: number, event: any) => {
  const query = event.query !== undefined ? event.query : ''
  searchUsers(labelId, query)
}

const onInputFocus = (labelId: number) => {
  // Load top 5 users when focusing on input
  if (!suggestedUsers.value[labelId] || suggestedUsers.value[labelId].length === 0) {
    searchUsers(labelId, '')
  }
}

const shareLabel = async (labelId: number) => {
  let username = shareUsername.value[labelId]
  
  // Handle if it's an object from autocomplete
  if (typeof username === 'object' && username !== null) {
    username = (username as any).username
  }
  
  username = username?.trim()
  
  if (!username) {
    errorMessage.value = 'Please enter a username'
    return
  }

  try {
    const response = await fetchWithCsrf(`/api/labels/${labelId}/share/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username }),
    })

    if (response.ok) {
      successMessage.value = `Successfully shared with ${username}`
      shareUsername.value[labelId] = ''
      await fetchLabels()
      setTimeout(() => successMessage.value = '', 3000)
    } else {
      const error = await response.json()
      errorMessage.value = error.error || 'Failed to share label'
      setTimeout(() => errorMessage.value = '', 3000)
    }
  } catch (error) {
    console.error('Error sharing label:', error)
    errorMessage.value = 'Error sharing label'
    setTimeout(() => errorMessage.value = '', 3000)
  }
}

const unshareLabel = async (labelId: number, username: string) => {
  try {
    const response = await fetchWithCsrf(`/api/labels/${labelId}/unshare/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username }),
    })

    if (response.ok) {
      successMessage.value = `Removed ${username} from label`
      await fetchLabels()
      setTimeout(() => successMessage.value = '', 3000)
    } else {
      const error = await response.json()
      errorMessage.value = error.error || 'Failed to unshare label'
      setTimeout(() => errorMessage.value = '', 3000)
    }
  } catch (error) {
    console.error('Error unsharing label:', error)
    errorMessage.value = 'Error unsharing label'
    setTimeout(() => errorMessage.value = '', 3000)
  }
}

onMounted(() => {
  fetchLabels()
})

const goBack = () => {
  router.push('/labels')
}
</script>

<template>
  <div class="share-labels-page">
    <div class="header">
      <Button label="Back to Labels" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Share Labels</h1>
    </div>

    <Message v-if="successMessage" severity="success" :closable="false">{{ successMessage }}</Message>
    <Message v-if="errorMessage" severity="error" :closable="false">{{ errorMessage }}</Message>

    <div class="labels-list">
      <Card v-for="label in labels" :key="label.id" class="label-card">
        <template #title>
          <div class="label-header">
            <Chip :label="label.name" :style="{ backgroundColor: label.color, color: '#fff' }" />
            <span class="owner-badge">{{ label.is_owner ? 'Your Label' : `Owned by ${label.owner_username}` }}</span>
          </div>
        </template>
        <template #content>
          <div v-if="label.is_owner" class="share-section">
            <div class="shared-users">
              <h3>Shared with:</h3>
              <div v-if="label.shared_with_usernames && label.shared_with_usernames.length > 0" class="users-list">
                <div v-for="username in label.shared_with_usernames" :key="username" class="user-item">
                  <span>{{ username }}</span>
                  <Button 
                    icon="pi pi-times" 
                    severity="danger" 
                    text 
                    size="small"
                    @click="unshareLabel(label.id, username)"
                  />
                </div>
              </div>
              <p v-else class="no-shares">Not shared with anyone</p>
            </div>

            <div class="share-input">
              <AutoComplete
                v-model="shareUsername[label.id]"
                :suggestions="suggestedUsers[label.id] || []"
                @complete="onUserSearch(label.id, $event)"
                @click="onInputFocus(label.id)"
                optionLabel="username"
                placeholder="Enter username to share with"
                forceSelection
                completeOnFocus
                @keypress.enter="shareLabel(label.id)"
              />
              <Button 
                label="Share" 
                icon="pi pi-share-alt" 
                @click="shareLabel(label.id)"
                :disabled="!shareUsername[label.id]"
              />
            </div>
          </div>
          <div v-else class="shared-info">
            <p>This label is shared with you by {{ label.owner_username }}</p>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.share-labels-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0;
  color: var(--theme-primary);
}

.labels-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.label-card {
  width: 100%;
}

.label-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.owner-badge {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
}

.share-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.shared-users h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #4b5563;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.user-item span {
  font-weight: 500;
}

.no-shares {
  color: #9ca3af;
  font-style: italic;
  margin: 0;
}

.share-input {
  display: flex;
  gap: 0.75rem;
}

.share-input :deep(.p-autocomplete) {
  flex: 1;
}

.share-input :deep(.p-autocomplete-input) {
  width: 100%;
}

.shared-info {
  color: #6b7280;
}

.shared-info p {
  margin: 0;
}
</style>
