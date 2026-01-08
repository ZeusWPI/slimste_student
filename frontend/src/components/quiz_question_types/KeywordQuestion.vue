<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Chip from 'primevue/chip'
import type { Card } from '../../config/types'

const props = defineProps<{
  card: Card
  allCards: Card[]
  questionNumber: number
  totalQuestions: number
  showLabels: boolean
}>()

const emit = defineEmits<{
  correct: []
  wrong: [answer?: string, correctAnswer?: string[]]
}>()

const selectedOption = ref<string | null>(null)
const options = ref<string[]>([])
const correctKeywordsInQuestion = ref<string[]>([])

const generateOptions = () => {
  if (!props.card.keywords) return
  
  // Mix correct keywords with wrong ones from other cards
  const correctKeywords = [...props.card.keywords]
  // Store which correct keywords are in this question
  correctKeywordsInQuestion.value = correctKeywords.slice(0, 2)
  const wrongKeywords: string[] = []
  
  // Collect keywords from other cards, excluding ones that are also on current card
  for (const card of props.allCards) {
    if (card.id !== props.card.id && card.keywords) {
      // Filter out keywords that exist on the current card
      const uniqueKeywords = card.keywords.filter(k => !correctKeywords.includes(k))
      wrongKeywords.push(...uniqueKeywords)
    }
  }
  
  // Shuffle and select wrong options
  const shuffledWrong = wrongKeywords.sort(() => Math.random() - 0.5)
  const numWrong = Math.min(3, shuffledWrong.length)
  const generatedOptions = [...correctKeywordsInQuestion.value, ...shuffledWrong.slice(0, numWrong)]
  
  options.value = generatedOptions.sort(() => Math.random() - 0.5)
}

onMounted(() => {
  generateOptions()
})

watch(() => props.card, () => {
  selectedOption.value = null
  generateOptions()
}, { deep: true })

const checkAnswer = (option: string) => {
  selectedOption.value = option
  const isCorrect = props.card.keywords?.includes(option)
  if (isCorrect) {
    emit('correct')
  } else {
    emit('wrong', option, correctKeywordsInQuestion.value)
  }
}
</script>

<template>
  <div class="question-content">
    <div class="debug-header">
      <span class="question-type-badge">Keyword Question</span>
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
        <h3>Which keyword belongs to this card?</h3>
        <div class="multiple-choice">
          <button 
            v-for="(option, index) in options" 
            :key="index"
            @click="checkAnswer(option)"
            class="choice-button"
            :class="{ 'selected': selectedOption === option }"
          >
            {{ option }}
          </button>
        </div>
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
  background: #10B981;
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

.title-section {
  text-align: center;
  padding: 1.5rem;
  background: var(--surface-50);
  border-radius: 8px;
  width: 100%;
}

.card-icon {
  font-size: 2.5rem;
  color: var(--theme-primary);
  margin-bottom: 0.5rem;
}

.card-title {
  font-size: 1.8rem;
  color: var(--theme-primary);
  margin: 0.5rem 0;
}

.labels-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}

.label-chip-small {
  font-size: 0.75rem !important;
  padding: 0.3rem 0.6rem !important;
}

.question-type h3 {
  font-size: 1.3rem;
  color: var(--theme-primary);
  margin: 0;
  text-align: center;
}

.multiple-choice {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
}

.choice-button {
  padding: 1rem 1.5rem;
  font-size: 1rem;
  text-align: left;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.choice-button:hover {
  border-color: var(--theme-primary);
  background: var(--surface-50);
  transform: translateX(5px);
}

.choice-button.selected {
  border-color: var(--theme-primary);
  background: var(--theme-primary);
  color: white;
}
</style>
