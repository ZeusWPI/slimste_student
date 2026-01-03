import {type IconOption } from '../config/icons'

export interface Label {
  id: number
  name: string
  color: string
  owner_username?: string
  shared_with_usernames?: string[]
  is_owner?: boolean
  card_count?: number
}

export interface Card {
  id: number
  title: string
  icon: string
  quick_facts: string[]
  keywords: string[]
  labels: Label[]
  owner_username?: string
  is_owner?: boolean
}

export interface Props {
  initialTitle?: string
  initialIcon?: IconOption
  initialLabels?: Label[]
  initialQuickFacts?: string[]
  initialKeywords?: string[]
  submitLabel?: string
  loading?: boolean
}