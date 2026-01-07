<script setup lang="ts">
import { computed } from 'vue'
import type { Card } from '../../config/types'
import AnswerReveal from './AnswerReveal.vue'
import { questionTypes, type QuestionType } from './questionTypesConfig'

const props = defineProps<{
  card: Card
  allCards: Card[]
  questionType: QuestionType
  questionNumber: number
  totalQuestions: number
  showLabels: boolean
  showAnswer: boolean
  userAnswer?: string | string[]
}>()

const emit = defineEmits<{
  correct: []
  wrong: [answer?: string | string[]]
  continue: []
}>()

const currentQuestionConfig = computed(() => questionTypes[props.questionType])
const CurrentQuestionComponent = computed(() => currentQuestionConfig.value.component)

const handleWrong = (answer?: string | string[]) => {
  emit('wrong', answer)
}
</script>

<template>
  <div class="question-handler">
    <component
      v-if="!showAnswer"
      :is="CurrentQuestionComponent"
      :card="card"
      :all-cards="currentQuestionConfig.requiresAllCards ? allCards : undefined"
      :question-number="questionNumber"
      :total-questions="totalQuestions"
      :show-labels="showLabels"
      @correct="emit('correct')"
      @wrong="handleWrong"
    />
    
    <AnswerReveal
      v-else
      :card="card"
      :user-answer="userAnswer"
      @continue="emit('continue')"
    />
  </div>
</template>

<style scoped>
.question-handler {
  width: 100%;
}
</style>
