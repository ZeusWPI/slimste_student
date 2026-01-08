<script setup lang="ts">
import type { Card } from '../../../config/types'

defineProps<{
  card: Card
  userAnswer?: string | string[]
  correctAnswer?: string | string[]
}>()
</script>

<template>
  <div class="answer-comparison">
    <div class="your-answer-box">
      <strong>Your answer:</strong>
      <div class="answer-text">
        <span v-if="userAnswer">
          <span v-if="Array.isArray(userAnswer)">{{ userAnswer.join(', ') }}</span>
          <span v-else>{{ userAnswer }}</span>
        </span>
        <span v-else class="no-answer-given">No answer given</span>
      </div>
    </div>
    <div class="correct-answer-box">
      <strong>Correct answer:</strong>
      <div class="answer-text">
        <template v-if="Array.isArray(correctAnswer)">
          <template v-for="(keyword, idx) in correctAnswer" :key="idx">
            <span 
              :class="{ 
                'missing-keyword': !(userAnswer && Array.isArray(userAnswer) && userAnswer.some(k => k.toLowerCase() === keyword.toLowerCase()))
              }"
            >{{ keyword }}</span><span v-if="idx < correctAnswer.length - 1">, </span>
          </template>
        </template>
        <span v-else>{{ correctAnswer }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.answer-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

.your-answer-box,
.correct-answer-box {
  padding: 1rem;
  border-radius: 6px;
  border: 2px solid;
}

.your-answer-box {
  background: #FEF2F2;
  border-color: #FCA5A5;
}

.your-answer-box strong {
  color: #991B1B;
  display: block;
  margin-bottom: 0.5rem;
}

.correct-answer-box {
  background: #ECFDF5;
  border-color: #6EE7B7;
}

.correct-answer-box strong {
  color: #047857;
  display: block;
  margin-bottom: 0.5rem;
}

.answer-text {
  font-size: 1rem;
  line-height: 1.5;
  color: #1F2937;
}

.no-answer-given {
  font-style: italic;
  color: #9CA3AF;
}

.missing-keyword {
  background: #FECACA !important;
  padding: 0.1rem 0.2rem;
  border-radius: 2px;
  font-weight: 600;
}
</style>
