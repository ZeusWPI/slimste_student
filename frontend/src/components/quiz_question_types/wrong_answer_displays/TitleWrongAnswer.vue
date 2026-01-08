<script setup lang="ts">
import type { Card } from '../../../config/types'

const props = defineProps<{
  card: Card
  userAnswer?: string | string[]
  correctAnswer?: string | string[]
}>()

// Helper function to highlight differences between strings using minimum edit distance
const highlightDifferences = (userText: string, correctText: string) => {
  const user = userText.toLowerCase()
  const correct = correctText.toLowerCase()
  
  const m = user.length
  const n = correct.length
  
  // Create DP table for edit distance
  const dp: number[][] = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0))
  
  // Initialize base cases
  for (let i = 0; i <= m; i++) dp[i]![0] = i
  for (let j = 0; j <= n; j++) dp[0]![j] = j
  
  // Fill DP table
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (user[i - 1] === correct[j - 1]) {
        dp[i]![j] = dp[i - 1]![j - 1]!
      } else {
        dp[i]![j] = 1 + Math.min(
          dp[i - 1]![j]!,     // deletion
          dp[i]![j - 1]!,     // insertion
          dp[i - 1]![j - 1]!  // substitution
        )
      }
    }
  }
  
  // Trace back to find the alignment
  let i = m
  let j = n
  const userHighlights: boolean[] = Array(m).fill(false)
  const correctHighlights: boolean[] = Array(n).fill(false)
  
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && user[i - 1] === correct[j - 1]) {
      // Match - move diagonally
      i--
      j--
    } else {
      // Find which operation was used
      const deletionCost = i > 0 ? dp[i - 1]![j]! : Infinity
      const insertionCost = j > 0 ? dp[i]![j - 1]! : Infinity
      const substitutionCost = (i > 0 && j > 0) ? dp[i - 1]![j - 1]! : Infinity
      
      const minCost = Math.min(deletionCost, insertionCost, substitutionCost)
      
      if (j > 0 && insertionCost === minCost) {
        // Insertion - highlight in correct text (needs to be added)
        correctHighlights[j - 1] = true
        j--
      } else if (i > 0 && j > 0 && substitutionCost === minCost) {
        // Substitution - highlight in both
        userHighlights[i - 1] = true
        correctHighlights[j - 1] = true
        i--
        j--
      } else if (i > 0) {
        // Deletion - highlight in user text (needs to be removed)
        userHighlights[i - 1] = true
        i--
      }
    }
  }
  
  // Build result strings with merged highlights
  const buildHighlightedString = (text: string, highlights: boolean[]) => {
    let result = ''
    let inHighlight = false
    let highlightBuffer = ''
    
    for (let idx = 0; idx < text.length; idx++) {
      const char = text[idx]
      
      if (highlights[idx]) {
        if (!inHighlight) {
          inHighlight = true
        }
        highlightBuffer += char
      } else {
        if (inHighlight) {
          result += `<span class="diff-highlight">${highlightBuffer}</span>`
          highlightBuffer = ''
          inHighlight = false
        }
        result += char
      }
    }
    
    // Close any remaining highlight
    if (inHighlight && highlightBuffer) {
      result += `<span class="diff-highlight">${highlightBuffer}</span>`
    }
    
    return result
  }
  
  return {
    userHighlighted: buildHighlightedString(userText, userHighlights),
    correctHighlighted: buildHighlightedString(correctText, correctHighlights)
  }
}
</script>

<template>
  <div class="answer-comparison">
    <div class="your-answer-box">
      <strong>Your answer:</strong>
      <div class="answer-text" v-html="highlightDifferences(userAnswer as string, card.title).userHighlighted"></div>
    </div>
    <div class="correct-answer-box">
      <strong>Correct answer:</strong>
      <div class="answer-text" v-html="highlightDifferences(userAnswer as string, card.title).correctHighlighted"></div>
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

.answer-text :deep(.diff-highlight) {
  background: #FECACA !important;
  padding: 0.1rem 0.2rem;
  border-radius: 2px;
  font-weight: 600;
}
</style>
