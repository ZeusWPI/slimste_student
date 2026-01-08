import { defineAsyncComponent } from 'vue'
import type { Card } from '../../config/types'

// Question type configuration - ADD NEW QUESTION TYPES HERE
export const questionTypes = {
  title: {
    component: defineAsyncComponent(() => import('./TitleQuestion.vue')),
    wrongAnswerComponent: defineAsyncComponent(() => import('./wrong_answer_displays/TitleWrongAnswer.vue')),
    name: 'Title Question',
    requiresAllCards: false,
    isAvailable: () => true, // Always available
  },
  keyword: {
    component: defineAsyncComponent(() => import('./KeywordQuestion.vue')),
    wrongAnswerComponent: defineAsyncComponent(() => import('./wrong_answer_displays/KeywordWrongAnswer.vue')),
    name: 'Keyword Question',
    requiresAllCards: true,
    isAvailable: (card: Card) => card.keywords && card.keywords.length > 0,
  },
  quick_fact: {
    component: defineAsyncComponent(() => import('./QuickFactQuestion.vue')),
    wrongAnswerComponent: defineAsyncComponent(() => import('./wrong_answer_displays/QuickFactWrongAnswer.vue')),
    name: 'Quick Fact Question',
    requiresAllCards: true,
    isAvailable: (card: Card) => card.quick_facts && card.quick_facts.length > 0,
  },
  list_keywords: {
    component: defineAsyncComponent(() => import('./ListKeywordsQuestion.vue')),
    wrongAnswerComponent: defineAsyncComponent(() => import('./wrong_answer_displays/ListKeywordsWrongAnswer.vue')),
    name: 'List Keywords Question',
    requiresAllCards: false,
    isAvailable: (card: Card) => card.keywords && card.keywords.length > 0,
  },
} as const

export type QuestionType = keyof typeof questionTypes

// Helper function to get available question types for a card
export const getAvailableQuestionTypes = (card: Card): QuestionType[] => {
  return (Object.keys(questionTypes) as QuestionType[]).filter(
    type => questionTypes[type].isAvailable(card)
  )
}

// Helper function to select a random question type for a card
export const selectRandomQuestionType = (card: Card): QuestionType => {
  const available = getAvailableQuestionTypes(card)
  return available[Math.floor(Math.random() * available.length)]!
}
