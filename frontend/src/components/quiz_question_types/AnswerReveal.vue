<script setup lang="ts">
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import { computed } from 'vue'
import type { Card } from '../../config/types'

const props = defineProps<{
  card: Card
  userAnswer?: string | string[]
}>()

const emit = defineEmits<{
  continue: []
}>()

const hasUserAnswer = computed(() => {
  if (!props.userAnswer) return false
  if (Array.isArray(props.userAnswer)) {
    return props.userAnswer.length > 0
  }
  return props.userAnswer.trim() !== ''
})

const userAnswerDisplay = computed(() => {
  if (!props.userAnswer) return ''
  if (Array.isArray(props.userAnswer)) {
    return props.userAnswer
  }
  return props.userAnswer
})
</script>

<template>
  <div class="answer-section">
    <h3 class="wrong-header">❌ Incorrect!</h3>
    
    <div v-if="hasUserAnswer" class="user-answer">
      <p class="answer-label">Your answer:</p>
      <div v-if="Array.isArray(userAnswerDisplay)" class="user-keywords">
        <Chip 
          v-for="(keyword, index) in userAnswerDisplay" 
          :key="index" 
          :label="keyword"
          class="user-keyword-chip"
        />
        <span v-if="userAnswerDisplay.length === 0" class="no-answer">(no keywords guessed)</span>
      </div>
      <h2 v-else class="user-answer-title">{{ userAnswerDisplay }}</h2>
    </div>
    
    <div class="correct-answer">
      <p class="answer-label">The correct answer is:</p>
      <h2 class="answer-title">{{ card.title }}</h2>
      
      <div v-if="card.quick_facts && card.quick_facts.length > 0" class="answer-details">
        <ul class="facts-list">
          <li v-for="(fact, index) in card.quick_facts" :key="index">{{ fact }}</li>
        </ul>
      </div>
      
      <div v-if="card.keywords && card.keywords.length > 0" class="answer-details">
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
    
    <div class="answer-buttons">
      <Button 
        label="Continue" 
        icon="pi pi-arrow-right" 
        @click="emit('continue')"
        severity="secondary"
      />
    </div>
  </div>
</template>

<style scoped>
.answer-section {
  padding: 1.5rem;
  background: var(--surface-50);
  border-radius: 8px;
}

.wrong-header {
  color: #EF4444;
  text-align: center;
  font-size: 1.5rem;
  margin: 0 0 1.5rem 0;
}

.correct-answer {
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.answer-label {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  margin: 0 0 0.5rem 0;
}

.answer-title {
  font-size: 2rem;
  color: var(--theme-primary);
  margin: 0 0 1.5rem 0;
}

.answer-details {
  margin-top: 1.5rem;
}

.detail-label {
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

.keyword-chip {
  font-size: 0.7rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
  background: transparent !important;
  border: 2px solid #6366f1 !important;
  color: #6366f1 !important;
}

.facts-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.facts-list li {
  margin-bottom: 0.5rem;
}

.answer-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.user-answer {
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.user-answer-title {
  font-size: 1.5rem;
  color: #EF4444;
  margin: 0;
}

.user-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.user-keyword-chip {
  font-size: 0.7rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
  background: rgba(239, 68, 68, 0.2) !important;
  border: 2px solid #EF4444 !important;
  color: #EF4444 !important;
}

.no-answer {
  color: var(--text-color-secondary);
  font-style: italic;
}
</style>
