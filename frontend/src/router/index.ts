import { createRouter, createWebHistory } from 'vue-router'
import StartPage from '../views/StartPage.vue'
import CardsList from '../views/CardsList.vue'
import CreateCard from '../views/CreateCard.vue'
import EditCard from '../views/EditCard.vue'
import CreateLabel from '../views/CreateLabel.vue'
import LabelsList from '../views/LabelsList.vue'
import ShareLabels from '../views/ShareLabels.vue'
import QuizPage from '../views/QuizPage.vue'
import QuizHistory from '../views/QuizHistory.vue'
import LoginPage from '../views/LoginPage.vue'
import { useAuth } from '../composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'home',
      component: StartPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/cards',
      name: 'cards',
      component: CardsList,
      meta: { requiresAuth: true }
    },
    {
      path: '/cards/create',
      name: 'create-card',
      component: CreateCard,
      meta: { requiresAuth: true }
    },
    {
      path: '/cards/:id/edit',
      name: 'edit-card',
      component: EditCard,
      meta: { requiresAuth: true }
    },
    {
      path: '/labels',
      name: 'labels',
      component: LabelsList,
      meta: { requiresAuth: true }
    },
    {
      path: '/labels/create',
      name: 'create-label',
      component: CreateLabel,
      meta: { requiresAuth: true }
    },
    {
      path: '/labels/share',
      name: 'share-labels',
      component: ShareLabels,
      meta: { requiresAuth: true }
    },
    {
      path: '/quiz',
      name: 'quiz',
      component: QuizPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/quiz/history',
      name: 'quiz-history',
      component: QuizHistory,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, checkAuth } = useAuth()
  
  // Check authentication status on first load
  if (!isAuthenticated.value && to.meta.requiresAuth) {
    await checkAuth()
  }
  
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next({ name: 'login' })
  } else if (to.meta.requiresGuest && isAuthenticated.value) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
