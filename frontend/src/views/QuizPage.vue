<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import LabelSelector from '../components/LabelSelector.vue'
import QuestionHandler from '../components/quiz_question_types/QuestionHandler.vue'
import WrongAnswerDisplay from '../components/quiz_question_types/WrongAnswerDisplay.vue'
import { selectRandomQuestionType, type QuestionType, questionTypes, getAvailableQuestionTypes } from '../components/quiz_question_types/questionTypesConfig'
import type { Label, Card as CardData } from '../config/types'

const router = useRouter()

const availableLabels = ref<Label[]>([])
const selectedLabels = ref<Label[]>([])
const includeUnlabeled = ref(false)
const showLabelsInQuiz = ref(true)
const isUntimed = ref(false)
const quizMode = ref<'one-per-card' | 'specific-amount'>('one-per-card')
const questionCount = ref(10)
const selectedQuestionTypes = ref<QuestionType[]>(Object.keys(questionTypes) as QuestionType[])
const allQuestionTypes = Object.keys(questionTypes) as QuestionType[]
const cards = ref<CardData[]>([])
const allCards = ref<CardData[]>([])
const usedCardIndices = ref<number[]>([])
const currentCardIndex = ref(0)
const totalQuestions = ref(0)
const currentQuestionNumber = ref(0)
const timeRemaining = ref(60)
const showAnswer = ref(false)
const quizStarted = ref(false)
const quizEnded = ref(false)
const correctAnswers = ref(0)
const wrongAnswers = ref(0)
const finalTime = ref(0)
let timerInterval: number | null = null
const userAnswer = ref<string | string[] | undefined>(undefined)

const currentQuestionType = ref<QuestionType>('title')

// Track wrong answers for summary
interface WrongAnswer {
  card: CardData
  questionType: QuestionType
  userAnswer?: string | string[]
  correctAnswer?: string | string[]
}
const wrongAnswersList = ref<WrongAnswer[]>([])

const currentCard = computed(() => cards.value[currentCardIndex.value])
const progress = computed(() => {
  if (quizMode.value === 'specific-amount') {
    if (totalQuestions.value === 0) return 0
    return (currentQuestionNumber.value / totalQuestions.value) * 100
  } else {
    if (cards.value.length === 0) return 0
    return ((currentCardIndex.value + 1) / cards.value.length) * 100
  }
})

const getNextRandomCard = () => {
  if (allCards.value.length === 0) return null
  
  // If we've used all cards, reset the used indices
  if (usedCardIndices.value.length >= allCards.value.length) {
    usedCardIndices.value = []
  }
  
  // Get available card indices
  const availableIndices = allCards.value
    .map((_, index) => index)
    .filter(index => !usedCardIndices.value.includes(index))
  
  // Pick a random available card
  const randomIndex = availableIndices[Math.floor(Math.random() * availableIndices.length)]
  
  if (randomIndex === undefined) return null
  
  usedCardIndices.value.push(randomIndex)
  
  return allCards.value[randomIndex]
}

const generateQuestion = () => {
  if (!currentCard.value) return
  
  showAnswer.value = false
  userAnswer.value = undefined
  
  // Get available question types for this card filtered by user selection
  const availableTypes = getAvailableQuestionTypes(currentCard.value)
    .filter(type => selectedQuestionTypes.value.includes(type))
  
  // Select a random question type from the available ones
  if (availableTypes.length > 0) {
    currentQuestionType.value = availableTypes[Math.floor(Math.random() * availableTypes.length)]!
  } else {
    // This shouldn't happen if validation is working, but fallback to first available
    const allAvailable = getAvailableQuestionTypes(currentCard.value)
    currentQuestionType.value = allAvailable[0] || 'title'
  }
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
  
  if (selectedQuestionTypes.value.length === 0) {
    alert('Please select at least one question type')
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
      const fetchedCards = await response.json()
      
      console.log(`Loaded ${fetchedCards.length} cards for quiz`)
      
      if (fetchedCards.length === 0) {
        alert('No cards found for selected labels')
        return
      }
      
      // Reset state
      correctAnswers.value = 0
      wrongAnswers.value = 0
      wrongAnswersList.value = []
      quizEnded.value = false
      finalTime.value = 0
      showAnswer.value = false
      usedCardIndices.value = []
      
      if (quizMode.value === 'one-per-card') {
        // Original mode: one question per card
        cards.value = [...fetchedCards]
        cards.value.sort(() => Math.random() - 0.5)
        currentCardIndex.value = 0
        totalQuestions.value = cards.value.length
        currentQuestionNumber.value = 1
      } else {
        // Specific amount mode
        allCards.value = [...fetchedCards]
        totalQuestions.value = questionCount.value
        currentQuestionNumber.value = 1
        
        // Generate first random card
        const firstCard = getNextRandomCard()
        if (firstCard) {
          cards.value = [firstCard]
          currentCardIndex.value = 0
        }
      }
      
      quizStarted.value = true
      timeRemaining.value = 60
      
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

const endQuiz = async () => {
  stopTimer()
  finalTime.value = timeRemaining.value
  quizEnded.value = true
  quizStarted.value = false
  
  // Save quiz result
  try {
    await fetch('/api/quiz-results/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        label_ids: selectedLabels.value.map(l => l.id),
        total_questions: totalQuestions.value,
        correct_answers: correctAnswers.value,
        wrong_answers: wrongAnswers.value,
        time_remaining: finalTime.value,
        is_untimed: isUntimed.value
      }),
    })
  } catch (error) {
    console.error('Error saving quiz result:', error)
  }
}

