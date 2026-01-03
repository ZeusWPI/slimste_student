<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import Dialog from 'primevue/dialog'
import LabelSelector from '../components/LabelSelector.vue'
import type { Label } from '../config/types'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface QuizResult {
  id: number
  labels: Label[]
  total_questions: number
  correct_answers: number
  wrong_answers: number
  time_remaining: number
  is_untimed: boolean
  completed_at: string
}

const router = useRouter()
const quizResults = ref<QuizResult[]>([])
const availableLabels = ref<Label[]>([])
const selectedLabelFilters = ref<Label[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalCount = ref(0)
const totalPages = ref(0)
const showGraph = ref(false)
const allQuizResults = ref<QuizResult[]>([])
const loadingGraph = ref(false)

const fetchLabels = async () => {
  try {
    const response = await fetch('/api/labels/', {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      // Handle paginated or non-paginated response
      availableLabels.value = Array.isArray(data) ? data : data.results || []
    }
  } catch (error) {
    console.error('Error fetching labels:', error)
  }
}

const fetchQuizResults = async (page: number = 1) => {
  loading.value = true
  try {
    const response = await fetch(`/api/quiz-results/?page=${page}`, {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      quizResults.value = data.results || []
      totalCount.value = data.count || 0
      totalPages.value = Math.ceil(totalCount.value / 10) // Backend page size is 10
    }
  } catch (error) {
    console.error('Error fetching quiz results:', error)
  } finally {
    loading.value = false
  }
}

const filteredQuizResults = computed(() => {
  if (selectedLabelFilters.value.length === 0) {
    return quizResults.value
  }
  return quizResults.value.filter(result =>
    selectedLabelFilters.value.some(filter =>
      result.labels.some(label => label.id === filter.id)
    )
  )
})

const filteredAllQuizResults = computed(() => {
  if (selectedLabelFilters.value.length === 0) {
    return allQuizResults.value
  }
  return allQuizResults.value.filter(result =>
    selectedLabelFilters.value.some(filter =>
      result.labels.some(label => label.id === filter.id)
    )
  )
})

const chartData = computed(() => {
  const data = filteredAllQuizResults.value
    .sort((a, b) => new Date(a.completed_at).getTime() - new Date(b.completed_at).getTime())
  
  return {
    labels: data.map((result, index) => `Quiz ${index + 1}`),
    datasets: [
      {
        label: 'Score (%)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3B82F6',
        data: data.map(result => getScorePercentage(result)),
        tension: 0.3,
        fill: true
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const
    },
    title: {
      display: true,
      text: 'Quiz Score Progress'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: function(value: any) {
          return value + '%'
        }
      }
    }
  }
}

const fetchAllQuizResults = async () => {
  loadingGraph.value = true
  try {
    const response = await fetch('/api/quiz-results/?all=true', {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      allQuizResults.value = Array.isArray(data) ? data : data.results || []
    }
  } catch (error) {
    console.error('Error fetching all quiz results:', error)
  } finally {
    loadingGraph.value = false
  }
}

const openGraph = async () => {
  if (allQuizResults.value.length === 0) {
    await fetchAllQuizResults()
  }
  showGraph.value = true
}

const deleteQuizResult = async (resultId: number) => {
  if (!confirm('Are you sure you want to delete this quiz result?')) {
    return
  }
  
  try {
    const response = await fetch(`/api/quiz-results/${resultId}/`, {
      method: 'DELETE',
      credentials: 'include'
    })
    
    if (response.ok) {
      // Refresh the current page
      await fetchQuizResults(currentPage.value)
      // Clear cached all results so it will be refetched if graph is opened
      allQuizResults.value = []
    } else {
      alert('Failed to delete quiz result')
    }
  } catch (error) {
    console.error('Error deleting quiz result:', error)
    alert('Error deleting quiz result')
  }
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchQuizResults(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchQuizResults(currentPage.value)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchQuizResults(currentPage.value)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getScorePercentage = (result: QuizResult) => {
  if (result.total_questions === 0) return 0
  return Math.round((result.correct_answers / result.total_questions) * 100)
}

const getScoreColor = (percentage: number) => {
  if (percentage >= 80) return '#10B981'
  if (percentage >= 60) return '#F59E0B'
  return '#EF4444'
}

onMounted(() => {
  fetchLabels()
  fetchQuizResults()
})

// Reset to page 1 when filters change
watch(selectedLabelFilters, () => {
  currentPage.value = 1
})

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="quiz-history-page">
    <div class="header">
      <Button label="Back to Home" icon="pi pi-arrow-left" @click="goBack" text />
      <h1>Quiz History</h1>
    </div>

    <div v-if="!loading && quizResults.length > 0" class="filter-section">
      <LabelSelector 
        v-model="selectedLabelFilters" 
        :options="availableLabels"
        placeholder="Filter by labels"
      />
      <Button 
        label="View Progress Graph" 
        icon="pi pi-chart-line" 
        @click="openGraph"
        severity="secondary"
        class="graph-button"
      />
    </div>

    <div v-if="loading" class="loading">Loading quiz history...</div>

    <div v-else-if="quizResults.length === 0" class="no-results">
      <i class="pi pi-inbox" style="font-size: 3rem; color: #9ca3af;"></i>
      <p>No quiz results yet. Take your first quiz!</p>
      <Button label="Start Quiz" icon="pi pi-play" @click="router.push('/quiz')" />
    </div>

    <div v-else-if="filteredQuizResults.length === 0" class="no-results">
      <i class="pi pi-filter" style="font-size: 3rem; color: #9ca3af;"></i>
      <p>No quiz results found with selected labels.</p>
    </div>

    <div v-else class="results-list">
      <Card v-for="result in filteredQuizResults" :key="result.id" class="result-item">
        <template #title>
          <div class="result-header">
            <div class="result-date">
              <i class="pi pi-calendar"></i>
              {{ formatDate(result.completed_at) }}
            </div>
            <div class="header-actions">
              <div class="result-score" :style="{ color: getScoreColor(getScorePercentage(result)) }">
                <i class="pi pi-chart-bar"></i>
                {{ getScorePercentage(result) }}%
              </div>
              <Button 
                icon="pi pi-trash" 
                @click="deleteQuizResult(result.id)"
                severity="danger"
                text
                rounded
                size="small"
                class="delete-btn"
              />
            </div>
          </div>
        </template>
        <template #content>
          <div class="result-content">
            <div v-if="result.labels.length > 0" class="result-labels">
              <span class="label-title">Topics:</span>
              <div class="labels-chips">
                <Chip 
                  v-for="label in result.labels" 
                  :key="label.id" 
                  :label="label.name" 
                  :style="{ backgroundColor: label.color, color: '#fff' }"
                  class="label-chip"
                />
              </div>
            </div>

            <div class="result-stats">
              <div class="stat-item">
                <i class="pi pi-check-circle" style="color: #10B981;"></i>
                <span class="stat-label">Correct:</span>
                <span class="stat-value">{{ result.correct_answers }}</span>
              </div>
              <div class="stat-item">
                <i class="pi pi-times-circle" style="color: #EF4444;"></i>
                <span class="stat-label">Wrong:</span>
                <span class="stat-value">{{ result.wrong_answers }}</span>
              </div>
              <div class="stat-item">
                <i class="pi pi-list"></i>
                <span class="stat-label">Total:</span>
                <span class="stat-value">{{ result.total_questions }}</span>
              </div>
              <div v-if="!result.is_untimed" class="stat-item">
                <i class="pi pi-clock" style="color: #3B82F6;"></i>
                <span class="stat-label">Time Left:</span>
                <span class="stat-value">{{ result.time_remaining }}s</span>
              </div>
              <div v-else class="stat-item">
                <i class="pi pi-infinity"></i>
                <span class="stat-label">Mode:</span>
                <span class="stat-value">Untimed</span>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <div v-if="totalPages > 1 && selectedLabelFilters.length === 0" class="pagination">
        <Button 
          icon="pi pi-chevron-left" 
          @click="prevPage" 
          :disabled="currentPage === 1"
          outlined
          rounded
        />
        <div class="page-numbers">
          <Button
            v-for="page in totalPages"
            :key="page"
            :label="String(page)"
            @click="goToPage(page)"
            :outlined="currentPage !== page"
            :class="{ 'active-page': currentPage === page }"
            rounded
          />
        </div>
        <Button 
          icon="pi pi-chevron-right" 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
          outlined
          rounded
        />
      </div>
    </div>

    <Dialog 
      v-model:visible="showGraph" 
      modal 
      header="Quiz Score Progress" 
      :style="{ width: '80vw', maxWidth: '900px' }"
      :dismissableMask="true"
    >
      <div v-if="loadingGraph" class="graph-loading">
        Loading graph data...
      </div>
      <div v-else-if="filteredAllQuizResults.length === 0" class="graph-no-data">
        <i class="pi pi-chart-line" style="font-size: 3rem; color: #9ca3af;"></i>
        <p>No quiz data to display</p>
      </div>
      <div v-else class="graph-container">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </Dialog>
  </div>
</template>

<style scoped>
.quiz-history-page {
  width: 100%;
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

h1 {
  color: var(--theme-primary);
  margin: 0;
  flex: 1;
}

.filter-section {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.graph-button {
  width: 100%;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: var(--text-color-secondary);
}

.no-results {
  text-align: center;
  padding: 4rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.no-results p {
  font-size: 1.1rem;
  color: #6b7280;
  margin: 0;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  width: 100%;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.result-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.95rem;
  font-weight: normal;
}

.result-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: bold;
}

.delete-btn {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.delete-btn:hover {
  opacity: 1;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-labels {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label-title {
  font-weight: 600;
  color: #4b5563;
  font-size: 0.9rem;
}

.labels-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.label-chip {
  font-size: 0.8rem !important;
  padding: 0.25rem 0.75rem !important;
  height: auto !important;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--surface-50);
  border-radius: 8px;
}

.stat-item i {
  font-size: 1.1rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
}

.stat-value {
  font-weight: 600;
  margin-left: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.active-page {
  font-weight: bold;
}

.graph-container {
  min-height: 400px;
  padding: 1rem 0;
}

.graph-loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.graph-no-data {
  text-align: center;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.graph-no-data p {
  color: #6b7280;
  margin: 0;
}
</style>
