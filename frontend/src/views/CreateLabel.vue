<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import FloatLabel from 'primevue/floatlabel'
import ColorPicker from 'primevue/colorpicker'

const router = useRouter()

const name = ref('')
const color = ref('3B82F6')
const saving = ref(false)

const createLabel = async () => {
  if (!name.value) {
    alert('Please enter a label name')
    return
  }

  saving.value = true
  try {
    const response = await fetch('/api/labels/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name.value,
        color: '#' + color.value,
      }),
    })

    if (response.ok) {
      router.push('/cards')
    } else {
      alert('Failed to create label')
    }
  } catch (error) {
    console.error('Error creating label:', error)
    alert('Error creating label')
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
      <h1>Create New Label</h1>
    </div>

    <Card class="create-form">
      <template #content>
        <div class="form-fields">
          <FloatLabel>
            <InputText id="name" v-model="name" style="width: 100%" />
            <label for="name">Label Name</label>
          </FloatLabel>

          <div class="color-field">
            <label for="color">Label Color</label>
            <div class="color-picker-wrapper">
              <ColorPicker v-model="color" format="hex" />
              <div 
                class="color-preview" 
                :style="{ backgroundColor: '#' + color }"
              >
                <span>{{ name || 'Preview' }}</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <Button label="Cancel" @click="goBack" severity="secondary" />
            <Button label="Create Label" icon="pi pi-check" @click="createLabel" :loading="saving" />
          </div>
        </div>
      </template>
    </Card>
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

.create-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.color-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.color-field label {
  font-weight: 500;
  color: var(--text-color);
}

.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.color-preview {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  text-align: center;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
}
</style>
