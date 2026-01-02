<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import LabelSelector from '../components/LabelSelector.vue'
import QuestionHandler from '../components/quiz_question_types/QuestionHandler.vue'
import { selectRandomQuestionType, type QuestionType } from '../components/quiz_question_types/questionTypesConfig'
import type { Label, Card as CardData } from '../config/types'

const router = useRouter()

const availableLabels = ref<Label[]>([])
const selectedLabels = ref<Label[]>([])
const includeUnlabeled = ref(false)
const showLabelsInQuiz = ref(true)
const isUntimed = ref(false)
const cards = ref<CardData[]>([])
const currentCardIndex = ref(0)
const timeRemaining = ref(60)
const showAnswer = ref(false)
const quizStarted = ref(false)
const quizEnded = ref(false)
const correctAnswers = ref(0)
const wrongAnswers = ref(0)
const finalTime = ref(0)
let timerInterval: number | null = null

const currentQuestionType = ref<QuestionType>('title')

const currentCard = computed(() => cards.value[currentCardIndex.value])
const progress = computed(() => {
  if (cards.value.length === 0) return 0
  return ((currentCardIndex.value + 1) / cards.value.length) * 100
})

const generateQuestion = () => {
  if (!currentCard.value) return
  
  showAnswer.value = false
  
  // Use the helper function from QuestionHandler to select a random question type
  currentQuestionType.value = selectRandomQuestionType(currentCard.value)
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

const startQuiz = async () => {
  if (selectedLabels.value.length === 0 && !includeUnlabeled.value) {
    alert('Please select at least one label or include unlabeled cards')
    return
  }

  try {
    let url = '/api/cards/?'
    if (selectedLabels.value.length > 0) {
      const labelIds = selectedLabels.value.map(l => l.id).join(',')
      url += `labels=${labelIds}`
    }
    if (includeUnlabeled.value) {
      url += `${selectedLabels.value.length > 0 ? '&' : ''}include_unlabeled=true`
    }
    
    const response = await fetch(url)
    if (response.ok) {
      cards.value = await response.json()
      
      console.log(`Loaded ${cards.value.length} cards for quiz`)
      
      if (cards.value.length === 0) {
        alert('No cards found for selected labels')
        return
      }
      
      // Shuffle cards
      cards.value.sort(() => Math.random() - 0.5)
      
      quizStarted.value = true
      timeRemaining.value = 60
      currentCardIndex.value = 0
      showAnswer.value = false
      correctAnswers.value = 0
      wrongAnswers.value = 0
      quizEnded.value = false
      finalTime.value = 0
      
      generateQuestion()
      
      if (!isUntimed.value) {
        startTimer()
      }
    } else {
      alert('Failed to load cards')
    }
  } catch (error) {
    console.error('Error fetching cards:', error)
    alert('Error loading quiz cards')
  }
}

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  
  timerInterval = window.setInterval(() => {
    timeRemaining.value--
    if (timeRemaining.value <= 0) {
      endQuiz()
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const endQuiz = () => {
  stopTimer()
  finalTime.value = timeRemaining.value
  quizEnded.value = true
  quizStarted.value = false
}

const handleCorrect = () => {
  correctAnswers.value++
  if (!isUntimed.value) {
    timeRemaining.value += 10
  }
  showAnswer.value = false
  
  if (currentCardIndex.value < cards.value.length - 1) {
    currentCardIndex.value++
    generateQuestion()
  } else {
    endQuiz()
  }
}

const handleWrong = () => {
  showAnswer.value = true
}

const continueAfterWrong = () => {
  wrongAnswers.value++
  showAnswer.value = false
  
  if (currentCardIndex.value < cards.value.length - 1) {
    currentCardIndex.value++
    generateQuestion()
  } else {
    endQuiz()
  }
}

const restartQuiz = () => {
  quizEnded.value = false
  showAnswer.value = false
  selectedLabels.value = []
  includeUnlabeled.value = false
  showLabelsInQuiz.value = true
  isUntimed.value = false
  cards.value = []
  currentCardIndex.value = 0
  timeRemaining.value = 60
  correctAnswers.value = 0
  wrongAnswers.value = 0
  finalTime.value = 0
}

const goBack = () => {
  stopTimer()
  router.push('/')
}

watch(() => quizStarted.value, (newVal) => {
  if (!newVal) {
    stopTimer()
  }
})
</script>

<template>
  <div class="quiz-page">
    <div class="header">
      <Button label="Back to Home" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Quiz Mode</h1>
    </div>

    <!-- Label Selection -->
    <div v-if="!quizStarted && !quizEnded" class="setup-section">
      <Card>
        <template #title>Select Quiz Topics</template>
        <template #content>
          <LabelSelector 
            v-model="selectedLabels" 
            :options="availableLabels"
            placeholder="Select labels for quiz"
          />
          <div class="checkbox-field">
            <label>
              <input type="checkbox" v-model="includeUnlabeled" />
              Include cards without labels
            </label>
          </div>
          <div class="checkbox-field">
            <label>
              <input type="checkbox" v-model="showLabelsInQuiz" />
              Show labels during quiz
            </label>
          </div>
          <div class="checkbox-field">
            <label>
              <input type="checkbox" v-model="isUntimed" />
              Untimed mode (no timer)
            </label>
          </div>
          <Button 
            label="Start Quiz" 
            icon="pi pi-play" 
            @click="startQuiz" 
            :disabled="selectedLabels.length === 0 && !includeUnlabeled"
            class="start-button"
          />
        </template>
      </Card>
    </div>

    <!-- Quiz Active -->
    <div v-if="quizStarted && currentCard" class="quiz-active">
      <div class="quiz-header">
        <div v-if="!isUntimed" class="timer" :class="{ 'timer-warning': timeRemaining < 20, 'timer-critical': timeRemaining < 10 }">
          <i class="pi pi-clock"></i>
          <span>{{ timeRemaining }}s</span>
        </div>
        <div v-else class="timer">
          <i class="pi pi-list"></i>
          <span>Untimed</span>
        </div>
        <div class="score">
          <Chip :label="`Correct: ${correctAnswers}`" style="background: #10B981; color: white; margin-right: 0.5rem;" />
          <Chip :label="`Wrong: ${wrongAnswers}`" style="background: #EF4444; color: white;" />
        </div>
      </div>

      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>

      <Card class="question-card">
        <template #content>
          <QuestionHandler
            :card="currentCard"
            :all-cards="cards"
            :question-type="currentQuestionType"
            :question-number="currentCardIndex + 1"
            :total-questions="cards.length"
            :show-labels="showLabelsInQuiz"
            :show-answer="showAnswer"
            @correct="handleCorrect"
            @wrong="handleWrong"
            @continue="continueAfterWrong"
          />
        </template>
      </Card>
    </div>

    <!-- Quiz Results -->
    <div v-if="quizEnded" class="results-section">
      <Card>
        <template #title>Quiz Complete!</template>
        <template #content>
          <div class="results-content">
            <div class="result-stat">
              <i class="pi pi-check-circle" style="color: #10B981; font-size: 3rem;"></i>
              <h2>{{ correctAnswers }}</h2>
              <p>Correct Answers</p>
            </div>
            <div class="result-stat">
              <i class="pi pi-times-circle" style="color: #EF4444; font-size: 3rem;"></i>
              <h2>{{ wrongAnswers }}</h2>
              <p>Wrong Answers</p>
            </div>
            <div class="result-stat">
              <i class="pi pi-clock" style="color: #3B82F6; font-size: 3rem;"></i>
              <h2>{{ cards.length }}</h2>
              <p>Total Questions</p>
            </div>
            <div v-if="finalTime > 0" class="result-stat">
              <i class="pi pi-stopwatch" style="color: #8B5CF6; font-size: 3rem;"></i>
              <h2>{{ finalTime }}s</h2>
              <p>Time Remaining</p>
            </div>
          </div>
          <div class="result-actions">
            <Button label="Try Again" icon="pi pi-refresh" @click="restartQuiz" />
            <Button label="Back to Home" icon="pi pi-home" @click="goBack" severity="secondary" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.quiz-page {
  width: 100%;
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
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

.setup-section {
  margin-top: 2rem;
}

.checkbox-field {
  margin-top: 1rem;
  padding: 0.5rem 0;
}

.checkbox-field label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.checkbox-field input[type="checkbox"] {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}

.start-button {
  margin-top: 1rem;
  width: 100%;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
}

.timer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: #3B82F6;
}

.timer-warning {
  color: #F59E0B;
}

.timer-critical {
  color: #EF4444;
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.score {
  display: flex;
  gap: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--theme-primary);
  transition: width 0.3s ease;
}

.question-card {
  margin-bottom: 2rem;
}

.results-section {
  margin-top: 2rem;
}

.results-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.result-stat {
  text-align: center;
}

.result-stat h2 {
  font-size: 2.5rem;
  margin: 0.5rem 0;
  color: var(--theme-primary);
}

.result-stat p {
  color: var(--text-color-secondary);
  margin: 0;
}

.result-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style>
