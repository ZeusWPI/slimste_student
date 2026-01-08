<script setup lang="ts">
import { computed } from 'vue'
import Chip from 'primevue/chip'
import type { Card } from '../../config/types'
import { questionTypes, type QuestionType } from './questionTypesConfig'

const props = defineProps<{
  card: Card
  questionType: QuestionType
  userAnswer?: string | string[]
  correctAnswer?: string | string[]
}>()

const wrongAnswerConfig = computed(() => questionTypes[props.questionType])
const WrongAnswerComponent = computed(() => wrongAnswerConfig.value.wrongAnswerComponent)
</script>

<template>
  <div class="wrong-answer-item">
    <div class="wrong-answer-header">
      <div class="wrong-answer-title">
        <span class="question-type-badge">{{ questionTypes[questionType].name }}</span>
        <h4>{{ card.title }}</h4>
      </div>
      <div v-if="card.labels && card.labels.length > 0" class="wrong-answer-labels">
        <Chip v-for="label in card.labels" :key="label.id" :label="label.name" 
              :style="{ backgroundColor: label.color, color: '#fff' }"
              class="label-chip" />
      </div>
    </div>
    <div class="wrong-answer-details">
      <component
        :is="WrongAnswerComponent"
        :card="card"
        :user-answer="userAnswer"
        :correct-answer="correctAnswer"
      />
    </div>
  </div>
</template>

<style scoped>
.wrong-answer-item {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.wrong-answer-item:last-child {
  margin-bottom: 0;
}

.wrong-answer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #E5E7EB;
}

.wrong-answer-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.question-type-badge {
  background: #6366F1;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.wrong-answer-header h4 {
  margin: 0;
  color: #374151;
  font-size: 1.1rem;
}

.wrong-answer-labels {
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

.wrong-answer-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>