const handleCorrect = () => {
  correctAnswers.value++
  if (!isUntimed.value) {
    timeRemaining.value += 10
  }
  showAnswer.value = false
  
  if (quizMode.value === 'specific-amount') {
    currentQuestionNumber.value++
    
    if (currentQuestionNumber.value > totalQuestions.value) {
      endQuiz()
    } else {
      // Get next random card
      const nextCard = getNextRandomCard()
      if (nextCard) {
        cards.value = [nextCard]
        currentCardIndex.value = 0
        generateQuestion()
      } else {
        endQuiz()
      }
    }
  } else {
    // One per card mode
    if (currentCardIndex.value < cards.value.length - 1) {
      currentCardIndex.value++
      currentQuestionNumber.value++
      generateQuestion()
    } else {
      endQuiz()
    }
  }
}

const handleWrong = (answer?: string | string[], correctAnswer?: string | string[]) => {
  userAnswer.value = answer
  showAnswer.value = true
  
  // Record the wrong answer
  if (currentCard.value) {
    wrongAnswersList.value.push({
      card: currentCard.value,
      questionType: currentQuestionType.value,
      userAnswer: answer,
      correctAnswer: correctAnswer
    })
  }
}

const continueAfterWrong = () => {
  wrongAnswers.value++
  showAnswer.value = false
  
  if (quizMode.value === 'specific-amount') {
    currentQuestionNumber.value++
    
    if (currentQuestionNumber.value > totalQuestions.value) {
      endQuiz()
    } else {
      // Get next random card
      const nextCard = getNextRandomCard()
      if (nextCard) {
        cards.value = [nextCard]
        currentCardIndex.value = 0
        generateQuestion()
      } else {
        endQuiz()
      }
    }
  } else {
    // One per card mode
    if (currentCardIndex.value < cards.value.length - 1) {
      currentCardIndex.value++
      currentQuestionNumber.value++
      generateQuestion()
    } else {
      endQuiz()
    }
  }
}

const restartQuiz = () => {
  quizEnded.value = false
  showAnswer.value = false
  selectedLabels.value = []
  includeUnlabeled.value = false
  showLabelsInQuiz.value = true
  isUntimed.value = false
  quizMode.value = 'one-per-card'
  questionCount.value = 10
  selectedQuestionTypes.value = Object.keys(questionTypes) as QuestionType[]
  cards.value = []
  allCards.value = []
  usedCardIndices.value = []
  currentCardIndex.value = 0
  totalQuestions.value = 0
  currentQuestionNumber.value = 0
  timeRemaining.value = 60
  correctAnswers.value = 0
  wrongAnswers.value = 0
  wrongAnswersList.value = []
  finalTime.value = 0
}

const redoQuizWithSameSettings = () => {
  // Reset quiz state but keep all settings
  quizEnded.value = false
  quizStarted.value = false
  showAnswer.value = false
  cards.value = []
  allCards.value = []
  usedCardIndices.value = []
  currentCardIndex.value = 0
  totalQuestions.value = 0
  currentQuestionNumber.value = 0
  timeRemaining.value = 60
  correctAnswers.value = 0
  wrongAnswers.value = 0
  wrongAnswersList.value = []
  finalTime.value = 0
  
  // Start quiz again with existing settings
  startQuiz()
}

