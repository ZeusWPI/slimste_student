<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import FloatLabel from 'primevue/floatlabel'
import Select from 'primevue/select'
import Chip from 'primevue/chip'
import LabelSelector from './LabelSelector.vue'
import { iconOptions, type IconOption } from '../config/icons'
import type { Label, Props } from '../config/types'

const props = withDefaults(defineProps<Props>(), {
  initialTitle: '',
  initialIcon: () => iconOptions[0]!,
  initialLabels: () => [],
  initialQuickFacts: () => [],
  initialKeywords: () => [],
  submitLabel: 'Submit',
  loading: false
})

const emit = defineEmits<{
  submit: [data: { title: string; icon: string; labelIds: number[]; quickFacts: string[]; keywords: string[] }]
  cancel: []
}>()

const title = ref(props.initialTitle)
const icon = ref<IconOption>(props.initialIcon)
const selectedLabels = ref<Label[]>(props.initialLabels)
const quickFacts = ref<string[]>(props.initialQuickFacts)
const keywords = ref<string[]>(props.initialKeywords)
const availableLabels = ref<Label[]>([])
const newQuickFact = ref('')
const newKeyword = ref('')

watch(() => props.initialTitle, (newVal) => { title.value = newVal })
watch(() => props.initialIcon, (newVal) => { icon.value = newVal })
watch(() => props.initialLabels, (newVal) => { selectedLabels.value = newVal })
watch(() => props.initialQuickFacts, (newVal) => { quickFacts.value = newVal })
watch(() => props.initialKeywords, (newVal) => { keywords.value = newVal })

const addQuickFact = () => {
  if (newQuickFact.value.trim()) {
    quickFacts.value.push(newQuickFact.value.trim())
    newQuickFact.value = ''
  }
}

const removeQuickFact = (index: number) => {
  quickFacts.value.splice(index, 1)
}

const addKeyword = () => {
  if (newKeyword.value.trim()) {
    keywords.value.push(newKeyword.value.trim())
    newKeyword.value = ''
  }
}

const removeKeyword = (index: number) => {
  keywords.value.splice(index, 1)
}

const fetchLabels = async () => {
  try {
    const response = await fetch('/api/labels/')
    if (response.ok) {
      availableLabels.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching labels:', error)
  }
}

onMounted(() => {
  fetchLabels()
})

const handleSubmit = () => {
  if (!title.value) {
    alert('Please fill in the title')
    return
  }

  emit('submit', {
    title: title.value,
    icon: icon.value.class,
    labelIds: selectedLabels.value.map(l => l.id),
    quickFacts: quickFacts.value,
    keywords: keywords.value
  })
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <Card class="card-form">
    <template #content>
      <div class="form-fields">
        <FloatLabel>
          <InputText id="title" v-model="title" style="width: 100%" />
          <label for="title">Title</label>
        </FloatLabel>

        <div class="icon-field">
          <label for="icon">Select Icon</label>
          <Select 
            v-model="icon" 
            :options="iconOptions" 
            optionLabel="name" 
            placeholder="Select an icon"
            style="width: 100%"
          >
            <template #value="slotProps">
              <div v-if="slotProps.value" class="icon-option">
                <i :class="slotProps.value.class"></i>
                <span>{{ slotProps.value.name }}</span>
              </div>
              <span v-else>{{ slotProps.placeholder }}</span>
            </template>
            <template #option="slotProps">
              <div class="icon-option">
                <i :class="slotProps.option.class"></i>
                <span>{{ slotProps.option.name }}</span>
              </div>
            </template>
          </Select>
        </div>

        <div class="label-field">
          <label for="labels">Select Labels</label>
          <LabelSelector 
            v-model="selectedLabels" 
            :options="availableLabels"
            placeholder="Select labels"
          />
        </div>

        <div class="list-field">
          <label>Quick Facts</label>
          <div class="list-input">
            <InputText 
              v-model="newQuickFact" 
              placeholder="Add a quick fact" 
              @keyup.enter="addQuickFact"
              style="flex: 1"
            />
            <Button icon="pi pi-plus" @click="addQuickFact" />
          </div>
          <div v-if="quickFacts.length > 0" class="list-items">
            <Chip 
              v-for="(fact, index) in quickFacts" 
              :key="index" 
              :label="fact" 
              removable 
              @remove="removeQuickFact(index)"
            />
          </div>
        </div>

        <div class="list-field">
          <label>Keywords</label>
          <div class="list-input">
            <InputText 
              v-model="newKeyword" 
              placeholder="Add a keyword" 
              @keyup.enter="addKeyword"
              style="flex: 1"
            />
            <Button icon="pi pi-plus" @click="addKeyword" />
          </div>
          <div v-if="keywords.length > 0" class="list-items">
            <Chip 
              v-for="(keyword, index) in keywords" 
              :key="index" 
              :label="keyword" 
              removable 
              @remove="removeKeyword(index)"
            />
          </div>
        </div>

        <div class="form-actions">
          <Button label="Cancel" @click="handleCancel" severity="secondary" />
          <Button :label="submitLabel" icon="pi pi-check" @click="handleSubmit" :loading="loading" />
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.card-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-fields {
  padding-top: 1em;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.icon-field,
.label-field,
.list-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.icon-field label,
.label-field label,
.list-field label {
  font-weight: 500;
  color: var(--text-color);
}

.list-input {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.list-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.icon-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon-option i {
  font-size: 1.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
}
</style>
