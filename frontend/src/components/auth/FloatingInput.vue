<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="floating-input-wrapper">
    <div class="input-container" :class="{ 'has-icon': icon, error: error }">
      <span v-if="icon" class="input-icon" aria-hidden="true">{{ icon }}</span>
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="{ error: error }"
        :aria-label="label"
        :aria-describedby="error ? errorId : undefined"
        :aria-invalid="!!error"
        :aria-required="required"
        @input="handleInput"
        @focus="handleFocus"
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
    <div
      v-if="error"
      :id="errorId"
      class="error-message"
      role="alert"
      aria-live="polite"
    >
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed, ref } from 'vue'

type InputType =
  | 'text'
  | 'password'
  | 'email'
  | 'number'
  | 'tel'
  | 'url'
  | 'search'

interface Props {
  label: string
  modelValue: string | number
  type?: InputType
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
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

// 使用稳定的ID生成方式（如果Vue 3.3+支持useId，否则使用固定前缀+随机数）
const baseId = `floating-input-${Date.now().toString(36)}`
const inputId = computed(() => `${baseId}-input`)
const errorId = computed(() => `${baseId}-error`)

const isFocused = ref(false)

const labelText = computed(() => {
  return props.required ? `${props.label} *` : props.label
})

const isLabelActive = computed(() => {
  return (
    isFocused.value ||
    !!props.modelValue ||
    !!String(props.modelValue).trim()
  )
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
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
  border: 1px solid var(--input-border);
  border-radius: var(--border-radius);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s ease;
  background-color: var(--input-background);
  color: var(--input-text);
}

input:focus {
  border-color: var(--input-border-focus);
  outline: 2px solid transparent;
  outline-offset: 2px;
}

input:focus-visible {
  outline: 2px solid var(--input-border-focus);
  outline-offset: 2px;
}

input.error {
  border-color: var(--color-error);
}

input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.floating-label {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: var(--text-secondary);
  pointer-events: none;
  transition: all 0.2s ease;
  background-color: var(--input-background);
  padding: 0 0.25rem;
}

.input-container.has-icon .floating-label {
  left: 2.5rem;
}

.floating-label-active {
  top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-primary-dark-blue);
  transform: translateY(0);
}

input:focus + .floating-label {
  color: var(--color-primary-dark-blue);
}

input.error + .floating-label {
  color: var(--color-error);
}

.error-message {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-error);
  line-height: 1.25rem;
}
</style>
