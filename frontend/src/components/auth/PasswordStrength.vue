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
}

.password-strength.hidden {
  display: none;
}

.strength-indicator {
  width: 100%;
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.strength-bar {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 2px;
}

.strength-bar.weak {
  background-color: #ef4444; /* 红色 */
}

.strength-bar.medium {
  background-color: #f59e0b; /* 橙色/黄色 */
}

.strength-bar.strong {
  background-color: #10b981; /* 绿色 */
}

.strength-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.strength-text {
  font-weight: 500;
  color: #374151;
}

.strength-hint {
  color: #6b7280;
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
