<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="floating-input-wrapper">
    <div class="input-container" :class="{ 'has-icon': icon, error: error }">
      <span v-if="icon" class="input-icon">{{ icon }}</span>
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="{ error: error }"
        @input="handleInput"
        @focus="isFocused = true"
        @blur="handleBlur"
      />
      <label
        :for="inputId"
        class="floating-label"
        :class="{ 'floating-label-active': isLabelActive }"
      >
        {{ labelText }}
      </label>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed, ref } from 'vue'

interface Props {
  label: string
  modelValue: string | number
  type?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  icon?: string
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
  error: '',
  icon: '',
  required: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = `floating-input-${Math.random().toString(36).substring(2, 9)}`
const isFocused = ref(false)

const labelText = computed(() => {
  return props.required ? `${props.label} *` : props.label
})

const isLabelActive = computed(() => {
  return isFocused.value || !!props.modelValue || !!String(props.modelValue).trim()
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleBlur = () => {
  isFocused.value = false
}
</script>

<style scoped>
.floating-input-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 1rem;
}

.input-container {
  position: relative;
  width: 100%;
}

.input-container.has-icon {
  padding-left: 2.5rem;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: #6b7280;
  z-index: 1;
}

input {
  width: 100%;
  padding: 1rem 0.75rem;
  padding-top: 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
  background-color: transparent;
}

input:focus {
  border-color: #3b82f6;
}

input.error {
  border-color: #ef4444;
}

input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.floating-label {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: #6b7280;
  pointer-events: none;
  transition: all 0.2s;
  background-color: white;
  padding: 0 0.25rem;
}

.input-container.has-icon .floating-label {
  left: 2.5rem;
}

.floating-label-active {
  top: 0.5rem;
  font-size: 0.75rem;
  color: #3b82f6;
  transform: translateY(0);
}

input:focus + .floating-label {
  color: #3b82f6;
}

input.error + .floating-label {
  color: #ef4444;
}

.error-message {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #ef4444;
}
</style>
