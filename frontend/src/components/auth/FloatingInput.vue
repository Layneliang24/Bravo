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
/* Figma设计规范 - 输入框样式 */
.floating-input-wrapper {
  position: relative;
  width: 100%;
}

.input-container {
  position: relative;
  width: 100%;
}

.input-container.has-icon {
  padding-left: 48px;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  pointer-events: none;
}

input {
  width: 100%;
  height: var(--input-height);
  padding: 0 16px 0 48px;
  border: 2px solid var(--border-input);
  border-radius: var(--input-border-radius);
  font-family: var(--font-family);
  font-size: var(--font-size-subtitle);
  font-weight: 400;
  outline: none;
  transition: all 0.3s ease;
  background-color: var(--bg-input);
  color: var(--text-primary);
  box-shadow: var(--shadow-inset-input);
}

input::placeholder {
  color: var(--text-placeholder);
  font-size: var(--font-size-subtitle);
}

input:focus {
  border-color: var(--color-primary-orange);
  box-shadow: var(--shadow-inset-input),
    0 0 0 2px rgba(249, 115, 22, 0.1);
}

input:focus-visible {
  outline: 2px solid var(--color-primary-orange);
  outline-offset: 2px;
}

input.error {
  border-color: var(--color-error);
}

input:disabled {
  background-color: rgba(255, 255, 255, 0.4);
  cursor: not-allowed;
  opacity: 0.6;
}

.floating-label {
  position: absolute;
  left: 48px;
  top: 50%;
  transform: translateY(-50%) scale(1);
  font-family: var(--font-family);
  font-size: var(--font-size-subtitle);
  color: var(--text-placeholder);
  pointer-events: none;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    font-size 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    color 0.2s ease,
    top 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: var(--bg-input);
  padding: 0 4px;
  z-index: 1;
}

.input-container:not(.has-icon) .floating-label {
  left: 16px;
}

.floating-label-active {
  top: 0;
  font-size: 12px;
  color: var(--text-label);
  transform: translateY(-50%) scale(0.9);
  background-color: var(--bg-input);
}

input:focus + .floating-label {
  color: var(--color-primary-orange);
}

input:focus + .floating-label:not(.floating-label-active) {
  color: var(--color-primary-orange);
}

input.error + .floating-label {
  color: var(--color-error);
}

.error-message {
  margin-top: 4px;
  font-size: 14px;
  color: var(--color-error);
  line-height: 1.25rem;
  font-family: var(--font-family);
  font-weight: 400;
}
</style>
