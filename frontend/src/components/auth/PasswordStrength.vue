<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div
    v-if="show"
    class="password-strength"
    :class="{ hidden: !show }"
  >
    <div class="strength-indicator">
      <div
        class="strength-bar"
        :class="strengthClass"
        :style="{ width: strengthWidth }"
      ></div>
    </div>
    <div class="strength-info">
      <span class="strength-text">{{ strengthText }}</span>
      <span v-if="strengthHint" class="strength-hint">{{ strengthHint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed } from 'vue'

interface Props {
  password: string
  show?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  password: '',
  show: true,
})

type StrengthLevel = 'weak' | 'medium' | 'strong'

// 缓存正则表达式以提高性能
const LETTER_REGEX = /[a-zA-Z]/
const DIGIT_REGEX = /\d/
const SPECIAL_CHAR_REGEX = /[!@#$%^&*(),.?":{}|<>]/

/**
 * 计算密码强度
 * @param password - 密码字符串
 * @returns 强度等级：weak | medium | strong
 */
const calculateStrength = (password: string): StrengthLevel => {
  if (!password || password.length === 0) {
    return 'weak'
  }

  const length = password.length

  // 长度检查
  if (length < 8) {
    return 'weak'
  }

  // 检查字符类型（使用缓存的正则表达式）
  const hasLetter = LETTER_REGEX.test(password)
  const hasDigit = DIGIT_REGEX.test(password)
  const hasSpecialChar = SPECIAL_CHAR_REGEX.test(password)

  // 只有数字或只有字母 -> 弱
  if ((hasLetter && !hasDigit) || (!hasLetter && hasDigit)) {
    return 'weak'
  }

  // 包含字母和数字
  if (hasLetter && hasDigit) {
    // 长度刚好8位 -> 中等
    if (length === 8) {
      return 'medium'
    }
    // 长度超过8位或包含特殊字符 -> 强
    if (length > 8 || hasSpecialChar) {
      return 'strong'
    }
    return 'medium'
  }

  return 'weak'
}

const strength = computed<StrengthLevel>(() => {
  return calculateStrength(props.password)
})

const strengthClass = computed(() => {
  return {
    weak: strength.value === 'weak',
    medium: strength.value === 'medium',
    strong: strength.value === 'strong',
  }
})

const strengthWidth = computed(() => {
  switch (strength.value) {
    case 'weak':
      return '33%'
    case 'medium':
      return '66%'
    case 'strong':
      return '100%'
    default:
      return '0%'
  }
})

const strengthText = computed(() => {
  switch (strength.value) {
    case 'weak':
      return '弱'
    case 'medium':
      return '中'
    case 'strong':
      return '强'
    default:
      return '弱'
  }
})

const strengthHint = computed(() => {
  const password = props.password

  if (!password || password.length === 0) {
    return '请输入密码'
  }

  const length = password.length

  if (length < 8) {
    return '密码长度至少为8位'
  }

  // 使用缓存的正则表达式
  const hasLetter = LETTER_REGEX.test(password)
  const hasDigit = DIGIT_REGEX.test(password)

  if (!hasLetter || !hasDigit) {
    return '密码必须包含字母和数字'
  }

  if (length === 8) {
    return '建议使用更长的密码以提高安全性'
  }

  if (strength.value === 'strong') {
    return '密码强度良好'
  }

  return ''
})
</script>

<style scoped>
.password-strength {
  width: 100%;
  margin-top: 0.5rem;
  min-height: 40px;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.password-strength.hidden {
  display: none;
}

.strength-indicator {
  width: 100%;
  height: 4px;
  min-height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
  display: block;
  position: relative;
}

.strength-bar {
  height: 100%;
  min-height: 4px;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 2px;
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.strength-bar.weak {
  background-color: var(--color-error);
}

.strength-bar.medium {
  background-color: #f59e0b;
}

.strength-bar.strong {
  background-color: var(--color-success);
}

.strength-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.strength-text {
  font-weight: 500;
  color: var(--text-primary);
}

.strength-hint {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

/* 响应式设计优化 */
@media (max-width: 640px) {
  .strength-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .strength-hint {
    font-size: 0.7rem;
  }
}
</style>
