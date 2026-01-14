<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import LabelSelector from '../components/LabelSelector.vue'
import type { Label, Card as CardData } from '../config/types'

const router = useRouter()

const availableLabels = ref<Label[]>([])
const selectedLabels = ref<Label[]>([])
const includeUnlabeled = ref(false)
const showLabelsInFlashcards = ref(true)
const cards = ref<CardData[]>([])
const currentCardIndex = ref(0)
const isFlipped = ref(false)
const flashcardsStarted = ref(false)

const currentCard = computed(() => cards.value[currentCardIndex.value])
const progress = computed(() => {
  if (cards.value.length === 0) return 0
  return ((currentCardIndex.value + 1) / cards.value.length) * 100
})

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

const startFlashcards = async () => {
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
      const fetchedCards = await response.json()
      
      if (fetchedCards.length === 0) {
        alert('No cards found for selected labels')
        return
      }
      
      cards.value = [...fetchedCards]
      cards.value.sort(() => Math.random() - 0.5)
      currentCardIndex.value = 0
      isFlipped.value = false
      flashcardsStarted.value = true
    } else {
      alert('Failed to load cards')
    }
  } catch (error) {
    console.error('Error fetching cards:', error)
    alert('Error loading flashcards')
  }
}

const flipCard = () => {
  isFlipped.value = !isFlipped.value
}

const nextCard = () => {
  // If flipped, flip back first, then change card after animation
  if (isFlipped.value) {
    isFlipped.value = false
    setTimeout(() => {
      if (currentCardIndex.value < cards.value.length - 1) {
        currentCardIndex.value++
      } else {
        // Restart from beginning
        currentCardIndex.value = 0
      }
    }, 300) // Faster transition when navigating
  } else {
    if (currentCardIndex.value < cards.value.length - 1) {
      currentCardIndex.value++
    } else {
      // Restart from beginning
      currentCardIndex.value = 0
    }
  }
}

const previousCard = () => {
  // If flipped, flip back first, then change card after animation
  if (isFlipped.value) {
    isFlipped.value = false
    setTimeout(() => {
      if (currentCardIndex.value > 0) {
        currentCardIndex.value--
      } else {
        // Wrap to last card
        currentCardIndex.value = cards.value.length - 1
      }
    }, 300) // Faster transition when navigating
  } else {
    if (currentCardIndex.value > 0) {
      currentCardIndex.value--
    } else {
      // Wrap to last card
      currentCardIndex.value = cards.value.length - 1
    }
  }
}

