<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import type { Card } from '../../config/types'

const props = defineProps<{
  card: Card
  questionNumber: number
  totalQuestions: number
  showLabels: boolean
}>()

const emit = defineEmits<{
  correct: []
  wrong: [answer: string]
}>()

const userAnswer = ref('')

const checkAnswer = () => {
  const correct = userAnswer.value.trim().toLowerCase() === props.card.title.toLowerCase()
  if (correct) {
    emit('correct')
  } else {
    emit('wrong', userAnswer.value.trim())
  }
}
</script>

<template>
  <div class="question-content">
    <div class="debug-header">
      <span class="question-type-badge">Title Question</span>
      <p class="question-number">Question {{ questionNumber }} of {{ totalQuestions }}</p>
      <div class="labels-container">
        <Chip 
          v-if="showLabels && card.labels && card.labels.length > 0"
          v-for="label in card.labels" 
          :key="label.id" 
          :label="label.name" 
          :style="{ backgroundColor: label.color, color: '#fff' }"
          class="label-chip-header"
        />
      </div>
    </div>
    
    <div class="question-prompt">
      <div class="question-type">
        <h3>What is the title of this card?</h3>
        <div class="hints-section">
          <div v-if="card.quick_facts && card.quick_facts.length > 0">
            <ul class="facts-list">
              <li v-for="(fact, index) in card.quick_facts" :key="index">{{ fact }}</li>
            </ul>
          </div>
          <div v-if="card.keywords && card.keywords.length > 0" style="margin-top: 1rem;">
            <div class="keywords-list">
              <Chip 
                v-for="(keyword, index) in card.keywords" 
                :key="index" 
                :label="keyword"
                class="keyword-chip"
              />
            </div>
          </div>
        </div>
        <input 
          type="text" 
          v-model="userAnswer" 
          @keyup.enter="checkAnswer"
          placeholder="Type your answer..."
          class="text-input"
        />
        <Button 
          label="Submit Answer" 
          icon="pi pi-check" 
          @click="checkAnswer"
          :disabled="!userAnswer.trim()"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.question-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.question-number {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  margin: 0;
  flex: 1;
  text-align: center;
}

.question-type-badge {
  background: #8B5CF6;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.labels-container {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  min-width: 100px;
}

.label-chip-header {
  font-size: 0.7rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
}

.question-prompt {
  padding: 2rem;
}

.question-type {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.question-type h3 {
  font-size: 1.3rem;
  color: var(--theme-primary);
  margin: 0;
  text-align: center;
}

.hints-section {
  width: 100%;
  background: var(--surface-50);
  padding: 1.5rem;
  border-radius: 8px;
}

.hint-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.labels-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-chip {
  font-size: 0.7rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
  background: transparent !important;
  border: 2px solid #6366f1 !important;
  color: #6366f1 !important;
}

.label-chip-small {
  font-size: 0.75rem !important;
  padding: 0.3rem 0.6rem !important;
}

.facts-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.facts-list li {
  margin-bottom: 0.5rem;
}

.text-input {
  width: 100%;
  padding: 0.75rem;
  font-size: 1.1rem;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  transition: border-color 0.3s;
}

.text-input:focus {
  outline: none;
  border-color: var(--theme-primary);
}
</style>