const redoQuizWithWrongAnswers = () => {
  if (wrongAnswersList.value.length === 0) return
  
  // Extract cards from wrong answers
  const wrongCards = wrongAnswersList.value.map(wa => wa.card)
  
  // Reset quiz state
  quizEnded.value = false
  showAnswer.value = false
  usedCardIndices.value = []
  correctAnswers.value = 0
  wrongAnswers.value = 0
  wrongAnswersList.value = []
  finalTime.value = 0
  timeRemaining.value = 60
  
  // Set up quiz with wrong answer cards
  cards.value = [...wrongCards]
  cards.value.sort(() => Math.random() - 0.5)
  currentCardIndex.value = 0
  totalQuestions.value = cards.value.length
  currentQuestionNumber.value = 1
  
  quizStarted.value = true
  
  generateQuestion()
  
  if (!isUntimed.value) {
    startTimer()
  }
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
          
          <div class="question-types-section">
            <h3>Question Types (defaults to title question if none are available)</h3>
            <div class="question-types-grid">
              <div v-for="questionType in allQuestionTypes" :key="questionType" class="checkbox-field">
                <label>
                  <input 
                    type="checkbox" 
                    :value="questionType"
                    v-model="selectedQuestionTypes"
                  />
                  {{ questionTypes[questionType].name }}
                </label>
              </div>
            </div>
          </div>
          
          <div class="quiz-mode-section">
            <h3>Quiz Mode</h3>
            <div class="radio-field">
              <label>
                <input type="radio" v-model="quizMode" value="one-per-card" />
                One question per card
              </label>
            </div>
            <div class="radio-field">
              <label>
                <input type="radio" v-model="quizMode" value="specific-amount" />
                Specific number of questions
              </label>
            </div>
            <div v-if="quizMode === 'specific-amount'" class="question-count-field">
              <label for="questionCount">Number of questions:</label>
              <input 
                id="questionCount" 
                type="number" 
                v-model.number="questionCount" 
                min="1" 
                max="100"
                class="question-count-input"
              />
            </div>
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
            :question-number="currentQuestionNumber"
            :total-questions="totalQuestions"
            :show-labels="showLabelsInQuiz"
            :show-answer="showAnswer"
            :user-answer="userAnswer"
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
              <h2>{{ totalQuestions }}</h2>
              <p>Total Questions</p>
            </div>
            <div v-if="finalTime > 0" class="result-stat">
              <i class="pi pi-stopwatch" style="color: #8B5CF6; font-size: 3rem;"></i>
              <h2>{{ finalTime }}s</h2>
              <p>Time Remaining</p>
            </div>
          </div>
          
          <div class="result-actions">
            <Button label="Redo Quiz" icon="pi pi-replay" @click="redoQuizWithSameSettings" />
            <Button 
              v-if="wrongAnswersList.length > 0"
              label="Practice Wrong Answers" 
              icon="pi pi-exclamation-circle" 
              @click="redoQuizWithWrongAnswers" 
              severity="warning" 
            />
            <Button label="New Quiz" icon="pi pi-sliders-h" @click="restartQuiz" severity="secondary" />
            <Button label="Back to Home" icon="pi pi-home" @click="goBack" severity="secondary" />
          </div>
          
          <!-- Wrong Answers Summary -->
          <div v-if="wrongAnswersList.length > 0" class="wrong-answers-summary">
            <h3><i class="pi pi-exclamation-triangle"></i> Questions You Got Wrong</h3>
            <WrongAnswerDisplay
              v-for="(wrongAnswer, index) in wrongAnswersList"
              :key="index"
              :card="wrongAnswer.card"
              :question-type="wrongAnswer.questionType"
              :user-answer="wrongAnswer.userAnswer"
              :correct-answer="wrongAnswer.correctAnswer"
            />
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

.quiz-mode-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
}

.quiz-mode-section h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #4b5563;
}

.radio-field {
  padding: 0.5rem 0;
}

.radio-field label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.radio-field input[type="radio"] {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}

.question-count-field {
  margin-top: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.question-count-field label {
  font-size: 0.95rem;
  color: #4b5563;
}

.question-count-input {
  width: 80px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
}

.question-types-section {
  margin-top: 1.5rem;
}

.question-types-section h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #4b5563;
}

.question-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
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
  position: relative;
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

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #4b5563;
  white-space: nowrap;
  text-shadow: 0 0 2px white;
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

.wrong-answers-summary {
  margin: 2rem 0;
  padding: 1.5rem;
  background: #FEF2F2;
  border: 2px solid #FEE2E2;
  border-radius: 8px;
}

.wrong-answers-summary h3 {
  margin: 0 0 1.5rem 0;
  color: #DC2626;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