const endFlashcards = () => {
  flashcardsStarted.value = false
  cards.value = []
  currentCardIndex.value = 0
  isFlipped.value = false
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="quiz-container">
    <div v-if="!flashcardsStarted" class="setup-container">
      <Card class="setup-card">
        <template #title>
          <div class="title-container">
            <Button 
              icon="pi pi-arrow-left" 
              text 
              @click="goBack"
              class="back-button"
            />
            <h2>Flashcards</h2>
          </div>
        </template>
        <template #content>
          <div class="setup-content">
            <div class="section">
              <h3>Select Labels</h3>
              <LabelSelector
                v-model="selectedLabels"
                :options="availableLabels"
                placeholder="Select labels for flashcards"
              />
              <div class="checkbox-field">
                <label>
                  <input type="checkbox" v-model="includeUnlabeled" />
                  Include cards without labels
                </label>
              </div>
            </div>

            <div class="section">
              <div class="checkbox-field">
                <label>
                  <input type="checkbox" v-model="showLabelsInFlashcards" />
                  Show labels during flashcards
                </label>
              </div>
            </div>

            <Button 
              label="Start Flashcards" 
              icon="pi pi-play" 
              @click="startFlashcards"
              class="start-button"
            />
          </div>
        </template>
      </Card>
    </div>

    <div v-else class="flashcard-view">
      <div class="flashcard-header">
        <Button 
          icon="pi pi-times" 
          text 
          severity="secondary"
          @click="endFlashcards"
          class="end-button"
        />
        <div class="progress-container">
          <span class="progress-text">
            Card {{ currentCardIndex + 1 }} of {{ cards.length }}
          </span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="flashcard-content">
        <div 
          class="flashcard-wrapper"
          :class="{ 'flipped': isFlipped }"
          @click="flipCard"
        >
          <div class="flashcard">
            <div class="flashcard-front">
              <div class="flashcard-top-bar">
                <div class="flashcard-icon-corner">
                  <i v-if="currentCard?.icon" :class="currentCard.icon"></i>
                  <i v-else class="pi pi-file"></i>
                </div>
                <div v-if="showLabelsInFlashcards && currentCard?.labels.length" class="flashcard-labels-corner">
                  <Chip 
                    v-for="label in currentCard.labels" 
                    :key="label.id"
                    :label="label.name"
                    :style="{ 
                      backgroundColor: label.color, 
                      color: '#ffffff',
                      fontWeight: 'bold'
                    }"
                    class="label-chip-small"
                  />
                </div>
              </div>
              <h1 class="card-title">{{ currentCard?.title }}</h1>
              <div class="flip-icon">
                <i class="pi pi-refresh"></i>
              </div>
            </div>
            <div class="flashcard-back">
              <div class="flashcard-top-bar">
                <div class="flashcard-icon-corner">
                  <i v-if="currentCard?.icon" :class="currentCard.icon"></i>
                  <i v-else class="pi pi-file"></i>
                </div>
                <div v-if="showLabelsInFlashcards && currentCard?.labels.length" class="flashcard-labels-corner">
                  <Chip 
                    v-for="label in currentCard.labels" 
                    :key="label.id"
                    :label="label.name"
                    :style="{ 
                      backgroundColor: label.color, 
                      color: '#ffffff',
                      fontWeight: 'bold'
                    }"
                    class="label-chip-small"
                  />
                </div>
              </div>
              <h2 class="quick-facts-title">Quick Facts</h2>
              <ul class="quick-facts-list">
                <li v-for="(fact, index) in currentCard?.quick_facts" :key="index">
                  {{ fact }}
                </li>
              </ul>
              <div class="flip-icon">
                <i class="pi pi-refresh"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flashcard-controls">
        <Button 
          icon="pi pi-chevron-left"
          @click="previousCard"
          outlined
          class="nav-button"
        />
        <Button 
          :label="currentCardIndex === cards.length - 1 ? 'Restart' : 'Next Card'"
          icon="pi pi-chevron-right"
          iconPos="right"
          @click="nextCard"
          class="next-button"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.quiz-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.setup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.setup-card {
  width: 100%;
  max-width: 600px;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-button {
  padding: 0.5rem;
}

.setup-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section h3 {
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.checkbox-field {
  margin-top: 1rem;
}

.checkbox-field label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.start-button {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
}

.flashcard-view {
  display: flex;
  flex-direction: column;
  min-height: 80vh;
}

.flashcard-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.end-button {
  padding: 0.5rem;
}

.progress-container {
  flex: 1;
}

.progress-text {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.progress-bar {
  height: 8px;
  background: var(--surface-200);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.flashcard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  perspective: 1000px;
}

.flashcard-wrapper {
  width: 100%;
  max-width: 600px;
  height: 400px;
  cursor: pointer;
  position: relative;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flashcard-wrapper.flipped {
  transform: rotateY(180deg);
}

.flashcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flashcard-front,
.flashcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: var(--surface-card);
  border: 3px solid var(--surface-border);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 1px 8px rgba(0, 0, 0, 0.2);
}

.flashcard-front {
  background: linear-gradient(135deg, #ff7f00 0%, #a05305ff 100%);
  color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 1px 8px rgba(0, 0, 0, 0.3);
}

.flashcard-back {
  transform: rotateY(180deg);
  background: linear-gradient(135deg, #ff7f00 0%, #a05305ff 100%);
  color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 1px 8px rgba(0, 0, 0, 0.2);
}

.flashcard-top-bar {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  right: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  z-index: 1;
}

.flashcard-icon-corner {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.flashcard-labels-corner {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  justify-content: flex-end;
  max-width: 60%;
}

.label-chip-small {
  font-size: 0.75rem !important;
  padding: 0.25rem 0.5rem !important;
}

.card-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  word-break: break-word;
}

.quick-facts-title {
  font-size: 1.8rem;
  color: var(--primary-color);
  margin-bottom: 1.5rem;
}

.quick-facts-list {
  text-align: left;
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.quick-facts-list li {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border-left: 4px solid white;
  border-radius: 6px;
  font-size: 1.1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  color: white;
}

.flip-hint {
  margin-top: 2rem;
  font-size: 0.9rem;
  opacity: 0.7;
  font-style: italic;
}

.flip-icon {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 1.5rem;
  opacity: 0.6;
  transition: opacity 0.3s, transform 0.3s;
}

.labels-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.flashcard-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.nav-button {
  padding: 0.75rem 1.5rem;
}

.next-button {
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .quiz-container {
    padding: 1rem;
  }

  .flashcard-wrapper {
    height: 350px;
  }

  .card-title {
    font-size: 2rem;
  }

  .card-icon {
    font-size: 3rem;
  }

  .quick-facts-title {
    font-size: 1.5rem;
  }

  .quick-facts-list li {
    font-size: 1rem;
  }
}
</style>
