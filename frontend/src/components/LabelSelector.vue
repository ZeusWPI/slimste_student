<script setup lang="ts">
import MultiSelect from 'primevue/multiselect'
import Chip from 'primevue/chip'
import type { Label } from '../config/types'

interface Props {
  modelValue: Label[]
  options: Label[]
  placeholder?: string
}

defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: Label[]]
}>()

const updateValue = (value: Label[]) => {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="label-selector">
    <MultiSelect 
      :model-value="modelValue"
      @update:model-value="updateValue"
      :options="options" 
      optionLabel="name" 
      :placeholder="placeholder || 'Select labels'"
      style="width: 100%"
      display="chip"
    >
      <template #option="slotProps">
        <Chip 
          :label="slotProps.option.name" 
          :style="{ 
            backgroundColor: slotProps.option.color, 
            color: '#fff',
            fontSize: '0.75rem',
            padding: '0.25rem 0.5rem',
            height: 'auto'
          }" 
        />
      </template>
      <template #chip="slotProps">
        <Chip 
          :label="slotProps.value.name" 
          :style="{ 
            backgroundColor: slotProps.value.color, 
            color: '#fff',
            fontSize: '0.75rem',
            padding: '0.25rem 0.5rem',
            height: 'auto'
          }" 
        />
      </template>
    </MultiSelect>
  </div>
</template>

<style scoped>
.label-selector :deep(.p-multiselect-label) {
  padding: 0.5rem;
}

.label-selector :deep(.p-chip) {
  font-size: 0.75rem !important;
  padding: 0.25rem 0.5rem !important;
  height: auto !important;
}
</style>
