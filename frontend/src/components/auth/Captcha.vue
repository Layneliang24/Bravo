<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="captcha-container" :aria-busy="loading">
    <div v-if="loading" class="loading" aria-label="加载中">
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="error" role="alert">
      <span>{{ error }}</span>
      <button type="button" @click="handleRetry" :disabled="disabled">
        重试
      </button>
    </div>
    <div v-else class="captcha-content">
      <div class="captcha-image-wrapper">
        <img
          v-if="captchaImage"
          :src="captchaImage"
          alt="验证码"
          class="captcha-image"
        />
        <div v-else class="captcha-placeholder">验证码加载中...</div>
      </div>
      <div class="captcha-input-wrapper">
        <input
          v-model="captchaAnswer"
          type="text"
          placeholder="请输入验证码"
          :disabled="disabled"
          class="captcha-input"
          @input="handleInput"
        />
        <button
          type="button"
          @click="refreshCaptcha"
          :disabled="disabled || loading"
          class="refresh-button"
          aria-label="刷新验证码"
        >
          🔄
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { ref, onMounted, defineExpose } from 'vue'

interface Props {
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  'captcha-update': [
    data: {
      captcha_id: string
      captcha_answer: string
    },
  ]
}>()

const loading = ref(false)
const error = ref<string | null>(null)
const captchaId = ref('')
const captchaImage = ref('')
const captchaAnswer = ref('')

// API基础URL（可以根据环境配置调整）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 防抖定时器
let refreshTimer: ReturnType<typeof setTimeout> | null = null

const loadCaptcha = async (isRefresh = false) => {
  // 防止重复加载
  if (loading.value) {
    return
  }

  loading.value = true
  error.value = null

  try {
    const url = isRefresh
      ? `${API_BASE_URL}/api/auth/captcha/refresh/`
      : `${API_BASE_URL}/api/auth/captcha/`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      throw new Error(
        `获取验证码失败: ${response.status}${errorText ? ` - ${errorText}` : ''}`
      )
    }

    const data = await response.json()

    // 验证响应数据
    if (!data.captcha_id || !data.captcha_image) {
      throw new Error('验证码数据格式错误')
    }

    captchaId.value = data.captcha_id
    captchaImage.value = data.captcha_image

    // 重置答案
    captchaAnswer.value = ''

    // 发出事件
    emit('captcha-update', {
      captcha_id: captchaId.value,
      captcha_answer: captchaAnswer.value,
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '获取验证码失败'
    console.error('Captcha load error:', err)
  } finally {
    loading.value = false
  }
}

const refreshCaptcha = () => {
  // 如果正在加载，直接返回
  if (loading.value) {
    return
  }

  // 防抖处理：避免频繁刷新（仅在非测试环境下启用）
  if (import.meta.env.MODE !== 'test') {
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    refreshTimer = setTimeout(() => {
      loadCaptcha(true)
      refreshTimer = null
    }, 300) // 300ms防抖延迟
  } else {
    // 测试环境下立即执行
    loadCaptcha(true)
  }
}

const handleInput = () => {
  emit('captcha-update', {
    captcha_id: captchaId.value,
    captcha_answer: captchaAnswer.value,
  })
}

const handleRetry = () => {
  loadCaptcha(false)
}

// 组件挂载时加载验证码
onMounted(() => {
  loadCaptcha()
})

// 暴露方法供父组件调用
defineExpose({
  refreshCaptcha,
})
</script>

<style scoped>
.captcha-container {
  width: 100%;
  margin-bottom: 1rem;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  color: #ff6b6b;
  font-size: 14px;
  background: rgba(255, 100, 100, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.4);
  border-radius: 7px;
  font-family: 'Montserrat', sans-serif;
}

.error span {
  color: #ff6b6b;
  font-weight: 400;
}

.error button {
  padding: 0.5rem 1rem;
  background-color: #ff6b6b;
  color: rgb(255, 255, 255);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 400;
  transition: all 0.3s ease;
}

.error button:hover:not(:disabled) {
  background-color: #ff5252;
  transform: translateY(-1px);
}

.error button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.captcha-content {
  display: flex;
  flex-direction: row;
  gap: 12px;
  align-items: center;
}

/* 验证码显示框 - 160px × 64px */
.captcha-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--captcha-display-width);
  height: var(--captcha-display-height);
  border: 2px solid var(--border-captcha);
  border-radius: var(--input-border-radius);
  background: var(--bg-captcha);
  overflow: hidden;
  flex-shrink: 0;
}

.captcha-image {
  width: auto;
  height: 100%;
  max-width: 100%;
  display: block;
  object-fit: contain;
}

.captcha-placeholder {
  padding: 1rem;
  color: var(--text-secondary);
  font-size: var(--font-size-label);
  font-family: var(--font-family);
  text-align: center;
}

/* 验证码输入框 - 402.406px × 64px */
.captcha-input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
}

.captcha-input {
  width: var(--captcha-input-width);
  height: var(--captcha-input-height);
  padding: 0 20px;
  border: 2px solid var(--border-input);
  border-radius: var(--input-border-radius);
  background: var(--bg-input);
  color: var(--text-primary);
  font-family: var(--font-family);
  font-size: var(--font-size-captcha-input);
  font-weight: bold;
  letter-spacing: 2px;
  text-align: center;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-inset-input);
}

.captcha-input::placeholder {
  color: var(--text-placeholder);
  font-size: var(--font-size-subtitle);
  letter-spacing: 0;
  font-weight: 400;
}

.captcha-input:focus {
  border-color: var(--color-primary-orange);
  box-shadow: var(--shadow-inset-input),
    0 0 0 2px rgba(249, 115, 22, 0.1);
}

.captcha-input:focus-visible {
  outline: 2px solid var(--color-primary-orange);
  outline-offset: 2px;
}

.captcha-input:disabled {
  background: rgba(255, 255, 255, 0.4);
  cursor: not-allowed;
  opacity: 0.6;
}

.refresh-button {
  width: 24px;
  height: 24px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.refresh-button:hover:not(:disabled) {
  color: var(--color-primary-orange);
  background: rgba(249, 115, 22, 0.1);
}

.refresh-button:active:not(:disabled) {
  transform: scale(0.9);
}

.refresh-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}
</style>
