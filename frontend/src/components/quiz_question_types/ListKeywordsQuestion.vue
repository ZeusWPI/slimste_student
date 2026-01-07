<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Chip from 'primevue/chip'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import type { Card } from '../../config/types'

const props = defineProps<{
  card: Card
  questionNumber: number
  totalQuestions: number
  showLabels: boolean
}>()

const emit = defineEmits<{
  correct: []
  wrong: [answer: string[]]
}>()

const userInput = ref('')
const revealedKeywords = ref<Set<string>>(new Set())

const allRevealed = computed(() => {
  if (!props.card.keywords) return true
  return props.card.keywords.every(k => revealedKeywords.value.has(k.toLowerCase()))
})

watch(allRevealed, (revealed) => {
  if (revealed && props.card.keywords && props.card.keywords.length > 0) {
    // All keywords guessed correctly
    setTimeout(() => {
      emit('correct')
    }, 500)
  }
})

watch(() => props.card, () => {
  userInput.value = ''
  revealedKeywords.value = new Set()
}, { deep: true })

const checkGuess = () => {
  if (!userInput.value.trim() || !props.card.keywords) return
  
  const guess = userInput.value.trim().toLowerCase()
  const matchedKeyword = props.card.keywords.find(k => k.toLowerCase() === guess)
  
  if (matchedKeyword && !revealedKeywords.value.has(matchedKeyword.toLowerCase())) {
    revealedKeywords.value.add(matchedKeyword.toLowerCase())
  }
  
  userInput.value = ''
}

const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    checkGuess()
  }
}

const passQuestion = () => {
  // Convert revealed keywords set to array
  const guessedKeywords = Array.from(revealedKeywords.value)
  emit('wrong', guessedKeywords)
}

const isRevealed = (keyword: string) => {
  return revealedKeywords.value.has(keyword.toLowerCase())
}
</script>

<template>
  <div class="question-content">
    <div class="debug-header">
      <span class="question-type-badge list-keywords">List Keywords Question</span>
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
        <div class="title-section">
          <i :class="card.icon" class="card-icon"></i>
          <h2 class="card-title">{{ card.title }}</h2>
        </div>
        <p class="prompt-text">List all the keywords for this card:</p>
      </div>

      <div class="keywords-display">
        <div 
          v-for="keyword in card.keywords" 
          :key="keyword"
          class="keyword-item"
          :class="{ revealed: isRevealed(keyword) }"
        >
          <span v-if="isRevealed(keyword)">{{ keyword }}</span>
          <span v-else class="blurred">{{ keyword }}</span>
        </div>
      </div>

      <div class="guess-section">
        <div class="input-group">
          <InputText
            v-model="userInput"
            placeholder="Type a keyword..."
            @keypress="handleKeyPress"
            class="keyword-input"
            :disabled="allRevealed"
          />
          <Button 
            label="Check" 
            @click="checkGuess"
            :disabled="!userInput.trim() || allRevealed"
            icon="pi pi-check"
          />
        </div>
        
        <div class="progress-info">
          <p>{{ revealedKeywords.size }} / {{ card.keywords?.length || 0 }} keywords found</p>
        </div>

        <Button 
          label="Pass (Skip)" 
          @click="passQuestion"
          severity="secondary"
          outlined
          icon="pi pi-forward"
          class="pass-button"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.question-content {
  width: 100%;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.question-type-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.question-type-badge.list-keywords {
  background: #EC4899;
}

.question-number {
  font-size: 1rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0;
  flex: 1;
  text-align: center;
}

.labels-container {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.label-chip-header {
  font-size: 0.75rem;
}

.question-prompt {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.card-icon {
  font-size: 2.5rem;
  color: #6366f1;
}

.card-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.prompt-text {
  font-size: 1.1rem;
  color: #4b5563;
  margin: 0;
}

.keywords-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  padding: 1.5rem;
  border-radius: 0.75rem;
}

.keyword-item {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 2px solid #6366f1;
}

.keyword-item.revealed {
  background: transparent;
  color: #6366f1;
}

.keyword-item:not(.revealed) {
  background: #6366f1;
  color: white;
}

.blurred {
  filter: blur(10px);
  user-select: none;
}

.guess-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.input-group {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  max-width: 500px;
}

.keyword-input {
  flex: 1;
}

.progress-info {
  font-size: 1rem;
  color: #6b7280;
  font-weight: 500;
}

.progress-info p {
  margin: 0;
}

.pass-button {
  margin-top: 1rem;
}
</style>
